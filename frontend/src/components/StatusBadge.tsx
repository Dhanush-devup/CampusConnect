import React from "react";

interface StatusBadgeProps {
  status: string;
  size?: "sm" | "md";
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, size = "md" }) => {
  const normalized = status.toLowerCase();

  const getStyle = () => {
    switch (normalized) {
      // Application statuses
      case "applied":
        return "bg-blue-50 text-blue-700 border-blue-200 ring-blue-500/10";
      case "under_review":
        return "bg-amber-50 text-amber-700 border-amber-200 ring-amber-500/10";
      case "shortlisted":
        return "bg-purple-50 text-purple-700 border-purple-200 ring-purple-500/10";
      case "interview":
        return "bg-cyan-50 text-cyan-700 border-cyan-200 ring-cyan-500/10";
      case "selected":
        return "bg-emerald-50 text-emerald-700 border-emerald-200 ring-emerald-500/10 font-semibold";
      case "rejected":
        return "bg-rose-50 text-rose-700 border-rose-200 ring-rose-500/10";

      // Opportunity statuses
      case "open":
        return "bg-emerald-50 text-emerald-700 border-emerald-200";
      case "closed":
        return "bg-slate-100 text-slate-700 border-slate-200";
      case "draft":
        return "bg-amber-50 text-amber-700 border-amber-200";

      // Account statuses
      case "active":
        return "bg-emerald-50 text-emerald-700 border-emerald-200";
      case "disabled":
        return "bg-rose-50 text-rose-700 border-rose-200";

      // Roles
      case "student":
        return "bg-indigo-50 text-indigo-700 border-indigo-200";
      case "recruiter":
        return "bg-violet-50 text-violet-700 border-violet-200";
      case "admin":
        return "bg-purple-50 text-purple-700 border-purple-200";

      default:
        return "bg-slate-50 text-slate-600 border-slate-200";
    }
  };

  const formatText = (text: string) => {
    return text
      .split("_")
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ");
  };

  const sizeClasses = size === "sm" ? "px-2 py-0.5 text-xs" : "px-2.5 py-1 text-xs font-medium";

  return (
    <span
      className={`inline-flex items-center rounded-full border shadow-sm ring-1 ring-inset ${getStyle()} ${sizeClasses}`}
    >
      <span className="w-1.5 h-1.5 rounded-full bg-current mr-1.5 opacity-70"></span>
      {formatText(status)}
    </span>
  );
};
