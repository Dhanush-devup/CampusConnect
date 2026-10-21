import React, { useEffect, useState } from "react";
import { AlertCircle, Briefcase, Calendar, DollarSign, MapPin, Users } from "lucide-react";
import { adminApi } from "../../api/endpoints";
import { Opportunity } from "../../api/types";
import { DashboardLayout } from "../../components/DashboardLayout";
import { StatusBadge } from "../../components/StatusBadge";

export const AllOpportunities: React.FC = () => {
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState("");

  const fetchOpportunities = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await adminApi.listOpportunities(statusFilter || undefined);
      setOpportunities(data);
    } catch (err: any) {
      setError(err.message || "Failed to load opportunities.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchOpportunities();
  }, [statusFilter]);

  return (
    <DashboardLayout
      title="System-Wide Opportunities Oversight"
      subtitle="Comprehensive view of all job and internship requisitions posted across partner employers."
    >
      {error && (
        <div className="mb-6 rounded-xl bg-rose-50 border border-rose-200 p-4 text-xs text-rose-700 flex items-center gap-2">
          <AlertCircle className="h-4 w-4 shrink-0 text-rose-600" />
          <span>{error}</span>
        </div>
      )}

      {/* Filter Tabs */}
      <div className="mb-6 flex flex-wrap gap-2 border-b border-slate-200 pb-3">
        {[
          { label: "All Drives", value: "" },
          { label: "Open Only", value: "open" },
          { label: "Closed Only", value: "closed" },
          { label: "Drafts Only", value: "draft" },
        ].map((tab) => (
          <button
            key={tab.value}
            onClick={() => setStatusFilter(tab.value)}
            className={`rounded-xl px-3.5 py-1.5 text-xs font-semibold transition-all ${
              statusFilter === tab.value
                ? "bg-slate-900 text-white shadow-xs"
                : "bg-white text-slate-600 hover:bg-slate-100 border border-slate-200"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {isLoading ? (
        <div className="py-20 text-center">
          <div className="mx-auto h-8 w-8 animate-spin rounded-full border-4 border-indigo-600 border-t-transparent mb-3" />
          <p className="text-xs text-slate-500">Loading opportunities...</p>
        </div>
      ) : opportunities.length === 0 ? (
        <div className="rounded-2xl bg-white border border-dashed border-slate-300 p-12 text-center">
          <Briefcase className="mx-auto h-10 w-10 text-slate-300 mb-3" />
          <h3 className="text-sm font-bold text-slate-800">No opportunities in this view</h3>
        </div>
      ) : (
        <div className="bg-white rounded-2xl border border-slate-200/80 shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50/80 border-b border-slate-200 text-slate-500 font-bold uppercase tracking-wider">
                <tr>
                  <th className="py-3.5 px-6">Opportunity & Employer</th>
                  <th className="py-3.5 px-4">Type</th>
                  <th className="py-3.5 px-4">Min CGPA</th>
                  <th className="py-3.5 px-4">Compensation</th>
                  <th className="py-3.5 px-4">Deadline</th>
                  <th className="py-3.5 px-4">Status</th>
                  <th className="py-3.5 px-6 text-right">Applicants</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {opportunities.map((opp) => (
                  <tr key={opp.opportunity_id} className="hover:bg-slate-50/70 transition-colors">
                    <td className="py-4 px-6">
                      <p className="font-bold text-slate-900 text-sm">{opp.title}</p>
                      <p className="text-xs font-semibold text-indigo-600 mt-0.5">{opp.company.company_name}</p>
                    </td>
                    <td className="py-4 px-4">
                      <StatusBadge status={opp.opportunity_type} size="sm" />
                    </td>
                    <td className="py-4 px-4 font-bold text-slate-700">
                      {opp.eligibility_cgpa.toFixed(2)}
                    </td>
                    <td className="py-4 px-4 text-slate-600">
                      ₹{opp.salary_stipend?.toLocaleString() || "Unspecified"}/mo
                    </td>
                    <td className="py-4 px-4 text-slate-500">
                      {new Date(opp.deadline).toLocaleDateString()}
                    </td>
                    <td className="py-4 px-4">
                      <StatusBadge status={opp.status} size="sm" />
                    </td>
                    <td className="py-4 px-6 text-right font-bold text-indigo-600">
                      {opp.application_count ?? 0}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </DashboardLayout>
  );
};
