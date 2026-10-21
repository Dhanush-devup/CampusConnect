import React from "react";
import { Link } from "react-router-dom";
import {
  ArrowRight,
  BarChart3,
  Briefcase,
  Building2,
  CheckCircle2,
  GraduationCap,
  ShieldCheck,
  Sparkles,
  Users,
} from "lucide-react";
import { Navbar } from "../components/Navbar";

export const LandingPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <Navbar />

      {/* Hero Section */}
      <section className="relative overflow-hidden bg-white pt-16 pb-20 border-b border-slate-200/80">
        <div className="absolute inset-0 bg-[radial-gradient(#e0e7ff_1px,transparent_1px)] [background-size:16px_16px] opacity-40 pointer-events-none" />
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="inline-flex items-center gap-2 rounded-full bg-indigo-50 px-3.5 py-1 text-xs font-semibold text-indigo-700 border border-indigo-200/80 mb-6 shadow-xs">
            <Sparkles className="h-3.5 w-3.5 text-indigo-600" />
            Next-Gen College Placement Management
          </div>

          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-slate-900 max-w-4xl mx-auto leading-tight">
            Connecting Ambitious Students with{" "}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-violet-600">
              Leading Employers
            </span>
          </h1>

          <p className="mt-6 text-lg text-slate-600 max-w-2xl mx-auto leading-relaxed">
            CampusConnect unifies campus recruitments, automated CGPA eligibility checks,
            transparent hiring pipelines, and real-time institutional analytics in one platform.
          </p>

          <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              to="/login"
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 rounded-xl bg-indigo-600 px-6 py-3.5 text-sm font-semibold text-white shadow-md shadow-indigo-500/20 hover:bg-indigo-500 transition-all"
            >
              Sign In to Portal
              <ArrowRight className="h-4 w-4" />
            </Link>
            <Link
              to="/register/student"
              className="w-full sm:w-auto inline-flex items-center justify-center rounded-xl border border-slate-300 bg-white px-6 py-3.5 text-sm font-semibold text-slate-700 shadow-xs hover:bg-slate-50 hover:border-slate-400 transition-all"
            >
              Register as Student
            </Link>
            <Link
              to="/register/recruiter"
              className="w-full sm:w-auto inline-flex items-center justify-center rounded-xl border border-indigo-200 bg-indigo-50/50 px-6 py-3.5 text-sm font-semibold text-indigo-700 hover:bg-indigo-100/70 transition-all"
            >
              Hire from Campus
            </Link>
          </div>
        </div>
      </section>

      {/* Role Portals Grid */}
      <section className="py-16 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
            Designed for Every Campus Stakeholder
          </h2>
          <p className="mt-2 text-sm text-slate-500">
            Dedicated portals crafted for seamless interaction between students, recruiters, and placement officers.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Student Card */}
          <div className="bg-white rounded-2xl p-8 border border-slate-200/80 shadow-sm hover:shadow-md transition-all flex flex-col justify-between">
            <div>
              <div className="w-12 h-12 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center mb-6">
                <GraduationCap className="h-6 w-6" />
              </div>
              <h3 className="text-xl font-bold text-slate-900 mb-2">Student Portal</h3>
              <p className="text-sm text-slate-600 mb-6 leading-relaxed">
                Discover job and internship opportunities, view CGPA requirements, submit applications with PDF resumes, and track hiring stages live.
              </p>
              <ul className="space-y-2.5 text-xs text-slate-600 font-medium mb-6">
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-emerald-500" />
                  Automated CGPA eligibility verification
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-emerald-500" />
                  Real-time status tracking (Review, Interview, Selected)
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-emerald-500" />
                  One-click application with PDF resume upload
                </li>
              </ul>
            </div>
            <Link
              to="/register/student"
              className="inline-flex items-center justify-center rounded-xl bg-indigo-50 py-2.5 text-xs font-bold text-indigo-700 hover:bg-indigo-100 transition-colors"
            >
              Student Registration &rarr;
            </Link>
          </div>

          {/* Recruiter Card */}
          <div className="bg-white rounded-2xl p-8 border border-slate-200/80 shadow-sm hover:shadow-md transition-all flex flex-col justify-between">
            <div>
              <div className="w-12 h-12 rounded-xl bg-violet-50 text-violet-600 flex items-center justify-center mb-6">
                <Building2 className="h-6 w-6" />
              </div>
              <h3 className="text-xl font-bold text-slate-900 mb-2">Recruiter Portal</h3>
              <p className="text-sm text-slate-600 mb-6 leading-relaxed">
                Post full-time and internship openings, filter applicant pools by department and CGPA, view resumes securely, and update candidate stages.
              </p>
              <ul className="space-y-2.5 text-xs text-slate-600 font-medium mb-6">
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-emerald-500" />
                  Company-isolated candidate pipeline
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-emerald-500" />
                  Instant status transitions (Shortlist, Interview, Select)
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-emerald-500" />
                  Authorized, secure resume downloads
                </li>
              </ul>
            </div>
            <Link
              to="/register/recruiter"
              className="inline-flex items-center justify-center rounded-xl bg-violet-50 py-2.5 text-xs font-bold text-violet-700 hover:bg-violet-100 transition-colors"
            >
              Recruiter Registration &rarr;
            </Link>
          </div>

          {/* Admin Card */}
          <div className="bg-white rounded-2xl p-8 border border-slate-200/80 shadow-sm hover:shadow-md transition-all flex flex-col justify-between">
            <div>
              <div className="w-12 h-12 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center mb-6">
                <BarChart3 className="h-6 w-6" />
              </div>
              <h3 className="text-xl font-bold text-slate-900 mb-2">Placement Cell Oversight</h3>
              <p className="text-sm text-slate-600 mb-6 leading-relaxed">
                College-wide oversight of placement percentages, partner companies, open job requisitions, and account activation controls.
              </p>
              <ul className="space-y-2.5 text-xs text-slate-600 font-medium mb-6">
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-emerald-500" />
                  Real-time database-driven placement KPI statistics
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-emerald-500" />
                  Complete user account status governance
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-emerald-500" />
                  Zero hardcoded data — 100% database backed
                </li>
              </ul>
            </div>
            <Link
              to="/login"
              className="inline-flex items-center justify-center rounded-xl bg-amber-50 py-2.5 text-xs font-bold text-amber-700 hover:bg-amber-100 transition-colors"
            >
              Admin Sign In &rarr;
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="mt-auto border-t border-slate-200 bg-white py-8 text-center text-xs text-slate-400">
        <p>CampusConnect • Internship & Placement Management System • Academic DBMS Project</p>
      </footer>
    </div>
  );
};
