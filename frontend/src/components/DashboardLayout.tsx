import React, { useState } from "react";
import { Navbar } from "./Navbar";
import { Sidebar } from "./Sidebar";

interface DashboardLayoutProps {
  children: React.ReactNode;
  title?: string;
  subtitle?: string;
  actions?: React.ReactNode;
}

export const DashboardLayout: React.FC<DashboardLayoutProps> = ({
  children,
  title,
  subtitle,
  actions,
}) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <Navbar onToggleSidebar={() => setSidebarOpen(!sidebarOpen)} />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
        <main className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8">
          {(title || actions) && (
            <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
              <div>
                {title && <h1 className="text-2xl font-bold tracking-tight text-slate-900">{title}</h1>}
                {subtitle && <p className="mt-1 text-sm text-slate-500">{subtitle}</p>}
              </div>
              {actions && <div className="flex items-center gap-3">{actions}</div>}
            </div>
          )}
          {children}
        </main>
      </div>
    </div>
  );
};
