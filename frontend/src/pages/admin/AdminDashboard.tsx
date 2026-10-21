import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  AlertCircle,
  Award,
  BarChart3,
  Briefcase,
  Building2,
  CheckCircle2,
  FileCheck2,
  GraduationCap,
  Percent,
  ShieldCheck,
  TrendingUp,
  Users,
} from "lucide-react";
import {
  Bar,
  BarChart,
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { adminApi } from "../../api/endpoints";
import { AdminDashboardStats } from "../../api/types";
import { DashboardLayout } from "../../components/DashboardLayout";
import { StatCard } from "../../components/StatCard";

export const AdminDashboard: React.FC = () => {
  const [stats, setStats] = useState<AdminDashboardStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const data = await adminApi.getStatistics();
        setStats(data);
      } catch (err: any) {
        setError(err.message || "Failed to load placement analytics.");
      } finally {
        setIsLoading(false);
      }
    };

    fetchStats();
  }, []);

  const statusColors: Record<string, string> = {
    applied: "#3b82f6",
    under_review: "#f59e0b",
    shortlisted: "#8b5cf6",
    interview: "#06b6d4",
    selected: "#10b981",
    rejected: "#f43f5e",
  };

  const statusPieData = stats
    ? Object.entries(stats.applications_by_status || {}).map(([key, val]) => ({
        name: key.replace("_", " ").toUpperCase(),
        value: val,
        color: statusColors[key] || "#94a3b8",
      }))
    : [];

  const deptBarData = stats
    ? Object.entries(stats.applications_by_department || {}).map(([dept, count]) => ({
        department: dept.length > 15 ? dept.slice(0, 15) + "…" : dept,
        applications: count,
      }))
    : [];

  return (
    <DashboardLayout
      title="Institutional Placement Analytics"
      subtitle="Real-time database metrics across students, recruitment partners, and hiring conversions."
      actions={
        <div className="flex items-center gap-2">
          <Link
            to="/admin/users"
            className="inline-flex items-center gap-1.5 rounded-xl border border-slate-300 bg-white px-3.5 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-50 transition-colors"
          >
            <Users className="h-4 w-4 text-slate-500" />
            Manage Accounts
          </Link>
          <Link
            to="/admin/opportunities"
            className="inline-flex items-center gap-1.5 rounded-xl bg-slate-900 px-3.5 py-2 text-xs font-semibold text-white hover:bg-slate-800 transition-colors"
          >
            <Briefcase className="h-4 w-4" />
            Review Postings
          </Link>
        </div>
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
          title="Campus Placement Rate"
          value={`${stats?.placement_rate ?? 0}%`}
          subtitle="Students with confirmed offers"
          icon={Percent}
          color="emerald"
        />
        <StatCard
          title="Total Registered Students"
          value={stats?.students_count ?? 0}
          subtitle={`${stats?.total_users ?? 0} total system users`}
          icon={GraduationCap}
          color="indigo"
        />
        <StatCard
          title="Partner Companies"
          value={stats?.total_companies ?? 0}
          subtitle={`${stats?.recruiters_count ?? 0} active recruiter accounts`}
          icon={Building2}
          color="violet"
        />
        <StatCard
          title="Placement Applications"
          value={stats?.total_applications ?? 0}
          subtitle={`${stats?.open_opportunities ?? 0} active hiring drives`}
          icon={FileCheck2}
          color="amber"
        />
      </div>

      {isLoading ? (
        <div className="py-20 text-center">
          <div className="mx-auto h-8 w-8 animate-spin rounded-full border-4 border-indigo-600 border-t-transparent mb-3" />
          <p className="text-xs text-slate-500">Aggregating institutional database metrics...</p>
        </div>
      ) : (
        <div className="space-y-8">
          {/* Charts Row */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Status Breakdown Pie Chart */}
            <div className="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-sm">
              <h2 className="text-base font-bold text-slate-900 mb-1">Applications by Hiring Stage</h2>
              <p className="text-xs text-slate-500 mb-4">Current distribution across the candidate pipeline</p>

              {statusPieData.length === 0 || statusPieData.every((d) => d.value === 0) ? (
                <div className="py-16 text-center text-xs text-slate-400">
                  No application activity recorded yet.
                </div>
              ) : (
                <div className="h-64 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={statusPieData}
                        cx="50%"
                        cy="50%"
                        innerRadius={55}
                        outerRadius={85}
                        paddingAngle={4}
                        dataKey="value"
                      >
                        {statusPieData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip
                        contentStyle={{
                          borderRadius: "12px",
                          border: "1px solid #e2e8f0",
                          fontSize: "12px",
                        }}
                      />
                      <Legend wrapperStyle={{ fontSize: "11px", paddingTop: "8px" }} />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              )}
            </div>

            {/* Department Breakdown Bar Chart */}
            <div className="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-sm">
              <h2 className="text-base font-bold text-slate-900 mb-1">Applications by Department</h2>
              <p className="text-xs text-slate-500 mb-4">Student participation count across branches</p>

              {deptBarData.length === 0 ? (
                <div className="py-16 text-center text-xs text-slate-400">
                  No department application data available yet.
                </div>
              ) : (
                <div className="h-64 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={deptBarData} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                      <XAxis dataKey="department" tick={{ fontSize: 10 }} interval={0} stroke="#94a3b8" />
                      <YAxis tick={{ fontSize: 11 }} stroke="#94a3b8" allowDecimals={false} />
                      <Tooltip
                        cursor={{ fill: "transparent" }}
                        contentStyle={{
                          borderRadius: "12px",
                          border: "1px solid #e2e8f0",
                          fontSize: "12px",
                        }}
                      />
                      <Bar dataKey="applications" fill="#6366f1" radius={[6, 6, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              )}
            </div>
          </div>

          {/* Top Companies Table */}
          <div className="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-sm">
            <div className="flex items-center justify-between mb-5">
              <div>
                <h2 className="text-base font-bold text-slate-900">Top Recruiting Partners</h2>
                <p className="text-xs text-slate-500">Companies with the highest hiring requisition volume</p>
              </div>
              <Link
                to="/admin/companies"
                className="text-xs font-semibold text-indigo-600 hover:text-indigo-700"
              >
                View all partners &rarr;
              </Link>
            </div>

            {!stats?.top_companies || stats.top_companies.length === 0 ? (
              <div className="py-10 text-center text-xs text-slate-400">
                No partner companies registered yet.
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr className="border-b border-slate-100 text-slate-400 font-semibold uppercase tracking-wider">
                      <th className="pb-3">Company Name</th>
                      <th className="pb-3">Total Opportunities Posted</th>
                      <th className="pb-3">Total Applications Received</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {stats.top_companies.map((co) => (
                      <tr key={co.company_id} className="hover:bg-slate-50/70 transition-colors">
                        <td className="py-3.5 font-bold text-slate-900 flex items-center gap-2">
                          <Building2 className="h-4 w-4 text-violet-500" />
                          {co.company_name}
                        </td>
                        <td className="py-3.5 text-slate-700 font-semibold">
                          {co.opportunities_count} Drives
                        </td>
                        <td className="py-3.5 text-indigo-600 font-bold">
                          {co.applications_count} Candidates
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}
    </DashboardLayout>
  );
};
