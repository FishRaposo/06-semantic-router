"use client";

import { useEffect, useState, useCallback } from "react";
import { RouteRegistry } from "@/components/RouteRegistry";
import { listRoutes, registerRoute, deleteRoute } from "@/lib/api";
import type { Route } from "@/types";

export default function RoutesPage() {
  const [routes, setRoutes] = useState<Route[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [toolName, setToolName] = useState("");
  const [confidenceThreshold, setConfidenceThreshold] = useState("0.7");
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const fetchRoutes = useCallback(async () => {
    try {
      const data = await listRoutes();
      setRoutes(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch routes");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchRoutes();
  }, [fetchRoutes]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setSubmitError(null);
    try {
      await registerRoute({
        name,
        description,
        tool_name: toolName,
        confidence_threshold: parseFloat(confidenceThreshold) || 0.7,
        required_permissions: [],
        fallback_route: null,
        metadata: {},
      });
      setName("");
      setDescription("");
      setToolName("");
      setConfidenceThreshold("0.7");
      await fetchRoutes();
    } catch (err) {
      setSubmitError(err instanceof Error ? err.message : "Failed to register route");
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (routeName: string) => {
    if (!confirm(`Delete route "${routeName}"?`)) return;
    try {
      await deleteRoute(routeName);
      await fetchRoutes();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete route");
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Route Management</h1>

      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          {error}
        </div>
      )}

      <div className="rounded-lg border border-gray-200 bg-white p-6">
        <h2 className="mb-4 text-lg font-semibold text-gray-900">Add Route</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-gray-700">
                Name
              </label>
              <input
                id="name"
                type="text"
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                placeholder="weather_lookup"
              />
            </div>
            <div>
              <label htmlFor="toolName" className="block text-sm font-medium text-gray-700">
                Tool Name
              </label>
              <input
                id="toolName"
                type="text"
                required
                value={toolName}
                onChange={(e) => setToolName(e.target.value)}
                className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                placeholder="get_weather"
              />
            </div>
          </div>
          <div>
            <label htmlFor="description" className="block text-sm font-medium text-gray-700">
              Description
            </label>
            <input
              id="description"
              type="text"
              required
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              placeholder="Retrieve current weather conditions for a location"
            />
          </div>
          <div>
            <label htmlFor="threshold" className="block text-sm font-medium text-gray-700">
              Confidence Threshold
            </label>
            <input
              id="threshold"
              type="number"
              required
              min="0"
              max="1"
              step="0.05"
              value={confidenceThreshold}
              onChange={(e) => setConfidenceThreshold(e.target.value)}
              className="mt-1 block w-32 rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </div>
          {submitError && (
            <p className="text-sm text-red-600">{submitError}</p>
          )}
          <button
            type="submit"
            disabled={submitting}
            className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
          >
            {submitting ? "Registering..." : "Register Route"}
          </button>
        </form>
      </div>

      {loading ? (
        <p className="text-sm text-gray-500">Loading routes...</p>
      ) : routes.length === 0 ? (
        <p className="text-sm text-gray-500">No routes registered.</p>
      ) : (
        <div className="space-y-3">
          {routes.map((route) => (
            <div
              key={route.name}
              className="rounded-lg border border-gray-200 bg-white p-4"
            >
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-medium text-gray-900">{route.name}</h3>
                  <p className="mt-1 text-sm text-gray-600">{route.description}</p>
                  <p className="mt-1 text-xs text-gray-400">Tool: {route.tool_name}</p>
                </div>
                <div className="flex items-center gap-3">
                  <span className="rounded-full bg-blue-50 px-2.5 py-0.5 text-xs font-medium text-blue-700">
                    {route.confidence_threshold}
                  </span>
                  <button
                    onClick={() => handleDelete(route.name)}
                    className="rounded-md bg-red-50 px-3 py-1 text-xs font-medium text-red-600 hover:bg-red-100"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
