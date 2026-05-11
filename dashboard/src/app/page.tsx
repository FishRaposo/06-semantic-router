"use client";

import { useEffect, useState, useCallback } from "react";
import { ConfidenceChart } from "@/components/ConfidenceChart";
import { DecisionLog } from "@/components/DecisionLog";
import { RouteRegistry } from "@/components/RouteRegistry";
import { getHealth, listRoutes, getDecisions } from "@/lib/api";
import type { HealthResponse } from "@/types";

export default function Home() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [routeCount, setRouteCount] = useState<number | null>(null);
  const [decisionCount, setDecisionCount] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      const [h, routes, decisions] = await Promise.all([
        getHealth(),
        listRoutes(),
        getDecisions(1),
      ]);
      setHealth(h);
      setRouteCount(routes.length);
      setDecisionCount(decisions.total);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch data");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, [fetchData]);

  return (
    <div className="space-y-8">
      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
        <div className="rounded-lg border border-gray-200 bg-white p-6">
          <h3 className="text-sm font-medium text-gray-500">Status</h3>
          {loading ? (
            <div className="mt-2 h-8 w-24 animate-pulse rounded bg-gray-200" />
          ) : (
            <p className="mt-2 text-2xl font-semibold text-gray-900">
              {health?.status ?? "unreachable"}
            </p>
          )}
        </div>
        <div className="rounded-lg border border-gray-200 bg-white p-6">
          <h3 className="text-sm font-medium text-gray-500">Total Routes</h3>
          {loading ? (
            <div className="mt-2 h-8 w-16 animate-pulse rounded bg-gray-200" />
          ) : (
            <p className="mt-2 text-2xl font-semibold text-gray-900">
              {routeCount ?? 0}
            </p>
          )}
        </div>
        <div className="rounded-lg border border-gray-200 bg-white p-6">
          <h3 className="text-sm font-medium text-gray-500">Recent Decisions</h3>
          {loading ? (
            <div className="mt-2 h-8 w-16 animate-pulse rounded bg-gray-200" />
          ) : (
            <p className="mt-2 text-2xl font-semibold text-gray-900">
              {decisionCount ?? 0}
            </p>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <RouteRegistry />
        <ConfidenceChart />
      </div>

      <DecisionLog />
    </div>
  );
}
