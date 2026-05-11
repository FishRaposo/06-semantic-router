"use client";

import { useEffect, useState, useCallback } from "react";
import { getDecisions, listRoutes } from "@/lib/api";
import type { DecisionLog, Route } from "@/types";

export default function DecisionsPage() {
  const [decisions, setDecisions] = useState<DecisionLog[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [routes, setRoutes] = useState<Route[]>([]);
  const [filterRoute, setFilterRoute] = useState("");
  const [minConfidence, setMinConfidence] = useState(0);

  const fetchDecisions = useCallback(async () => {
    try {
      setLoading(true);
      const res = await getDecisions(200);
      setDecisions(res.decisions);
      setTotal(res.total);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch decisions");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDecisions();
    listRoutes().then(setRoutes).catch(() => {});
  }, [fetchDecisions]);

  const filtered = decisions.filter((d) => {
    if (filterRoute && d.decision.selected_route !== filterRoute) return false;
    if (d.decision.confidence < minConfidence) return false;
    return true;
  });

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Decision Log</h1>

      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          {error}
        </div>
      )}

      <div className="flex flex-wrap items-end gap-4 rounded-lg border border-gray-200 bg-white p-4">
        <div>
          <label htmlFor="route-filter" className="block text-sm font-medium text-gray-700">
            Route
          </label>
          <select
            id="route-filter"
            value={filterRoute}
            onChange={(e) => setFilterRoute(e.target.value)}
            className="mt-1 block rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          >
            <option value="">All Routes</option>
            {routes.map((r) => (
              <option key={r.name} value={r.name}>
                {r.name}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label htmlFor="min-confidence" className="block text-sm font-medium text-gray-700">
            Min Confidence: {minConfidence.toFixed(2)}
          </label>
          <input
            id="min-confidence"
            type="range"
            min="0"
            max="1"
            step="0.05"
            value={minConfidence}
            onChange={(e) => setMinConfidence(parseFloat(e.target.value))}
            className="mt-1 block w-48"
          />
        </div>
        <button
          onClick={fetchDecisions}
          disabled={loading}
          className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? "Loading..." : "Refresh"}
        </button>
      </div>

      <div className="rounded-lg border border-gray-200 bg-white p-6">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900">
            Decisions ({filtered.length} of {total})
          </h2>
        </div>

        {loading ? (
          <p className="text-sm text-gray-500">Loading decisions...</p>
        ) : filtered.length === 0 ? (
          <p className="text-sm text-gray-500">No decisions match the current filters.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead>
                <tr>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">
                    Query
                  </th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">
                    Route
                  </th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">
                    Confidence
                  </th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">
                    Time (ms)
                  </th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">
                    Fallback
                  </th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">
                    Timestamp
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {filtered.map((log, idx) => (
                  <tr key={idx}>
                    <td className="max-w-[200px] truncate px-3 py-2 text-sm text-gray-900">
                      {log.request.query}
                    </td>
                    <td className="px-3 py-2 text-sm text-gray-900">
                      {log.decision.selected_route ?? "\u2014"}
                    </td>
                    <td className="px-3 py-2 text-sm">
                      <span
                        className={
                          log.decision.confidence >= 0.7
                            ? "text-green-600"
                            : log.decision.confidence >= 0.4
                              ? "text-yellow-600"
                              : "text-red-600"
                        }
                      >
                        {log.decision.confidence.toFixed(3)}
                      </span>
                    </td>
                    <td className="px-3 py-2 text-sm text-gray-600">
                      {log.processing_time_ms}
                    </td>
                    <td className="px-3 py-2 text-sm text-gray-600">
                      {log.decision.fallback_used ? "Yes" : "No"}
                    </td>
                    <td className="whitespace-nowrap px-3 py-2 text-sm text-gray-500">
                      {new Date(log.timestamp).toLocaleTimeString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
