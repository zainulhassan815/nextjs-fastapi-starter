"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useAuthOptions } from "@/lib/api";
import {
  getReviewQueueOptions,
  getBudgetOptions,
  submitReviewDecisionMutation,
  getReviewQueueQueryKey,
  getBudgetQueryKey,
} from "@/lib/api/generated/@tanstack/react-query.gen";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import { Textarea } from "@/components/ui/textarea";

function formatTimestamp(iso: string): string {
  const date = new Date(iso);
  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function ReviewCardSkeleton() {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <Skeleton className="h-5 w-24" />
          <Skeleton className="h-4 w-32" />
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <Skeleton className="h-16 w-full" />
        <div className="flex gap-2">
          <Skeleton className="h-8 w-24" />
          <Skeleton className="h-8 w-24" />
        </div>
      </CardContent>
    </Card>
  );
}

export default function QueuePage() {
  const { options: authOptions, isAuthenticated } = useAuthOptions();
  const queryClient = useQueryClient();
  const [notes, setNotes] = useState<Record<number, string>>({});
  const [expandedNotes, setExpandedNotes] = useState<Record<number, boolean>>(
    {}
  );

  const queue = useQuery({
    ...getReviewQueueOptions(authOptions),
    enabled: isAuthenticated,
    refetchInterval: 10_000,
  });

  const budget = useQuery({
    ...getBudgetOptions(authOptions),
    enabled: isAuthenticated,
    refetchInterval: 10_000,
  });

  const submitMutation = useMutation({
    ...submitReviewDecisionMutation(authOptions),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: getReviewQueueQueryKey() });
      queryClient.invalidateQueries({ queryKey: getBudgetQueryKey() });
    },
  });

  const budgetUsed = budget.data?.reviews_this_hour ?? 0;
  const budgetTotal = budget.data?.budget_per_hour ?? 20;
  const budgetRemaining = budget.data?.remaining ?? 0;
  const budgetExhausted = budgetRemaining === 0;
  const budgetPercent =
    budgetTotal > 0 ? Math.round((budgetUsed / budgetTotal) * 100) : 0;

  const pendingItems = queue.data ?? [];

  function handleSubmit(postId: number, decision: "approved" | "rejected") {
    const note = notes[postId]?.trim() || null;
    submitMutation.mutate({
      body: { post_id: postId, decision, note },
    });
  }

  return (
    <div className="mx-auto max-w-4xl space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Review Queue</h1>
          <p className="text-muted-foreground">
            Human review for AI-escalated content
          </p>
        </div>
        {budget.isLoading ? (
          <Skeleton className="h-5 w-32" />
        ) : (
          <Badge
            variant={budgetExhausted ? "destructive" : "secondary"}
            className="text-sm"
          >
            {budgetUsed}/{budgetTotal} reviews this hour
          </Badge>
        )}
      </div>

      {/* Budget Progress */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-base">Hourly Review Budget</CardTitle>
          <CardDescription>
            {budgetRemaining} review{budgetRemaining !== 1 ? "s" : ""} remaining
            this hour
          </CardDescription>
        </CardHeader>
        <CardContent>
          {budget.isLoading ? (
            <Skeleton className="h-4 w-full" />
          ) : (
            <div className="space-y-2">
              <Progress value={budgetPercent} />
              <div className="text-muted-foreground flex justify-between text-sm">
                <span>{budgetUsed} used</span>
                <span>{budgetRemaining} remaining</span>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Queue Items */}
      {queue.isLoading ? (
        <div className="space-y-4">
          <ReviewCardSkeleton />
          <ReviewCardSkeleton />
          <ReviewCardSkeleton />
        </div>
      ) : pendingItems.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <p className="text-muted-foreground text-lg">
              No items pending review
            </p>
            <p className="text-muted-foreground mt-1 text-sm">
              All escalated content has been reviewed. Check back later.
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {pendingItems.map((item) => {
            const isSubmitting =
              submitMutation.isPending &&
              submitMutation.variables?.body?.post_id === item.post_id;
            const noteExpanded = expandedNotes[item.post_id] ?? false;

            return (
              <Card key={item.id}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Badge variant="outline">Post #{item.post_id}</Badge>
                      <Badge variant="secondary">{item.status}</Badge>
                    </div>
                    <span className="text-muted-foreground text-sm">
                      {formatTimestamp(item.created_at)}
                    </span>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* AI Reasoning */}
                  <div className="space-y-1">
                    <p className="text-muted-foreground text-xs font-medium uppercase tracking-wide">
                      AI Reasoning
                    </p>
                    <div className="bg-muted rounded-lg p-3 text-sm whitespace-pre-wrap">
                      {item.ai_reasoning}
                    </div>
                  </div>

                  {/* Optional Note */}
                  <div className="space-y-2">
                    {!noteExpanded ? (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() =>
                          setExpandedNotes((prev) => ({
                            ...prev,
                            [item.post_id]: true,
                          }))
                        }
                      >
                        Add a note
                      </Button>
                    ) : (
                      <Textarea
                        placeholder="Optional review note..."
                        value={notes[item.post_id] ?? ""}
                        onChange={(e) =>
                          setNotes((prev) => ({
                            ...prev,
                            [item.post_id]: e.target.value,
                          }))
                        }
                        className="min-h-12"
                      />
                    )}
                  </div>

                  {/* Action Buttons */}
                  <div className="flex items-center gap-2">
                    <Button
                      variant="outline"
                      className="border-green-300 text-green-700 hover:bg-green-50 hover:text-green-800 dark:border-green-700 dark:text-green-400 dark:hover:bg-green-950 dark:hover:text-green-300"
                      disabled={budgetExhausted || isSubmitting}
                      onClick={() => handleSubmit(item.post_id, "approved")}
                    >
                      {isSubmitting &&
                      submitMutation.variables?.body?.decision === "approved"
                        ? "Approving..."
                        : "Approve"}
                    </Button>
                    <Button
                      variant="outline"
                      className="border-red-300 text-red-700 hover:bg-red-50 hover:text-red-800 dark:border-red-700 dark:text-red-400 dark:hover:bg-red-950 dark:hover:text-red-300"
                      disabled={budgetExhausted || isSubmitting}
                      onClick={() => handleSubmit(item.post_id, "rejected")}
                    >
                      {isSubmitting &&
                      submitMutation.variables?.body?.decision === "rejected"
                        ? "Rejecting..."
                        : "Reject"}
                    </Button>
                    {budgetExhausted && (
                      <span className="text-muted-foreground ml-2 text-xs">
                        Hourly budget exhausted
                      </span>
                    )}
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
