"use client";

import { useQuery } from "@tanstack/react-query";
import { useAuthOptions } from "@/lib/api";
import {
  getContentStatsOptions,
  getBudget2Options,
  getDetectionMethodsOptions,
  getBudgetOptions,
} from "@/lib/api/generated/@tanstack/react-query.gen";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";

const STATUS_COLORS: Record<string, string> = {
  safe: "bg-green-100 text-green-800",
  harmful: "bg-red-100 text-red-800",
  pending: "bg-gray-100 text-gray-800",
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

function truncate(text: string, maxLength: number = 120): string {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength) + "...";
}

function StatsCardSkeleton() {
  return (
    <Card>
      <CardHeader className="pb-2">
        <Skeleton className="h-4 w-24" />
      </CardHeader>
      <CardContent>
        <Skeleton className="h-8 w-16" />
        <Skeleton className="mt-2 h-3 w-32" />
      </CardContent>
    </Card>
  );
}

export default function DashboardPage() {
  const { options: authOptions, isAuthenticated } = useAuthOptions();

  const stats = useQuery({
    ...getContentStatsOptions(authOptions),
    enabled: isAuthenticated,
    refetchInterval: 10_000,
  });

  const budget = useQuery({
    ...getBudget2Options(authOptions),
    enabled: isAuthenticated,
    refetchInterval: 10_000,
  });

  const reviewBudget = useQuery({
    ...getBudgetOptions(authOptions),
    enabled: isAuthenticated,
    refetchInterval: 10_000,
  });

  const detectionMethods = useQuery({
    ...getDetectionMethodsOptions(authOptions),
    enabled: isAuthenticated,
    refetchInterval: 10_000,
  });

  const isLoading =
    stats.isLoading ||
    budget.isLoading ||
    reviewBudget.isLoading ||
    detectionMethods.isLoading;

  const avgDecayFactor =
    detectionMethods.data && detectionMethods.data.length > 0
      ? detectionMethods.data.reduce((sum, m) => sum + m.decay_factor, 0) /
        detectionMethods.data.length
      : null;

  return (
    <div className="mx-auto max-w-7xl space-y-6 p-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground">
          Content moderation overview and system health
        </p>
      </div>

      {/* Stats Cards Row */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {isLoading ? (
          <>
            <StatsCardSkeleton />
            <StatsCardSkeleton />
            <StatsCardSkeleton />
            <StatsCardSkeleton />
          </>
        ) : (
          <>
            <Card>
              <CardHeader className="pb-2">
                <CardDescription>Total Posts</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">
                  {stats.data?.total_posts ?? 0}
                </div>
                <p className="text-muted-foreground text-xs">
                  Across all statuses
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardDescription>Budget Used</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">
                  ${budget.data?.spent_this_month_usd?.toFixed(2) ?? "0.00"}
                </div>
                <p className="text-muted-foreground text-xs">
                  of ${budget.data?.monthly_budget_usd?.toFixed(2) ?? "0.00"}{" "}
                  monthly limit
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardDescription>Reviews This Hour</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">
                  {reviewBudget.data?.reviews_this_hour ?? 0}
                  <span className="text-muted-foreground text-lg font-normal">
                    {" "}
                    / {reviewBudget.data?.budget_per_hour ?? 0}
                  </span>
                </div>
                <p className="text-muted-foreground text-xs">
                  {reviewBudget.data?.remaining ?? 0} remaining
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardDescription>Detection Health</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">
                  {avgDecayFactor !== null
                    ? `${(avgDecayFactor * 100).toFixed(0)}%`
                    : "N/A"}
                </div>
                <p className="text-muted-foreground text-xs">
                  Avg decay factor across {detectionMethods.data?.length ?? 0}{" "}
                  methods
                </p>
              </CardContent>
            </Card>
          </>
        )}
      </div>

      {/* Budget Progress Bar */}
      <Card>
        <CardHeader>
          <CardTitle>Budget Utilization</CardTitle>
          <CardDescription>
            Monthly API cost budget consumption
          </CardDescription>
        </CardHeader>
        <CardContent>
          {budget.isLoading ? (
            <div className="space-y-2">
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-3 w-24" />
            </div>
          ) : (
            <div className="space-y-2">
              <Progress
                value={budget.data?.budget_utilization_pct ?? 0}
              />
              <div className="text-muted-foreground flex justify-between text-sm">
                <span>
                  {budget.data?.budget_utilization_pct?.toFixed(1) ?? 0}% used
                </span>
                <span>
                  ${budget.data?.remaining_usd?.toFixed(2) ?? "0.00"} remaining
                </span>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Content by Status + Content by Language */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Content by Status</CardTitle>
            <CardDescription>
              Distribution of posts across moderation statuses
            </CardDescription>
          </CardHeader>
          <CardContent>
            {stats.isLoading ? (
              <div className="flex flex-wrap gap-2">
                <Skeleton className="h-6 w-20" />
                <Skeleton className="h-6 w-20" />
                <Skeleton className="h-6 w-20" />
              </div>
            ) : stats.data?.by_status &&
              Object.keys(stats.data.by_status).length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {Object.entries(stats.data.by_status).map(([status, count]) => (
                  <Badge
                    key={status}
                    variant="outline"
                    className={`text-sm ${STATUS_COLORS[status] ?? "bg-gray-100 text-gray-800"}`}
                  >
                    {status}: {count}
                  </Badge>
                ))}
              </div>
            ) : (
              <p className="text-muted-foreground text-sm">No posts yet</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Content by Language</CardTitle>
            <CardDescription>
              Distribution of posts across detected languages
            </CardDescription>
          </CardHeader>
          <CardContent>
            {stats.isLoading ? (
              <div className="flex flex-wrap gap-2">
                <Skeleton className="h-6 w-20" />
                <Skeleton className="h-6 w-20" />
              </div>
            ) : stats.data?.by_language &&
              Object.keys(stats.data.by_language).length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {Object.entries(stats.data.by_language).map(
                  ([language, count]) => (
                    <Badge key={language} variant="secondary" className="text-sm">
                      {language}: {count}
                    </Badge>
                  )
                )}
              </div>
            ) : (
              <p className="text-muted-foreground text-sm">No posts yet</p>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
          <CardDescription>Last 10 posts submitted for moderation</CardDescription>
        </CardHeader>
        <CardContent>
          {stats.isLoading ? (
            <div className="space-y-3">
              {Array.from({ length: 5 }).map((_, i) => (
                <div key={i} className="flex items-center gap-3">
                  <Skeleton className="h-6 w-16" />
                  <Skeleton className="h-4 w-12" />
                  <Skeleton className="h-4 flex-1" />
                  <Skeleton className="h-4 w-24" />
                </div>
              ))}
            </div>
          ) : stats.data?.recent_posts && stats.data.recent_posts.length > 0 ? (
            <div className="space-y-3">
              {stats.data.recent_posts.slice(0, 10).map((post) => (
                <div
                  key={post.id}
                  className="flex items-start gap-3 rounded-lg border p-3"
                >
                  <Badge
                    variant="outline"
                    className={`shrink-0 ${STATUS_COLORS[post.status] ?? "bg-gray-100 text-gray-800"}`}
                  >
                    {post.status}
                  </Badge>
                  <Badge variant="secondary" className="shrink-0">
                    {post.language}
                  </Badge>
                  <p className="min-w-0 flex-1 text-sm">
                    {truncate(post.content)}
                  </p>
                  <span className="text-muted-foreground shrink-0 text-xs">
                    {formatTimestamp(post.created_at)}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-muted-foreground text-sm">
              No recent posts to display
            </p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
