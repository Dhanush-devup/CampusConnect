import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  AlertCircle,
  ArrowRight,
  Briefcase,
  CheckCircle2,
  Clock,
  Eye,
  FileCheck2,
  GraduationCap,
  Sparkles,
  Users,
} from "lucide-react";
import { applicationsApi, opportunitiesApi, profilesApi } from "../../api/endpoints";
import { Application, Opportunity, StudentDashboardStats } from "../../api/types";
import { DashboardLayout } from "../../components/DashboardLayout";
import { StatCard } from "../../components/StatCard";
import { StatusBadge } from "../../components/StatusBadge";
import { useAuth } from "../../context/AuthContext";

export const StudentDashboard: React.FC = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState<StudentDashboardStats | null>(null);
  const [recentApplications, setRecentApplications] = useState<Application[]>([]);
  const [featuredJobs, setFeaturedJobs] = useState<Opportunity[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const [statsData, appsData, jobsData] = await Promise.all([
          profilesApi.getStudentDashboardStats(),
          applicationsApi.listStudentApplications(),
          opportunitiesApi.list({ status: "open" }),
        ]);
        setStats(statsData);
        setRecentApplications(appsData.slice(0, 5));
        setFeaturedJobs(jobsData.slice(0, 4));
      } catch (err: any) {
        setError(err.message || "Failed to load dashboard data.");
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, []);

  const student = user?.student_profile;

  return (
    <DashboardLayout
      title={`Welcome back, ${user?.name || "Student"}!`}
      subtitle="Here is your placement application status and recently posted opportunities."
      actions={
        <Link
          to="/student/opportunities"
          className="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-4 py-2.5 text-xs font-semibold text-white shadow-sm hover:bg-indigo-500 transition-all"
        >
          <Briefcase className="h-4 w-4" />
          Explore Opportunities
        </Link>
      }
    >
      {error && (
        <div className="mb-6 rounded-xl bg-rose-50 border border-rose-200 p-4 text-xs text-rose-700 flex items-center gap-2">
          <AlertCircle className="h-4 w-4 shrink-0 text-rose-600" />
          <span>{error}</span>
        </div>
      )}

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
        <StatCard
          title="Total Applications"
          value={stats?.total_applications ?? 0}
          subtitle="Opportunities applied to"
          icon={FileCheck2}
          color="indigo"
        />
        <StatCard
          title="Under Review"
          value={stats?.under_review ?? 0}
          subtitle="Screening in progress"
          icon={Clock}
          color="amber"
        />
        <StatCard
          title="Interviews & Shortlists"
          value={(stats?.shortlisted ?? 0) + (stats?.interview ?? 0)}
          subtitle="Advanced stages"
          icon={Sparkles}
          color="violet"
        />
        <StatCard
          title="Offers / Selected"
          value={stats?.selected ?? 0}
          subtitle="Placement confirmed"
          icon={CheckCircle2}
          color="emerald"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column: Recent Applications */}
        <div className="lg:col-span-2 space-y-8">
          <div className="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-sm">
            <div className="flex items-center justify-between mb-5">
              <div>
                <h2 className="text-base font-bold text-slate-900">Recent Applications</h2>
                <p className="text-xs text-slate-500">Your latest candidate submissions</p>
              </div>
              <Link
                to="/student/applications"
                className="text-xs font-semibold text-indigo-600 hover:text-indigo-700 flex items-center gap-1"
              >
                View all ({stats?.total_applications ?? 0})
                <ArrowRight className="h-3.5 w-3.5" />
              </Link>
            </div>

            {isLoading ? (
              <div className="py-12 text-center text-xs text-slate-400">Loading applications...</div>
            ) : recentApplications.length === 0 ? (
              <div className="py-10 text-center rounded-xl bg-slate-50 border border-dashed border-slate-200">
                <FileCheck2 className="mx-auto h-8 w-8 text-slate-300 mb-2" />
                <p className="text-xs font-semibold text-slate-600">No applications submitted yet</p>
                <p className="text-[11px] text-slate-400 mt-0.5">Explore open campus opportunities and apply.</p>
                <Link
                  to="/student/opportunities"
                  className="mt-3 inline-block rounded-lg bg-indigo-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-indigo-500"
                >
                  Browse Jobs
                </Link>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr className="border-b border-slate-100 text-slate-400 font-semibold uppercase tracking-wider">
                      <th className="pb-3">Role & Company</th>
                      <th className="pb-3">Applied On</th>
                      <th className="pb-3">Status</th>
                      <th className="pb-3 text-right">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {recentApplications.map((app) => (
                      <tr key={app.application_id} className="hover:bg-slate-50/70 transition-colors">
                        <td className="py-3">
                          <p className="font-bold text-slate-900">{app.opportunity_title}</p>
                          <p className="text-slate-500 text-[11px]">{app.company_name}</p>
                        </td>
                        <td className="py-3 text-slate-600">
                          {new Date(app.application_date).toLocaleDateString()}
                        </td>
                        <td className="py-3">
                          <StatusBadge status={app.status} size="sm" />
                        </td>
                        <td className="py-3 text-right">
                          <Link
                            to="/student/applications"
                            className="inline-flex items-center gap-1 text-slate-500 hover:text-indigo-600 font-medium"
                          >
                            <Eye className="h-3.5 w-3.5" />
                            Details
                          </Link>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* Featured Open Opportunities */}
          <div className="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-sm">
            <div className="flex items-center justify-between mb-5">
              <div>
                <h2 className="text-base font-bold text-slate-900">Featured Open Opportunities</h2>
                <p className="text-xs text-slate-500">Currently active placement & internship drives</p>
              </div>
              <Link
                to="/student/opportunities"
                className="text-xs font-semibold text-indigo-600 hover:text-indigo-700 flex items-center gap-1"
              >
                Explore all
                <ArrowRight className="h-3.5 w-3.5" />
              </Link>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {featuredJobs.map((job) => (
                <div
                  key={job.opportunity_id}
                  className="rounded-xl border border-slate-200 p-4 hover:border-indigo-300 hover:shadow-xs transition-all flex flex-col justify-between"
                >
                  <div>
                    <div className="flex items-start justify-between gap-2 mb-2">
                      <span className="text-xs font-bold text-slate-800 line-clamp-1">{job.title}</span>
                      <StatusBadge status={job.opportunity_type} size="sm" />
                    </div>
                    <p className="text-xs text-slate-500 mb-2">{job.company.company_name}</p>
                    <div className="flex items-center gap-3 text-[11px] text-slate-400">
                      <span>Min CGPA: {job.eligibility_cgpa.toFixed(2)}</span>
                      {job.salary_stipend && <span>₹{job.salary_stipend.toLocaleString()}/mo</span>}
                    </div>
                  </div>
                  <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between">
                    <span className="text-[10px] text-slate-400">
                      Closes: {new Date(job.deadline).toLocaleDateString()}
                    </span>
                    <Link
                      to="/student/opportunities"
                      className="text-xs font-semibold text-indigo-600 hover:underline"
                    >
                      View & Apply &rarr;
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column: Student Academic Card */}
        <div className="space-y-6">
          <div className="bg-gradient-to-br from-indigo-900 via-indigo-800 to-indigo-950 text-white rounded-2xl p-6 shadow-md shadow-indigo-950/20">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-xl bg-white/10 flex items-center justify-center">
                <GraduationCap className="h-5 w-5 text-indigo-200" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-white">Student Academic Profile</h3>
                <p className="text-[11px] text-indigo-200">{user?.email}</p>
              </div>
            </div>

            <div className="space-y-3 border-t border-white/10 pt-4 text-xs">
              <div className="flex justify-between items-center">
                <span className="text-indigo-200">Department</span>
                <span className="font-semibold text-white">{student?.department || "Unassigned"}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-indigo-200">Current CGPA</span>
                <span className="font-bold text-emerald-400 bg-emerald-950/60 border border-emerald-500/30 px-2 py-0.5 rounded text-xs">
                  {student?.cgpa.toFixed(2) || "0.00"} / 10.0
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-indigo-200">Graduation Class</span>
                <span className="font-semibold text-white">{student?.graduation_year || "2026"}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-indigo-200">Eligible Drives</span>
                <span className="font-semibold text-white">
                  {stats?.eligible_opportunities_count ?? 0} Opportunities
                </span>
              </div>
            </div>

            <div className="mt-5 pt-4 border-t border-white/10">
              <Link
                to="/student/profile"
                className="w-full inline-flex items-center justify-center gap-1.5 rounded-xl bg-white/10 hover:bg-white/20 py-2 text-xs font-semibold text-white transition-colors"
              >
                Update Academic Details
              </Link>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
};
