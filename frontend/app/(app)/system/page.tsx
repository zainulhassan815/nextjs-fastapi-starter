"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useAuthOptions } from "@/lib/api";
import {
  getDetectionMethodsOptions,
  getDetectionMethodsQueryKey,
  getBudget2Options,
  getBudget2QueryKey,
  resetDetectionMethodsMutation,
} from "@/lib/api/generated/@tanstack/react-query.gen";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Progress } from "@/components/ui/progress";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";

function decayColor(decay: number): string {
  if (decay > 0.7) return "text-green-600";
  if (decay >= 0.3) return "text-yellow-600";
  return "text-red-600";
}

function decayIndicatorClass(decay: number): string {
  if (decay > 0.7) return "[&_[data-slot=progress-indicator]]:bg-green-500";
  if (decay >= 0.3) return "[&_[data-slot=progress-indicator]]:bg-yellow-500";
  return "[&_[data-slot=progress-indicator]]:bg-red-500";
}

function TableSkeleton() {
  return (
    <div className="space-y-3">
      {Array.from({ length: 5 }).map((_, i) => (
        <div key={i} className="flex items-center gap-4">
          <Skeleton className="h-4 w-32" />
          <Skeleton className="h-4 w-12" />
          <Skeleton className="h-4 w-16" />
          <Skeleton className="h-4 w-24" />
          <Skeleton className="h-4 flex-1" />
        </div>
      ))}
    </div>
  );
}

function BudgetSkeleton() {
  return (
    <div className="space-y-4">
      <Skeleton className="h-6 w-48" />
      <Skeleton className="h-4 w-full" />
      <Skeleton className="h-4 w-32" />
      <Skeleton className="h-4 w-40" />
      <Skeleton className="h-4 w-36" />
    </div>
  );
}

export default function SystemPage() {
  const { options: authOptions, isAuthenticated } = useAuthOptions();
  const queryClient = useQueryClient();

  const detectionMethods = useQuery({
    ...getDetectionMethodsOptions(authOptions),
    enabled: isAuthenticated,
    refetchInterval: 10_000,
  });

  const budget = useQuery({
    ...getBudget2Options(authOptions),
    enabled: isAuthenticated,
    refetchInterval: 10_000,
  });

  const resetMutation = useMutation({
    ...resetDetectionMethodsMutation(authOptions),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: getDetectionMethodsQueryKey(),
      });
    },
  });

  return (
    <div className="mx-auto max-w-7xl space-y-6 p-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">System Health</h1>
        <p className="text-muted-foreground">
          Detection methods and budget breakdown
        </p>
      </div>

      {/* Detection Methods */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Detection Methods</CardTitle>
              <CardDescription>
                Active detection methods and their current health
              </CardDescription>
            </div>
            <Button
              variant="destructive"
              size="sm"
              disabled={resetMutation.isPending}
              onClick={() => resetMutation.mutate({})}
            >
              {resetMutation.isPending ? "Resetting..." : "Reset All"}
            </Button>
          </div>
          {resetMutation.isSuccess && (
            <p className="text-sm text-green-600">
              {resetMutation.data?.message}
            </p>
          )}
        </CardHeader>
        <CardContent>
          {detectionMethods.isLoading ? (
            <TableSkeleton />
          ) : detectionMethods.data && detectionMethods.data.length > 0 ? (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>Stage</TableHead>
                  <TableHead>Usage Count</TableHead>
                  <TableHead>Decay Factor</TableHead>
                  <TableHead>Description</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {detectionMethods.data.map((method) => (
                  <TableRow key={method.id}>
                    <TableCell className="font-medium">{method.name}</TableCell>
                    <TableCell>
                      <Badge variant="outline">Stage {method.stage}</Badge>
                    </TableCell>
                    <TableCell>{method.usage_count}</TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <Progress
                          value={method.decay_factor * 100}
                          className={`w-20 ${decayIndicatorClass(method.decay_factor)}`}
                        />
                        <span
                          className={`text-sm font-medium ${decayColor(method.decay_factor)}`}
                        >
                          {(method.decay_factor * 100).toFixed(0)}%
                        </span>
                      </div>
                    </TableCell>
                    <TableCell className="text-muted-foreground max-w-xs truncate text-sm">
                      {method.description}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          ) : (
            <p className="text-muted-foreground text-sm">
              No detection methods configured
            </p>
          )}
        </CardContent>
      </Card>

      {/* Budget Breakdown */}
      <Card>
        <CardHeader>
          <CardTitle>Budget Breakdown</CardTitle>
          <CardDescription>
            Monthly API cost budget and usage details
          </CardDescription>
        </CardHeader>
        <CardContent>
          {budget.isLoading ? (
            <BudgetSkeleton />
          ) : budget.data ? (
            <div className="space-y-6">
              {/* Monthly spend headline */}
              <div>
                <div className="mb-2 flex items-baseline gap-1">
                  <span className="text-2xl font-bold">
                    ${budget.data.spent_this_month_usd.toFixed(2)}
                  </span>
                  <span className="text-muted-foreground text-sm">
                    / ${budget.data.monthly_budget_usd.toFixed(2)}
                  </span>
                </div>
                <Progress value={budget.data.budget_utilization_pct} />
                <p className="text-muted-foreground mt-1 text-sm">
                  {budget.data.budget_utilization_pct.toFixed(1)}% of monthly
                  budget used
                </p>
              </div>

              {/* Stats grid */}
              <div className="grid gap-4 sm:grid-cols-3">
                <div className="rounded-lg border p-4">
                  <p className="text-muted-foreground text-sm">
                    Total API Calls
                  </p>
                  <p className="text-2xl font-bold">
                    {budget.data.total_api_calls}
                  </p>
                </div>
                <div className="rounded-lg border p-4">
                  <p className="text-muted-foreground text-sm">
                    Remaining Budget
                  </p>
                  <p className="text-2xl font-bold text-green-600">
                    ${budget.data.remaining_usd.toFixed(2)}
                  </p>
                </div>
                <div className="rounded-lg border p-4">
                  <p className="text-muted-foreground text-sm">
                    Monthly Limit
                  </p>
                  <p className="text-2xl font-bold">
                    ${budget.data.monthly_budget_usd.toFixed(2)}
                  </p>
                </div>
              </div>

              {/* Cost by stage */}
              <div>
                <h3 className="mb-3 text-sm font-semibold">Cost by Stage</h3>
                {budget.data.cost_by_stage &&
                Object.keys(budget.data.cost_by_stage).length > 0 ? (
                  <div className="space-y-2">
                    {Object.entries(budget.data.cost_by_stage).map(
                      ([stage, cost]) => (
                        <div
                          key={stage}
                          className="flex items-center justify-between rounded-lg border px-4 py-2"
                        >
                          <span className="text-sm font-medium">
                            Stage {stage}
                          </span>
                          <span className="text-sm font-mono">
                            ${(cost as number).toFixed(2)}
                          </span>
                        </div>
                      )
                    )}
                  </div>
                ) : (
                  <p className="text-muted-foreground text-sm">
                    No cost data available
                  </p>
                )}
              </div>
            </div>
          ) : (
            <p className="text-muted-foreground text-sm">
              Budget data unavailable
            </p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
