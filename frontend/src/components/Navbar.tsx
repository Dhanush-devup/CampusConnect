import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { GraduationCap, LogOut, Menu, User as UserIcon } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { StatusBadge } from "./StatusBadge";

interface NavbarProps {
  onToggleSidebar?: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ onToggleSidebar }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate("/login");
  };

  return (
    <header className="sticky top-0 z-30 flex h-16 w-full items-center justify-between border-b border-slate-200 bg-white/90 px-4 sm:px-6 backdrop-blur-md">
      <div className="flex items-center gap-3">
        {onToggleSidebar && (
          <button
            onClick={onToggleSidebar}
            className="rounded-lg p-2 text-slate-500 hover:bg-slate-100 lg:hidden"
            aria-label="Toggle Navigation"
          >
            <Menu className="h-5 w-5" />
          </button>
        )}
        <Link to="/" className="flex items-center gap-2.5">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-tr from-indigo-600 to-indigo-500 text-white shadow-md shadow-indigo-500/20">
            <GraduationCap className="h-6 w-6" />
          </div>
          <div>
            <span className="text-lg font-extrabold tracking-tight text-slate-900">
              Campus<span className="text-indigo-600">Connect</span>
            </span>
            <span className="hidden sm:inline-block ml-2 text-[10px] font-semibold uppercase tracking-wider text-slate-400 border border-slate-200 rounded px-1.5 py-0.5">
              Placement Portal
            </span>
          </div>
        </Link>
      </div>

      <div className="flex items-center gap-3">
        {user ? (
          <div className="flex items-center gap-3">
            <div className="hidden sm:flex flex-col text-right">
              <span className="text-sm font-semibold text-slate-900 leading-none">{user.name}</span>
              <span className="text-xs text-slate-500 mt-1">{user.email}</span>
            </div>
            <StatusBadge status={user.role} size="sm" />
            <button
              onClick={handleLogout}
              className="flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-medium text-slate-700 shadow-sm hover:bg-slate-50 hover:text-rose-600 transition-colors"
              title="Sign Out"
            >
              <LogOut className="h-3.5 w-3.5" />
              <span className="hidden sm:inline">Logout</span>
            </button>
          </div>
        ) : (
          <div className="flex items-center gap-2">
            <Link
              to="/login"
              className="rounded-lg px-3.5 py-2 text-sm font-semibold text-slate-700 hover:text-indigo-600"
            >
              Sign In
            </Link>
            <Link
              to="/register/student"
              className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 transition-colors"
            >
              Get Started
            </Link>
          </div>
        )}
      </div>
    </header>
  );
};
