import type {
  Route,
  RouteConfig,
  RoutingRequest,
  RoutingDecision,
  DecisionLogResponse,
  HealthResponse,
} from "@/types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function fetchApi<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}/api/v1${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
    ...options,
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status} ${response.statusText}`);
  }

  return response.json() as Promise<T>;
}

export async function getHealth(): Promise<HealthResponse> {
  return fetchApi<HealthResponse>("/health");
}

export async function listRoutes(): Promise<Route[]> {
  return fetchApi<Route[]>("/routes");
}

export async function registerRoute(config: RouteConfig): Promise<Route> {
  return fetchApi<Route>("/routes", {
    method: "POST",
    body: JSON.stringify(config),
  });
}

export async function deleteRoute(name: string): Promise<void> {
  const response = await fetch(
    `${API_BASE}/api/v1/routes/${encodeURIComponent(name)}`,
    { method: "DELETE" }
  );
  if (!response.ok) {
    throw new Error(`API error: ${response.status} ${response.statusText}`);
  }
}

export async function routeRequest(request: RoutingRequest): Promise<RoutingDecision> {
  return fetchApi<RoutingDecision>("/route", {
    method: "POST",
    body: JSON.stringify(request),
  });
}

export async function getDecisions(
  limit: number = 50,
  offset: number = 0
): Promise<DecisionLogResponse> {
  return fetchApi<DecisionLogResponse>(`/decisions?limit=${limit}&offset=${offset}`);
}
