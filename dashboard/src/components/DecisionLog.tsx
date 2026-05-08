"use client";

import { useEffect, useState } from "react";
import type { DecisionLog } from "@/types";
import { getDecisions } from "@/lib/api";

export function DecisionLog() {
  const [decisions, setDecisions] = useState<DecisionLog[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getDecisions(20)
      .then((res) => setDecisions(res.decisions))
      .catch(() => setDecisions([]))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-6">
      <h2 className="mb-4 text-lg font-semibold text-gray-900">
        Recent Decisions
      </h2>
      {loading ? (
        <p className="text-sm text-gray-500">Loading decisions...</p>
      ) : decisions.length === 0 ? (
        <p className="text-sm text-gray-500">No decisions recorded yet.</p>
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
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {decisions.map((log, idx) => (
                <tr key={idx}>
                  <td className="max-w-[200px] truncate px-3 py-2 text-sm text-gray-900">
                    {log.request.query}
                  </td>
                  <td className="px-3 py-2 text-sm text-gray-900">
                    {log.decision.selected_route ?? "—"}
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
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
