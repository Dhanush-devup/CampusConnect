import React from "react";
import { LucideIcon } from "lucide-react";

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  color?: "indigo" | "emerald" | "amber" | "violet" | "rose" | "cyan";
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  subtitle,
  icon: Icon,
  color = "indigo",
}) => {
  const colorMap = {
    indigo: {
      bg: "bg-indigo-50",
      text: "text-indigo-600",
      border: "hover:border-indigo-200",
      ring: "group-hover:ring-indigo-100",
    },
    emerald: {
      bg: "bg-emerald-50",
      text: "text-emerald-600",
      border: "hover:border-emerald-200",
      ring: "group-hover:ring-emerald-100",
    },
    amber: {
      bg: "bg-amber-50",
      text: "text-amber-600",
      border: "hover:border-amber-200",
      ring: "group-hover:ring-amber-100",
    },
    violet: {
      bg: "bg-violet-50",
      text: "text-violet-600",
      border: "hover:border-violet-200",
      ring: "group-hover:ring-violet-100",
    },
    rose: {
      bg: "bg-rose-50",
      text: "text-rose-600",
      border: "hover:border-rose-200",
      ring: "group-hover:ring-rose-100",
    },
    cyan: {
      bg: "bg-cyan-50",
      text: "text-cyan-600",
      border: "hover:border-cyan-200",
      ring: "group-hover:ring-cyan-100",
    },
  };

  const scheme = colorMap[color];

  return (
    <div
      className={`group relative overflow-hidden rounded-2xl bg-white p-6 shadow-sm border border-slate-100 transition-all duration-200 hover:shadow-md ${scheme.border}`}
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
            {title}
          </p>
          <p className="mt-2 text-3xl font-bold tracking-tight text-slate-900">
            {value}
          </p>
          {subtitle && (
            <p className="mt-1 text-xs text-slate-500 flex items-center gap-1">
              {subtitle}
            </p>
          )}
        </div>
        <div
          className={`flex h-12 w-12 items-center justify-center rounded-xl ${scheme.bg} ${scheme.text} transition-transform duration-200 group-hover:scale-110`}
        >
          <Icon className="h-6 w-6" />
        </div>
      </div>
    </div>
  );
};
