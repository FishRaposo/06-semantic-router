import type { Metadata, Viewport } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "SemanticRouter Dashboard",
  description: "Monitor and manage semantic routing decisions",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-gray-50 text-gray-900 antialiased">
        <header className="border-b border-gray-200 bg-white">
          <nav className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
            <a href="/" className="text-xl font-bold text-blue-600">SemanticRouter</a>
            <div className="flex gap-6">
              <a href="/" className="text-sm font-medium text-gray-600 hover:text-blue-600">Dashboard</a>
              <a href="/routes" className="text-sm font-medium text-gray-600 hover:text-blue-600">Routes</a>
              <a href="/decisions" className="text-sm font-medium text-gray-600 hover:text-blue-600">Decisions</a>
            </div>
          </nav>
        </header>
        <main className="mx-auto max-w-7xl px-6 py-8">{children}</main>
      </body>
    </html>
  );
}
