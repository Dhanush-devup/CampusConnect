import React, { useEffect, useState } from "react";
import { AlertCircle, Download, FileCheck2, Filter, Mail } from "lucide-react";
import { adminApi, applicationsApi } from "../../api/endpoints";
import { Application } from "../../api/types";
import { DashboardLayout } from "../../components/DashboardLayout";
import { StatusBadge } from "../../components/StatusBadge";

export const AllApplications: React.FC = () => {
  const [applications, setApplications] = useState<Application[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState("");

  const fetchApplications = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await adminApi.listApplications(statusFilter || undefined);
      setApplications(data);
    } catch (err: any) {
      setError(err.message || "Failed to load applications ledger.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchApplications();
  }, [statusFilter]);

  const handleDownloadResume = async (app: Application) => {
    try {
      await applicationsApi.downloadResume(
        app.application_id,
        `${app.student_name.replace(" ", "_")}_Resume.pdf`
      );
    } catch (err: any) {
      alert(err.message || "Could not retrieve candidate resume.");
    }
  };

  return (
    <DashboardLayout
      title="College-Wide Applications Ledger"
      subtitle="Complete institutional record of student applications, recruitment stages, and hiring outcomes."
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
          { label: "All Applications", value: "" },
          { label: "Applied", value: "applied" },
          { label: "Under Review", value: "under_review" },
          { label: "Shortlisted", value: "shortlisted" },
          { label: "Interview", value: "interview" },
          { label: "Selected", value: "selected" },
          { label: "Rejected", value: "rejected" },
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
          <p className="text-xs text-slate-500">Loading placement ledger...</p>
        </div>
      ) : applications.length === 0 ? (
        <div className="rounded-2xl bg-white border border-dashed border-slate-300 p-12 text-center">
          <FileCheck2 className="mx-auto h-10 w-10 text-slate-300 mb-3" />
          <h3 className="text-sm font-bold text-slate-800">No applications found</h3>
        </div>
      ) : (
        <div className="bg-white rounded-2xl border border-slate-200/80 shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50/80 border-b border-slate-200 text-slate-500 font-bold uppercase tracking-wider">
                <tr>
                  <th className="py-3.5 px-6">Candidate</th>
                  <th className="py-3.5 px-4">Department</th>
                  <th className="py-3.5 px-4">CGPA</th>
                  <th className="py-3.5 px-4">Opportunity</th>
                  <th className="py-3.5 px-4">Employer</th>
                  <th className="py-3.5 px-4">Status</th>
                  <th className="py-3.5 px-6 text-right">Resume</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {applications.map((app) => (
                  <tr key={app.application_id} className="hover:bg-slate-50/70 transition-colors">
                    <td className="py-4 px-6 font-bold text-slate-900">
                      {app.student_name}
                      <p className="font-normal text-slate-400 text-[11px] flex items-center gap-1 mt-0.5">
                        <Mail className="h-3 w-3" />
                        {app.student_email}
                      </p>
                    </td>
                    <td className="py-4 px-4 text-slate-700 font-medium">
                      {app.student_department}
                    </td>
                    <td className="py-4 px-4 font-bold text-emerald-600">
                      {app.student_cgpa.toFixed(2)}
                    </td>
                    <td className="py-4 px-4 font-semibold text-slate-800">
                      {app.opportunity_title}
                    </td>
                    <td className="py-4 px-4 font-semibold text-violet-600">
                      {app.company_name}
                    </td>
                    <td className="py-4 px-4">
                      <StatusBadge status={app.status} size="sm" />
                    </td>
                    <td className="py-4 px-6 text-right">
                      {app.resume_path ? (
                        <button
                          onClick={() => handleDownloadResume(app)}
                          className="inline-flex items-center gap-1 text-xs font-semibold text-indigo-600 hover:text-indigo-800 hover:underline"
                        >
                          <Download className="h-3.5 w-3.5" />
                          View PDF
                        </button>
                      ) : (
                        <span className="text-slate-400 text-[11px]">None</span>
                      )}
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
