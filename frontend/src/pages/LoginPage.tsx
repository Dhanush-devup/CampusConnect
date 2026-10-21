import React, { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { AlertCircle, ArrowRight, GraduationCap, KeyRound, Lock, Mail } from "lucide-react";
import { authApi } from "../api/endpoints";
import { useAuth } from "../context/AuthContext";
import { Navbar } from "../components/Navbar";

export const LoginPage: React.FC = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const from = (location.state as any)?.from?.pathname || null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      const res = await authApi.login({ email, password });
      login(res.access_token, res.user);

      // Redirect according to role
      if (from) {
        navigate(from, { replace: true });
      } else {
        const roleHome = {
          student: "/student",
          recruiter: "/recruiter",
          admin: "/admin",
        }[res.user.role];
        navigate(roleHome || "/");
      }
    } catch (err: any) {
      setError(err.message || "Failed to authenticate. Please check your credentials.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDemoLogin = async (demoEmail: string, demoPassword: string) => {
    setEmail(demoEmail);
    setPassword(demoPassword);
    setError(null);
    setIsSubmitting(true);

    try {
      const res = await authApi.login({ email: demoEmail, password: demoPassword });
      login(res.access_token, res.user);
      const roleHome = {
        student: "/student",
        recruiter: "/recruiter",
        admin: "/admin",
      }[res.user.role];
      navigate(roleHome || "/");
    } catch (err: any) {
      setError(err.message || "Could not log in with demo account. Ensure backend has initialized.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <Navbar />

      <div className="flex-1 flex items-center justify-center p-4 sm:p-6 lg:p-8">
        <div className="w-full max-w-md">
          {/* Card */}
          <div className="bg-white rounded-2xl shadow-xl shadow-slate-200/50 border border-slate-200/80 p-8">
            <div className="text-center mb-8">
              <div className="mx-auto w-12 h-12 rounded-2xl bg-indigo-600 text-white flex items-center justify-center shadow-lg shadow-indigo-500/30 mb-4">
                <Lock className="h-6 w-6" />
              </div>
              <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Sign in to your account</h2>
              <p className="mt-1 text-xs text-slate-500">
                Enter your credentials or choose a 1-click evaluation account
              </p>
            </div>

            {error && (
              <div className="mb-6 rounded-xl bg-rose-50 border border-rose-200 p-3.5 text-xs text-rose-700 flex items-start gap-2.5">
                <AlertCircle className="h-4 w-4 shrink-0 mt-0.5 text-rose-600" />
                <span>{error}</span>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                  Email Address
                </label>
                <div className="relative">
                  <Mail className="absolute left-3.5 top-3 h-4 w-4 text-slate-400" />
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="name@college.edu"
                    className="w-full rounded-xl border border-slate-300 pl-10 pr-3.5 py-2.5 text-sm text-slate-900 placeholder:text-slate-400 focus:border-indigo-600 focus:outline-none focus:ring-1 focus:ring-indigo-600 transition-colors"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                  Password
                </label>
                <div className="relative">
                  <KeyRound className="absolute left-3.5 top-3 h-4 w-4 text-slate-400" />
                  <input
                    type="password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full rounded-xl border border-slate-300 pl-10 pr-3.5 py-2.5 text-sm text-slate-900 placeholder:text-slate-400 focus:border-indigo-600 focus:outline-none focus:ring-1 focus:ring-indigo-600 transition-colors"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={isSubmitting}
                className="w-full mt-2 flex items-center justify-center gap-2 rounded-xl bg-indigo-600 py-3 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-600 focus:ring-offset-2 disabled:opacity-50 transition-all"
              >
                {isSubmitting ? "Authenticating..." : "Sign In"}
                {!isSubmitting && <ArrowRight className="h-4 w-4" />}
              </button>
            </form>

            {/* Demo Quick Logins for College Project Evaluation */}
            <div className="mt-8 pt-6 border-t border-slate-100">
              <p className="text-[11px] font-bold uppercase tracking-wider text-slate-400 text-center mb-3">
                Evaluation Demo Accounts
              </p>
              <div className="grid grid-cols-3 gap-2">
                <button
                  type="button"
                  onClick={() => handleDemoLogin("admin@campusconnect.edu", "Admin@123")}
                  className="rounded-lg border border-purple-200 bg-purple-50/70 py-2 px-2 text-[11px] font-bold text-purple-700 hover:bg-purple-100 transition-colors"
                >
                  Admin
                </button>
                <button
                  type="button"
                  onClick={() => handleDemoLogin("recruiter@techcorp.com", "Demo@123")}
                  className="rounded-lg border border-violet-200 bg-violet-50/70 py-2 px-2 text-[11px] font-bold text-violet-700 hover:bg-violet-100 transition-colors"
                >
                  Recruiter
                </button>
                <button
                  type="button"
                  onClick={() => handleDemoLogin("student@demo.edu", "Demo@123")}
                  className="rounded-lg border border-indigo-200 bg-indigo-50/70 py-2 px-2 text-[11px] font-bold text-indigo-700 hover:bg-indigo-100 transition-colors"
                >
                  Student
                </button>
              </div>
            </div>

            {/* Registration Links */}
            <div className="mt-6 text-center text-xs text-slate-500 space-y-1.5">
              <p>
                New student?{" "}
                <Link to="/register/student" className="font-semibold text-indigo-600 hover:underline">
                  Register student profile
                </Link>
              </p>
              <p>
                New recruiter?{" "}
                <Link to="/register/recruiter" className="font-semibold text-violet-600 hover:underline">
                  Register company account
                </Link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
