import React, { useEffect, useState } from "react";
import {
  AlertCircle,
  CheckCircle2,
  Download,
  FileText,
  Filter,
  GraduationCap,
  Mail,
  Search,
  UserCheck,
  Users,
} from "lucide-react";
import { applicationsApi, opportunitiesApi } from "../../api/endpoints";
import { Application, ApplicationStatusType, Opportunity } from "../../api/types";
import { DashboardLayout } from "../../components/DashboardLayout";
import { StatusBadge } from "../../components/StatusBadge";
import { useAuth } from "../../context/AuthContext";

export const ReviewApplications: React.FC = () => {
  const { user } = useAuth();
  const [applications, setApplications] = useState<Application[]>([]);
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  // Filters
  const [selectedOppId, setSelectedOppId] = useState<string>("");
  const [statusFilter, setStatusFilter] = useState<string>("");
  const [departmentFilter, setDepartmentFilter] = useState<string>("");

  const fetchData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [apps, opps] = await Promise.all([
        applicationsApi.listRecruiterApplications({
          opportunity_id: selectedOppId ? parseInt(selectedOppId) : undefined,
          status: statusFilter || undefined,
          department: departmentFilter || undefined,
        }),
        opportunitiesApi.list({ company_id: user?.company_id || undefined }),
      ]);
      setApplications(apps);
      setOpportunities(opps);
    } catch (err: any) {
      setError(err.message || "Failed to load candidate applications.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [selectedOppId, statusFilter, departmentFilter, user]);

  const handleStatusChange = async (appId: number, nextStatus: ApplicationStatusType) => {
    try {
      await applicationsApi.updateStatus(appId, nextStatus);
      setToastMessage(`Candidate stage updated to "${nextStatus.replace('_', ' ')}".`);
      // Update local state smoothly
      setApplications((prev) =>
        prev.map((a) => (a.application_id === appId ? { ...a, status: nextStatus } : a))
      );
    } catch (err: any) {
      alert(err.message || "Failed to update status.");
    }
  };

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
      title="Candidate Review Desk"
      subtitle="Review applicant profiles, inspect resumes, and advance candidates through recruitment stages."
    >
      {toastMessage && (
        <div className="mb-6 rounded-xl bg-emerald-50 border border-emerald-200 p-4 text-xs font-semibold text-emerald-800 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="h-4 w-4 text-emerald-600" />
            <span>{toastMessage}</span>
          </div>
          <button onClick={() => setToastMessage(null)} className="text-emerald-600 hover:underline">
            Dismiss
          </button>
        </div>
      )}

      {error && (
        <div className="mb-6 rounded-xl bg-rose-50 border border-rose-200 p-4 text-xs text-rose-700 flex items-center gap-2">
          <AlertCircle className="h-4 w-4 shrink-0 text-rose-600" />
          <span>{error}</span>
        </div>
      )}

      {/* Filter Toolbar */}
      <div className="bg-white rounded-2xl border border-slate-200/80 p-4 mb-6 shadow-xs flex flex-wrap items-center gap-3">
        <div className="flex items-center gap-1.5 text-xs font-bold text-slate-500 uppercase tracking-wider mr-2">
          <Filter className="h-4 w-4" />
          Filter:
        </div>

        {/* Opportunity filter */}
        <select
          value={selectedOppId}
          onChange={(e) => setSelectedOppId(e.target.value)}
          className="rounded-xl border border-slate-300 px-3 py-2 text-xs text-slate-700 bg-white focus:border-violet-600 focus:outline-none"
        >
          <option value="">All Job Requisitions</option>
          {opportunities.map((o) => (
            <option key={o.opportunity_id} value={o.opportunity_id}>
              {o.title}
            </option>
          ))}
        </select>

        {/* Status filter */}
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="rounded-xl border border-slate-300 px-3 py-2 text-xs text-slate-700 bg-white focus:border-violet-600 focus:outline-none"
        >
          <option value="">All Recruitment Stages</option>
          <option value="applied">Applied (New)</option>
          <option value="under_review">Under Review</option>
          <option value="shortlisted">Shortlisted</option>
          <option value="interview">Interview Scheduled</option>
          <option value="selected">Selected / Offer</option>
          <option value="rejected">Rejected</option>
        </select>

        {/* Department filter */}
        <input
          type="text"
          value={departmentFilter}
          onChange={(e) => setDepartmentFilter(e.target.value)}
          placeholder="Filter by Department..."
          className="rounded-xl border border-slate-300 px-3 py-2 text-xs text-slate-700 placeholder:text-slate-400 focus:border-violet-600 focus:outline-none"
        />

        {(selectedOppId || statusFilter || departmentFilter) && (
          <button
            onClick={() => {
              setSelectedOppId("");
              setStatusFilter("");
              setDepartmentFilter("");
            }}
            className="text-xs font-semibold text-rose-600 hover:underline ml-auto"
          >
            Clear Filters
          </button>
        )}
      </div>

      {/* Candidate List */}
      {isLoading ? (
        <div className="py-20 text-center">
          <div className="mx-auto h-8 w-8 animate-spin rounded-full border-4 border-violet-600 border-t-transparent mb-3" />
          <p className="text-xs text-slate-500">Loading candidates...</p>
        </div>
      ) : applications.length === 0 ? (
        <div className="rounded-2xl bg-white border border-dashed border-slate-300 p-12 text-center">
          <Users className="mx-auto h-10 w-10 text-slate-300 mb-3" />
          <h3 className="text-sm font-bold text-slate-800">No matching applications found</h3>
          <p className="text-xs text-slate-500 mt-1">
            Try adjusting your search filters or check your active job postings.
          </p>
        </div>
      ) : (
        <div className="bg-white rounded-2xl border border-slate-200/80 shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50/80 border-b border-slate-200 text-slate-500 font-bold uppercase tracking-wider">
                <tr>
                  <th className="py-3.5 px-6">Candidate Details</th>
                  <th className="py-3.5 px-4">Academic Info</th>
                  <th className="py-3.5 px-4">Target Job</th>
                  <th className="py-3.5 px-4">Current Stage</th>
                  <th className="py-3.5 px-4">Resume</th>
                  <th className="py-3.5 px-6 text-right">Update Hiring Stage</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {applications.map((app) => (
                  <tr key={app.application_id} className="hover:bg-slate-50/70 transition-colors">
                    {/* Candidate */}
                    <td className="py-4 px-6">
                      <p className="font-bold text-slate-900 text-sm">{app.student_name}</p>
                      <p className="text-slate-400 text-xs flex items-center gap-1 mt-0.5">
                        <Mail className="h-3 w-3" />
                        {app.student_email}
                      </p>
                    </td>

                    {/* Academic */}
                    <td className="py-4 px-4">
                      <p className="font-semibold text-slate-800">{app.student_department}</p>
                      <p className="text-xs mt-0.5">
                        CGPA:{" "}
                        <span className="font-bold text-emerald-600 bg-emerald-50 px-1.5 py-0.5 rounded">
                          {app.student_cgpa.toFixed(2)}
                        </span>
                        <span className="text-slate-400 ml-1.5">({app.student_graduation_year})</span>
                      </p>
                    </td>

                    {/* Target Job */}
                    <td className="py-4 px-4">
                      <p className="font-bold text-slate-800">{app.opportunity_title}</p>
                      <p className="text-slate-400 text-[11px] capitalize">{app.opportunity_type.replace('_', ' ')}</p>
                    </td>

                    {/* Status Badge */}
                    <td className="py-4 px-4">
                      <StatusBadge status={app.status} size="sm" />
                    </td>

                    {/* Resume */}
                    <td className="py-4 px-4">
                      {app.resume_path ? (
                        <button
                          onClick={() => handleDownloadResume(app)}
                          className="inline-flex items-center gap-1 text-xs font-semibold text-violet-600 hover:text-violet-800 hover:underline"
                        >
                          <Download className="h-3.5 w-3.5" />
                          PDF Resume
                        </button>
                      ) : (
                        <span className="text-slate-400 text-[11px]">Not uploaded</span>
                      )}
                    </td>

                    {/* Action Selector */}
                    <td className="py-4 px-6 text-right">
                      <select
                        value={app.status}
                        onChange={(e) => handleStatusChange(app.application_id, e.target.value as ApplicationStatusType)}
                        className="rounded-xl border border-slate-300 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 shadow-xs focus:border-violet-600 focus:outline-none"
                      >
                        <option value="applied">Mark as Applied</option>
                        <option value="under_review">Mark Under Review</option>
                        <option value="shortlisted">Shortlist Candidate</option>
                        <option value="interview">Schedule Interview</option>
                        <option value="selected">Select / Offer</option>
                        <option value="rejected">Reject</option>
                      </select>
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
