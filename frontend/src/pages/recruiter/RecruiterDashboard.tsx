import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  AlertCircle,
  Briefcase,
  Building2,
  CheckCircle2,
  Clock,
  FileText,
  Plus,
  Sparkles,
  Users,
} from "lucide-react";
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Cell } from "recharts";
import { applicationsApi, opportunitiesApi, profilesApi } from "../../api/endpoints";
import { Application, Opportunity, RecruiterDashboardStats } from "../../api/types";
import { DashboardLayout } from "../../components/DashboardLayout";
import { StatCard } from "../../components/StatCard";
import { StatusBadge } from "../../components/StatusBadge";
import { useAuth } from "../../context/AuthContext";

export const RecruiterDashboard: React.FC = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState<RecruiterDashboardStats | null>(null);
  const [recentApplications, setRecentApplications] = useState<Application[]>([]);
  const [companyJobs, setCompanyJobs] = useState<Opportunity[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const [statsData, appsData, jobsData] = await Promise.all([
          profilesApi.getRecruiterDashboardStats(),
          applicationsApi.listRecruiterApplications(),
          opportunitiesApi.list({ company_id: user?.company_id || undefined }),
        ]);
        setStats(statsData);
        setRecentApplications(appsData.slice(0, 5));
        setCompanyJobs(jobsData.slice(0, 4));
      } catch (err: any) {
        setError(err.message || "Failed to load recruiter analytics.");
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [user]);

  const funnelData = [
    { name: "Applied", count: stats?.applied || 0, color: "#3b82f6" },
    { name: "Under Review", count: stats?.under_review || 0, color: "#f59e0b" },
    { name: "Shortlisted", count: stats?.shortlisted || 0, color: "#8b5cf6" },
    { name: "Interview", count: stats?.interview || 0, color: "#06b6d4" },
    { name: "Selected", count: stats?.selected || 0, color: "#10b981" },
    { name: "Rejected", count: stats?.rejected || 0, color: "#f43f5e" },
  ];

  return (
    <DashboardLayout
      title={`${user?.company?.company_name || "Employer"} Recruiter Hub`}
      subtitle="Monitor your job requisitions, candidate pipeline, and hiring conversion rates."
      actions={
        <Link
          to="/recruiter/opportunities"
          className="inline-flex items-center gap-2 rounded-xl bg-violet-600 px-4 py-2.5 text-xs font-semibold text-white shadow-sm hover:bg-violet-500 transition-all"
        >
          <Plus className="h-4 w-4" />
          Post New Opportunity
        </Link>
      }
    >
      {error && (
        <div className="mb-6 rounded-xl bg-rose-50 border border-rose-200 p-4 text-xs text-rose-700 flex items-center gap-2">
          <AlertCircle className="h-4 w-4 shrink-0 text-rose-600" />
          <span>{error}</span>
        </div>
      )}

      {/* KPI Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
        <StatCard
          title="Active Drives"
          value={stats?.open_opportunities ?? 0}
          subtitle={`${stats?.total_opportunities ?? 0} total postings`}
          icon={Briefcase}
          color="violet"
        />
        <StatCard
          title="Total Candidates"
          value={stats?.total_applications ?? 0}
          subtitle="Applications received"
          icon={Users}
          color="indigo"
        />
        <StatCard
          title="In Screening / Interview"
          value={(stats?.under_review ?? 0) + (stats?.shortlisted ?? 0) + (stats?.interview ?? 0)}
          subtitle="Active pipeline"
          icon={Sparkles}
          color="cyan"
        />
        <StatCard
          title="Offers Accepted"
          value={stats?.selected ?? 0}
          subtitle="Final selections"
          icon={CheckCircle2}
          color="emerald"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Funnel Chart */}
        <div className="lg:col-span-2 bg-white rounded-2xl border border-slate-200/80 p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-base font-bold text-slate-900">Candidate Recruitment Funnel</h2>
              <p className="text-xs text-slate-500">Real-time candidate count across each hiring stage</p>
            </div>
            <Link
              to="/recruiter/applications"
              className="text-xs font-semibold text-violet-600 hover:text-violet-700"
            >
              Review Pipeline &rarr;
            </Link>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={funnelData} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                <XAxis dataKey="name" tick={{ fontSize: 11 }} interval={0} stroke="#94a3b8" />
                <YAxis tick={{ fontSize: 11 }} stroke="#94a3b8" allowDecimals={false} />
                <Tooltip
                  cursor={{ fill: "transparent" }}
                  contentStyle={{
                    borderRadius: "12px",
                    border: "1px solid #e2e8f0",
                    fontSize: "12px",
                  }}
                />
                <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                  {funnelData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Company Profile Quick Card */}
        <div className="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-xl bg-violet-50 text-violet-600 flex items-center justify-center">
                <Building2 className="h-5 w-5" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-slate-900">{user?.company?.company_name}</h3>
                <p className="text-[11px] text-slate-400">{user?.company?.industry || "Technology"}</p>
              </div>
            </div>

            <div className="space-y-2.5 text-xs text-slate-600 border-t border-slate-100 pt-3">
              <div className="flex justify-between">
                <span className="text-slate-400">Contact Email:</span>
                <span className="font-medium text-slate-800">{user?.company?.email}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Location:</span>
                <span className="font-medium text-slate-800">{user?.company?.location || "Headquarters"}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Total Postings:</span>
                <span className="font-medium text-slate-800">{stats?.total_opportunities ?? 0}</span>
              </div>
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-slate-100">
            <Link
              to="/recruiter/company"
              className="w-full inline-flex items-center justify-center rounded-xl bg-violet-50 hover:bg-violet-100 py-2 text-xs font-semibold text-violet-700 transition-colors"
            >
              Edit Company Profile
            </Link>
          </div>
        </div>
      </div>

      {/* Recent Candidate Submissions */}
      <div className="mt-8 bg-white rounded-2xl border border-slate-200/80 p-6 shadow-sm">
        <div className="flex items-center justify-between mb-5">
          <div>
            <h2 className="text-base font-bold text-slate-900">Recent Candidate Applications</h2>
            <p className="text-xs text-slate-500">Students who recently applied to your job postings</p>
          </div>
          <Link
            to="/recruiter/applications"
            className="text-xs font-semibold text-violet-600 hover:text-violet-700"
          >
            Open Candidate Desk &rarr;
          </Link>
        </div>

        {recentApplications.length === 0 ? (
          <div className="py-10 text-center rounded-xl bg-slate-50 border border-dashed border-slate-200">
            <FileText className="mx-auto h-8 w-8 text-slate-300 mb-2" />
            <p className="text-xs font-semibold text-slate-600">No applicants yet</p>
            <p className="text-[11px] text-slate-400 mt-0.5">
              Make sure your hiring drives are marked as "Open".
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-100 text-slate-400 font-semibold uppercase tracking-wider">
                  <th className="pb-3">Candidate</th>
                  <th className="pb-3">Department</th>
                  <th className="pb-3">CGPA</th>
                  <th className="pb-3">Job Title</th>
                  <th className="pb-3">Status</th>
                  <th className="pb-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {recentApplications.map((app) => (
                  <tr key={app.application_id} className="hover:bg-slate-50/70 transition-colors">
                    <td className="py-3 font-bold text-slate-900">
                      {app.student_name}
                      <p className="font-normal text-slate-400 text-[11px]">{app.student_email}</p>
                    </td>
                    <td className="py-3 text-slate-600">{app.student_department}</td>
                    <td className="py-3 font-semibold text-emerald-600">{app.student_cgpa.toFixed(2)}</td>
                    <td className="py-3 text-slate-700 font-medium">{app.opportunity_title}</td>
                    <td className="py-3">
                      <StatusBadge status={app.status} size="sm" />
                    </td>
                    <td className="py-3 text-right">
                      <Link
                        to="/recruiter/applications"
                        className="inline-flex items-center gap-1 text-violet-600 hover:text-violet-700 font-semibold"
                      >
                        Review
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
};
