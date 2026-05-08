export interface Route {
  name: string;
  description: string;
  tool_name: string;
  confidence_threshold: number;
  required_permissions: string[];
  fallback_route: string | null;
  metadata: Record<string, string>;
  embedding: number[] | null;
}

export interface RouteConfig {
  name: string;
  description: string;
  tool_name: string;
  confidence_threshold: number;
  required_permissions: string[];
  fallback_route: string | null;
  metadata: Record<string, string>;
}

export interface RoutingRequest {
  query: string;
  context: Record<string, unknown> | null;
  user_id: string | null;
  metadata: Record<string, string>;
}

export interface PolicyCheck {
  allowed: boolean;
  reason: string | null;
  required_action: string | null;
  missing_permissions: string[];
}

export interface ExecutionResult {
  tool_name: string;
  status: string;
  data: Record<string, unknown> | null;
  error: string | null;
}

export interface RoutingDecision {
  selected_route: string | null;
  confidence: number;
  rejected_routes: RejectedRoute[];
  policy_check: PolicyCheck | null;
  fallback_used: boolean;
  clarification: string | null;
  execution_result: ExecutionResult | null;
}

export interface RejectedRoute {
  route_name: string;
  score: number;
}

export interface DecisionLog {
  request: RoutingRequest;
  decision: RoutingDecision;
  timestamp: string;
  processing_time_ms: number;
}

export interface DecisionLogResponse {
  decisions: DecisionLog[];
  total: number;
}

export interface HealthResponse {
  status: string;
  version: string;
  routes_loaded: number;
  embedding_service: string;
}

export interface ConfidenceBucket {
  range: string;
  count: number;
  label: string;
}
