import React from "react";
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { RoleType } from "../api/types";

interface ProtectedRouteProps {
  children: React.ReactNode;
  allowedRoles?: RoleType[];
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  allowedRoles,
}) => {
  const { user, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center bg-slate-50">
        <div className="flex flex-col items-center gap-3">
          <div className="h-10 w-10 animate-spin rounded-full border-4 border-indigo-600 border-t-transparent" />
          <p className="text-sm font-medium text-slate-500">Loading CampusConnect...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (allowedRoles && !allowedRoles.includes(user.role)) {
    // Redirect to their respective authorized home
    const roleRedirectMap: Record<RoleType, string> = {
      student: "/student",
      recruiter: "/recruiter",
      admin: "/admin",
    };
    return <Navigate to={roleRedirectMap[user.role] || "/"} replace />;
  }

  return <>{children}</>;
};
