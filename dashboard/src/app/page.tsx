import { DecisionLog } from "@/components/DecisionLog";
import { ConfidenceChart } from "@/components/ConfidenceChart";
import { RouteRegistry } from "@/components/RouteRegistry";
import { getHealth } from "@/lib/api";

export default async function Home() {
  let health;
  try {
    health = await getHealth();
  } catch {
    health = { status: "unreachable", version: "-", routes_loaded: 0, embedding_service: "-" };
  }

  return (
    <div className="space-y-8">
      <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
        <div className="rounded-lg border border-gray-200 bg-white p-6">
          <h3 className="text-sm font-medium text-gray-500">Status</h3>
          <p className="mt-2 text-2xl font-semibold text-gray-900">
            {health.status}
          </p>
        </div>
        <div className="rounded-lg border border-gray-200 bg-white p-6">
          <h3 className="text-sm font-medium text-gray-500">Routes Loaded</h3>
          <p className="mt-2 text-2xl font-semibold text-gray-900">
            {health.routes_loaded}
          </p>
        </div>
        <div className="rounded-lg border border-gray-200 bg-white p-6">
          <h3 className="text-sm font-medium text-gray-500">Embedding Service</h3>
          <p className="mt-2 text-2xl font-semibold text-gray-900">
            {health.embedding_service}
          </p>
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
