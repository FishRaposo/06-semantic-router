import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "SemanticRouter Dashboard",
  description: "Monitor and manage semantic routing decisions",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="font-sans antialiased">
        <nav className="border-b border-gray-200 bg-white px-6 py-4">
          <div className="mx-auto flex max-w-7xl items-center justify-between">
            <a href="/" className="text-xl font-bold text-gray-900">
              SemanticRouter
            </a>
            <div className="flex gap-6">
              <a
                href="/"
                className="text-sm font-medium text-gray-600 hover:text-gray-900"
              >
                Dashboard
              </a>
              <a
                href="/routes"
                className="text-sm font-medium text-gray-600 hover:text-gray-900"
              >
                Routes
              </a>
            </div>
          </div>
        </nav>
        <main className="mx-auto max-w-7xl px-6 py-8">{children}</main>
      </body>
    </html>
  );
}
