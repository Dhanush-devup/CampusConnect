import React from "react";
import { Link, useLocation } from "react-router-dom";
import {
  BarChart3,
  Briefcase,
  Building2,
  FileCheck2,
  FileText,
  GraduationCap,
  LayoutDashboard,
  ShieldCheck,
  UserCheck,
  Users,
} from "lucide-react";
import { useAuth } from "../context/AuthContext";

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose }) => {
  const { user } = useAuth();
  const location = useLocation();

  if (!user) return null;

  const isActive = (path: string) => {
    if (path === "/student" || path === "/recruiter" || path === "/admin") {
      return location.pathname === path;
    }
    return location.pathname.startsWith(path);
  };

  const getNavItems = () => {
    switch (user.role) {
      case "student":
        return [
          { label: "Overview", path: "/student", icon: LayoutDashboard },
          { label: "Explore Opportunities", path: "/student/opportunities", icon: Briefcase },
          { label: "My Applications", path: "/student/applications", icon: FileCheck2 },
          { label: "Academic Profile", path: "/student/profile", icon: GraduationCap },
        ];
      case "recruiter":
        return [
          { label: "Dashboard", path: "/recruiter", icon: LayoutDashboard },
          { label: "Manage Jobs", path: "/recruiter/opportunities", icon: Briefcase },
          { label: "Candidate Review", path: "/recruiter/applications", icon: FileText },
          { label: "Company Profile", path: "/recruiter/company", icon: Building2 },
        ];
      case "admin":
        return [
          { label: "Analytics & KPIs", path: "/admin", icon: BarChart3 },
          { label: "User Accounts", path: "/admin/users", icon: Users },
          { label: "Partner Companies", path: "/admin/companies", icon: Building2 },
          { label: "All Postings", path: "/admin/opportunities", icon: Briefcase },
          { label: "All Applications", path: "/admin/applications", icon: FileCheck2 },
        ];
      default:
        return [];
    }
  };

  const navItems = getNavItems();

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-slate-900/40 backdrop-blur-sm lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar Panel */}
      <aside
        className={`fixed inset-y-0 left-0 z-40 w-64 transform border-r border-slate-200 bg-white transition-transform duration-200 ease-in-out lg:static lg:translate-x-0 ${
          isOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="flex h-16 items-center border-b border-slate-100 px-6">
          <div className="flex items-center gap-2">
            <ShieldCheck className="h-5 w-5 text-indigo-600" />
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
              {user.role} workspace
            </span>
          </div>
        </div>

        <nav className="p-4 space-y-1">
          {navItems.map((item) => {
            const active = isActive(item.path);
            const Icon = item.icon;
            return (
              <Link
                key={item.path}
                to={item.path}
                onClick={onClose}
                className={`flex items-center gap-3 rounded-xl px-3.5 py-2.5 text-sm font-semibold transition-all ${
                  active
                    ? "bg-indigo-600 text-white shadow-sm shadow-indigo-500/25"
                    : "text-slate-600 hover:bg-slate-50 hover:text-indigo-600"
                }`}
              >
                <Icon className={`h-5 w-5 ${active ? "text-white" : "text-slate-400"}`} />
                {item.label}
              </Link>
            );
          })}
        </nav>

        {/* User Card at bottom of sidebar */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-slate-100 bg-slate-50/50">
          <div className="rounded-xl bg-white p-3 border border-slate-200/80 shadow-xs">
            <p className="text-xs font-bold text-slate-800 truncate">{user.name}</p>
            <p className="text-[11px] text-slate-400 truncate">{user.email}</p>
            {user.student_profile && (
              <div className="mt-2 flex items-center justify-between text-[11px] text-indigo-600 font-medium">
                <span>{user.student_profile.department}</span>
                <span>CGPA: {user.student_profile.cgpa.toFixed(2)}</span>
              </div>
            )}
            {user.company && (
              <p className="mt-1 text-[11px] text-violet-600 font-medium truncate">
                {user.company.company_name}
              </p>
            )}
          </div>
        </div>
      </aside>
    </>
  );
};
