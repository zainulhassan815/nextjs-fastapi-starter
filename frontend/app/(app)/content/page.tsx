"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useAuthOptions } from "@/lib/api";
import {
  listPostsOptions,
  listPostsQueryKey,
  createPostMutation,
  escalatePostMutation,
  getPostModerationOptions,
} from "@/lib/api/generated/@tanstack/react-query.gen";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

const statusColors: Record<string, string> = {
  safe: "bg-green-100 text-green-800",
  harmful: "bg-red-100 text-red-800",
  pending: "bg-gray-100 text-gray-800",
  uncertain: "bg-yellow-100 text-yellow-800",
  escalated: "bg-blue-100 text-blue-800",
};

const verdictColors: Record<string, string> = {
  safe: "bg-green-100 text-green-800",
  harmful: "bg-red-100 text-red-800",
  uncertain: "bg-yellow-100 text-yellow-800",
  escalated: "bg-blue-100 text-blue-800",
};

function formatTimestamp(iso: string): string {
  const date = new Date(iso);
  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function ModerationDetails({
  postId,
  authOptions,
}: {
  postId: number;
  authOptions: { client: typeof import("@/lib/api/client").apiClient; auth: string | undefined };
}) {
  const moderation = useQuery({
    ...getPostModerationOptions({
      ...authOptions,
      path: { post_id: postId },
    }),
    enabled: !!authOptions.auth,
    refetchInterval: 3_000,
  });

  if (moderation.isLoading) {
    return (
      <div className="mt-3 space-y-2 border-t pt-3">
        <Skeleton className="h-4 w-48" />
        <Skeleton className="h-12 w-full" />
        <Skeleton className="h-12 w-full" />
      </div>
    );
  }

  if (moderation.isError) {
    return (
      <div className="mt-3 border-t pt-3">
        <p className="text-sm text-red-600">
          Failed to load moderation results.
        </p>
      </div>
    );
  }

  const data = moderation.data;

  if (!data || data.results.length === 0) {
    return (
      <div className="mt-3 border-t pt-3">
        <p className="text-muted-foreground text-sm">
          No moderation results yet. Post is still pending review.
        </p>
      </div>
    );
  }

  return (
    <div className="mt-3 space-y-2 border-t pt-3">
      <div className="flex items-center gap-2">
        <span className="text-sm font-medium">Current Status:</span>
        <Badge
          variant="outline"
          className={
            statusColors[data.current_status] ?? "bg-gray-100 text-gray-800"
          }
        >
          {data.current_status}
        </Badge>
      </div>
      <div className="space-y-1">
        <p className="text-muted-foreground text-xs font-medium uppercase tracking-wide">
          Pipeline Stages
        </p>
        <div className="overflow-x-auto rounded-md border">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-muted/50 text-muted-foreground text-left text-xs">
                <th className="px-3 py-2">Stage</th>
                <th className="px-3 py-2">Method</th>
                <th className="px-3 py-2">Verdict</th>
                <th className="px-3 py-2">Confidence</th>
                <th className="px-3 py-2">Reasoning</th>
              </tr>
            </thead>
            <tbody>
              {data.results.map((result) => (
                <tr key={result.id} className="border-t">
                  <td className="px-3 py-2 font-medium">{result.stage}</td>
                  <td className="px-3 py-2">
                    {result.method_name ?? "Unknown"}
                  </td>
                  <td className="px-3 py-2">
                    <Badge
                      variant="outline"
                      className={`text-xs ${verdictColors[result.verdict] ?? "bg-gray-100 text-gray-800"}`}
                    >
                      {result.verdict}
                    </Badge>
                  </td>
                  <td className="px-3 py-2">
                    {(result.confidence * 100).toFixed(1)}%
                  </td>
                  <td className="max-w-xs px-3 py-2 text-xs text-gray-600">
                    {result.reasoning ?? "-"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default function ContentPage() {
  const { options: authOptions, isAuthenticated } = useAuthOptions();
  const queryClient = useQueryClient();

  const [text, setText] = useState("");
  const [language, setLanguage] = useState("auto");
  const [expandedPostId, setExpandedPostId] = useState<number | null>(null);

  const posts = useQuery({
    ...listPostsOptions(authOptions),
    enabled: isAuthenticated,
    refetchInterval: 5_000,
  });

  const createMutation = useMutation({
    ...createPostMutation(authOptions),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: listPostsQueryKey() });
      setText("");
      setLanguage("auto");
      // Auto-expand the new post to show pipeline progress
      if (data) setExpandedPostId(data.id);
      // Refetch again after pipeline has had time to run
      setTimeout(() => {
        queryClient.invalidateQueries({ queryKey: listPostsQueryKey() });
      }, 3_000);
    },
  });

  const escalateMutation = useMutation({
    ...escalatePostMutation(authOptions),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: listPostsQueryKey() });
    },
  });

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!text.trim()) return;
    createMutation.mutate({
      body: {
        content: text,
        language: language === "auto" ? null : language,
      },
    });
  }

  return (
    <div className="mx-auto max-w-4xl space-y-6 p-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Content</h1>
        <p className="text-muted-foreground">
          Submit posts for moderation and view the feed
        </p>
      </div>

      {/* Submit New Post */}
      <Card>
        <CardHeader>
          <CardTitle>Submit New Post</CardTitle>
          <CardDescription>
            Write content to be processed through the moderation pipeline
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="post-content">Content</Label>
              <Textarea
                id="post-content"
                placeholder="Write a post in English, Urdu, or Roman Urdu..."
                value={text}
                onChange={(e) => setText(e.target.value)}
                rows={4}
                className="resize-y"
              />
            </div>
            <div className="flex items-end gap-4">
              <div className="space-y-2">
                <Label>Language</Label>
                <Select value={language} onValueChange={(v) => setLanguage(v ?? "auto")}>
                  <SelectTrigger className="w-48">
                    <SelectValue placeholder="Auto-detect" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="auto">Auto-detect</SelectItem>
                    <SelectItem value="english">English</SelectItem>
                    <SelectItem value="urdu">Urdu</SelectItem>
                    <SelectItem value="roman_urdu">Roman Urdu</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <Button
                type="submit"
                disabled={createMutation.isPending || !text.trim()}
              >
                {createMutation.isPending ? "Submitting..." : "Submit Post"}
              </Button>
            </div>
            {createMutation.isError && (
              <p className="text-sm text-red-600">
                Failed to submit post. Please try again.
              </p>
            )}
          </form>
        </CardContent>
      </Card>

      {/* Posts Feed */}
      <div className="space-y-4">
        <h2 className="text-xl font-semibold">Posts Feed</h2>

        {posts.isLoading ? (
          <div className="space-y-4">
            {Array.from({ length: 3 }).map((_, i) => (
              <Card key={i}>
                <CardContent className="space-y-3 pt-6">
                  <Skeleton className="h-4 w-3/4" />
                  <Skeleton className="h-4 w-1/2" />
                  <div className="flex gap-2">
                    <Skeleton className="h-5 w-16" />
                    <Skeleton className="h-5 w-20" />
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : posts.data && posts.data.length > 0 ? (
          <div className="space-y-4">
            {posts.data.map((post) => (
              <Card key={post.id}>
                <CardContent className="space-y-3 pt-6">
                  <p className="text-sm leading-relaxed">{post.content}</p>
                  <div className="flex flex-wrap items-center gap-2">
                    <Badge
                      variant="outline"
                      className={
                        statusColors[post.status] ??
                        "bg-gray-100 text-gray-800"
                      }
                    >
                      {post.status}
                    </Badge>
                    <Badge variant="secondary">{post.language}</Badge>
                    {post.status !== "escalated" && (
                      <Button
                        variant="outline"
                        size="sm"
                        className="h-6 text-xs"
                        disabled={escalateMutation.isPending}
                        onClick={() =>
                          escalateMutation.mutate({
                            path: { post_id: post.id },
                          })
                        }
                      >
                        {escalateMutation.isPending &&
                        escalateMutation.variables?.path?.post_id === post.id
                          ? "Escalating..."
                          : "Escalate"}
                      </Button>
                    )}
                    <span className="text-muted-foreground ml-auto text-xs">
                      {formatTimestamp(post.created_at)}
                    </span>
                  </div>
                  <div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() =>
                        setExpandedPostId(
                          expandedPostId === post.id ? null : post.id
                        )
                      }
                      className="h-auto px-0 text-xs font-medium"
                    >
                      {expandedPostId === post.id
                        ? "Hide Moderation"
                        : "View Moderation"}
                    </Button>
                    {expandedPostId === post.id && isAuthenticated && (
                      <ModerationDetails
                        postId={post.id}
                        authOptions={authOptions}
                      />
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : (
          <Card>
            <CardContent className="py-12 text-center">
              <p className="text-muted-foreground">
                No posts yet. Submit your first post above.
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
