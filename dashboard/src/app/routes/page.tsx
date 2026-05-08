import { RouteRegistry } from "@/components/RouteRegistry";
import { listRoutes } from "@/lib/api";

export default async function RoutesPage() {
  let routes;
  try {
    routes = await listRoutes();
  } catch {
    routes = [];
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Route Management</h1>
      <RouteRegistry initialRoutes={routes} />
    </div>
  );
}
