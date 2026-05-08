"use client";

import { useEffect, useState } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import type { DecisionLog, ConfidenceBucket } from "@/types";
import { getDecisions } from "@/lib/api";

function bucketConfidence(decisions: DecisionLog[]): ConfidenceBucket[] {
  const buckets: ConfidenceBucket[] = [
    { range: "0.0-0.3", count: 0, label: "No Match" },
    { range: "0.3-0.5", count: 0, label: "Very Low" },
    { range: "0.5-0.7", count: 0, label: "Low" },
    { range: "0.7-0.85", count: 0, label: "Good" },
    { range: "0.85-1.0", count: 0, label: "High" },
  ];

  for (const d of decisions) {
    const c = d.decision.confidence;
    if (c < 0.3) buckets[0].count++;
    else if (c < 0.5) buckets[1].count++;
    else if (c < 0.7) buckets[2].count++;
    else if (c < 0.85) buckets[3].count++;
    else buckets[4].count++;
  }

  return buckets;
}

export function ConfidenceChart() {
  const [data, setData] = useState<ConfidenceBucket[]>([]);

  useEffect(() => {
    getDecisions(100)
      .then((res) => setData(bucketConfidence(res.decisions)))
      .catch(() => setData([]));
  }, []);

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-6">
      <h2 className="mb-4 text-lg font-semibold text-gray-900">
        Confidence Distribution
      </h2>
      {data.length === 0 || data.every((b) => b.count === 0) ? (
        <p className="text-sm text-gray-500">No decision data available yet.</p>
      ) : (
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="label" tick={{ fontSize: 12 }} />
            <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
            <Tooltip />
            <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
