"use client";

import { useEffect, useState } from "react";
import type { Route } from "@/types";
import { listRoutes } from "@/lib/api";

interface RouteRegistryProps {
  initialRoutes?: Route[];
}

export function RouteRegistry({ initialRoutes }: RouteRegistryProps) {
  const [routes, setRoutes] = useState<Route[]>(initialRoutes ?? []);

  useEffect(() => {
    if (initialRoutes) return;
    listRoutes().then(setRoutes).catch(() => setRoutes([]));
  }, [initialRoutes]);

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-6">
      <h2 className="mb-4 text-lg font-semibold text-gray-900">
        Route Registry
      </h2>
      {routes.length === 0 ? (
        <p className="text-sm text-gray-500">No routes registered.</p>
      ) : (
        <div className="space-y-3">
          {routes.map((route) => (
            <div
              key={route.name}
              className="rounded-md border border-gray-100 p-4"
            >
              <div className="flex items-center justify-between">
                <h3 className="font-medium text-gray-900">{route.name}</h3>
                <span className="rounded-full bg-blue-50 px-2.5 py-0.5 text-xs font-medium text-blue-700">
                  {route.confidence_threshold}
                </span>
              </div>
              <p className="mt-1 text-sm text-gray-600">
                {route.description}
              </p>
              <div className="mt-2 flex flex-wrap gap-1">
                {route.required_permissions.map((perm) => (
                  <span
                    key={perm}
                    className="rounded bg-gray-100 px-2 py-0.5 text-xs text-gray-600"
                  >
                    {perm}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
