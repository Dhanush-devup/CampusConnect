import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  AlertCircle,
  Briefcase,
  Calendar,
  CheckCircle2,
  Clock,
  Download,
  FileCheck2,
  FileText,
  MapPin,
  Upload,
} from "lucide-react";
import { applicationsApi } from "../../api/endpoints";
import { Application, ApplicationStatusType } from "../../api/types";
import { AtsReportModal, AtsScoreBadge } from "../../components/AtsScore";
import { usePendingScoreRefresh } from "../../hooks/usePendingScoreRefresh";
import { DashboardLayout } from "../../components/DashboardLayout";
import { Modal } from "../../components/Modal";
import { StatusBadge } from "../../components/StatusBadge";

export const MyApplications: React.FC = () => {
  const [applications, setApplications] = useState<Application[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState("");

  // Resume replace modal
  const [replacingApp, setReplacingApp] = useState<Application | null>(null);
  const [newResumeFile, setNewResumeFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [successToast, setSuccessToast] = useState<string | null>(null);
  const [atsReportApp, setAtsReportApp] = useState<Application | null>(null);

  // silent: refresh in place (e.g. while ATS scores are pending) without the loading spinner
  const fetchApplications = async ({ silent = false } = {}) => {
    if (!silent) setIsLoading(true);
    setError(null);
    try {
      const data = await applicationsApi.listStudentApplications();
      setApplications(data);
    } catch (err: any) {
      setError(err.message || "Failed to load applications.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchApplications();
  }, []);

  usePendingScoreRefresh(applications, () => fetchApplications({ silent: true }));

  const handleDownloadResume = async (app: Application) => {
    try {
      await applicationsApi.downloadResume(app.application_id, `${app.opportunity_title}_Resume.pdf`);
    } catch (err: any) {
      alert(err.message || "Could not download resume.");
    }
  };

  const handleReplaceResume = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!replacingApp || !newResumeFile) return;

    setIsUploading(true);
    setUploadError(null);
    try {
      await applicationsApi.uploadResume(replacingApp.application_id, newResumeFile);
      setSuccessToast("Resume updated! Your ATS score will appear within about 30 seconds.");
      setReplacingApp(null);
      setNewResumeFile(null);
      fetchApplications();
    } catch (err: any) {
      setUploadError(err.message || "Failed to upload resume.");
    } finally {
      setIsUploading(false);
    }
  };

  const filteredApps = statusFilter
    ? applications.filter((app) => app.status === statusFilter)
    : applications;

  const stages: ApplicationStatusType[] = [
    "applied",
    "under_review",
    "shortlisted",
    "interview",
    "selected",
  ];

  const getStageIndex = (status: ApplicationStatusType) => {
    if (status === "rejected") return -1;
    return stages.indexOf(status);
  };

  return (
    <DashboardLayout
      title="My Placement Applications"
      subtitle="Track the recruitment status and review milestones for all your submitted applications."
      actions={
        <Link
          to="/student/opportunities"
          className="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-4 py-2.5 text-xs font-semibold text-white shadow-sm hover:bg-indigo-500 transition-all"
        >
          <Briefcase className="h-4 w-4" />
          Apply to More Drives
        </Link>
      }
    >
      {/* Toast Notification */}
      {successToast && (
        <div className="mb-6 rounded-xl bg-emerald-50 border border-emerald-200 p-4 text-xs font-semibold text-emerald-800 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="h-4 w-4 text-emerald-600" />
            <span>{successToast}</span>
          </div>
          <button onClick={() => setSuccessToast(null)} className="text-emerald-600 hover:underline">
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

      {/* Applications List */}
      {isLoading ? (
        <div className="py-20 text-center">
          <div className="mx-auto h-8 w-8 animate-spin rounded-full border-4 border-indigo-600 border-t-transparent mb-3" />
          <p className="text-xs text-slate-500">Loading your applications...</p>
        </div>
      ) : filteredApps.length === 0 ? (
        <div className="rounded-2xl bg-white border border-dashed border-slate-300 p-12 text-center">
          <FileCheck2 className="mx-auto h-10 w-10 text-slate-300 mb-3" />
          <h3 className="text-sm font-bold text-slate-800">No applications in this category</h3>
          <p className="text-xs text-slate-500 mt-1">
            Browse open opportunities and submit your candidacy.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredApps.map((app) => {
            const currentStageIndex = getStageIndex(app.status);
            const isRejected = app.status === "rejected";

            return (
              <div
                key={app.application_id}
                className="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-sm hover:border-slate-300 transition-all"
              >
                <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-4">
                  <div>
                    <div className="flex items-center gap-2 mb-1.5">
                      <span className="text-base font-bold text-slate-900">{app.opportunity_title}</span>
                      <StatusBadge status={app.status} size="sm" />
                    </div>
                    <p className="text-xs font-semibold text-indigo-600">{app.company_name}</p>
                  </div>

                  <div className="flex items-center gap-2 text-xs text-slate-500">
                    <Calendar className="h-4 w-4 text-slate-400" />
                    <span>Applied on {new Date(app.application_date).toLocaleDateString()}</span>
                  </div>
                </div>

                {/* Progress Step Funnel */}
                <div className="my-5 rounded-xl bg-slate-50/80 p-4 border border-slate-100">
                  <p className="text-[11px] font-bold uppercase tracking-wider text-slate-400 mb-3">
                    Application Pipeline
                  </p>
                  {isRejected ? (
                    <div className="rounded-lg bg-rose-50 border border-rose-200 p-3 text-xs text-rose-700 flex items-center gap-2">
                      <AlertCircle className="h-4 w-4 shrink-0 text-rose-600" />
                      <span>This application was not selected to proceed further.</span>
                    </div>
                  ) : (
                    <div className="grid grid-cols-5 gap-2 text-center">
                      {stages.map((stageName, idx) => {
                        const isCompleted = currentStageIndex >= idx;
                        const isCurrent = currentStageIndex === idx;

                        return (
                          <div key={stageName} className="flex flex-col items-center">
                            <div
                              className={`w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold mb-1 transition-all ${
                                isCompleted
                                  ? "bg-indigo-600 text-white"
                                  : "bg-slate-200 text-slate-500"
                              } ${isCurrent ? "ring-4 ring-indigo-100 scale-110" : ""}`}
                            >
                              {idx + 1}
                            </div>
                            <span
                              className={`text-[10px] font-semibold capitalize ${
                                isCompleted ? "text-indigo-900" : "text-slate-400"
                              }`}
                            >
                              {stageName.replace("_", " ")}
                            </span>
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>

                {/* Resume Actions Footer */}
                <div className="flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-slate-100 text-xs">
                  <div className="flex items-center gap-2">
                    <FileText className="h-4 w-4 text-slate-400" />
                    {app.resume_path ? (
                      <>
                        <span className="text-slate-600 font-medium">Resume attached on file</span>
                        <AtsScoreBadge app={app} onClick={() => setAtsReportApp(app)} />
                      </>
                    ) : (
                      <span className="text-amber-600 font-medium">No resume attached</span>
                    )}
                  </div>

                  <div className="flex items-center gap-2">
                    {app.resume_path && (
                      <button
                        onClick={() => handleDownloadResume(app)}
                        className="inline-flex items-center gap-1.5 rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-50 transition-colors"
                      >
                        <Download className="h-3.5 w-3.5 text-slate-500" />
                        Download
                      </button>
                    )}
                    <button
                      onClick={() => {
                        setReplacingApp(app);
                        setUploadError(null);
                        setNewResumeFile(null);
                      }}
                      className="inline-flex items-center gap-1.5 rounded-lg border border-indigo-200 bg-indigo-50 px-3 py-1.5 text-xs font-semibold text-indigo-700 hover:bg-indigo-100 transition-colors"
                    >
                      <Upload className="h-3.5 w-3.5 text-indigo-600" />
                      {app.resume_path ? "Replace Resume" : "Upload Resume"}
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      <AtsReportModal
        key={atsReportApp?.application_id ?? "closed"}
        app={atsReportApp}
        viewer="student"
        onClose={() => setAtsReportApp(null)}
        onScoreChange={() => fetchApplications({ silent: true })}
      />

      {/* Replace Resume Modal */}
      {replacingApp && (
        <Modal
          isOpen={true}
          onClose={() => setReplacingApp(null)}
          title="Upload or Replace Resume"
          subtitle={`For application: ${replacingApp.opportunity_title}`}
        >
          {uploadError && (
            <div className="mb-4 rounded-xl bg-rose-50 border border-rose-200 p-3 text-xs text-rose-700 flex items-center gap-2">
              <AlertCircle className="h-4 w-4 shrink-0 text-rose-600" />
              <span>{uploadError}</span>
            </div>
          )}

          <form onSubmit={handleReplaceResume} className="space-y-4">
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                Select PDF Resume (Max 5MB)
              </label>
              <div className="rounded-xl border-2 border-dashed border-slate-300 p-6 text-center hover:border-indigo-400 transition-colors">
                <Upload className="mx-auto h-8 w-8 text-slate-400 mb-2" />
                <p className="text-xs text-slate-600 mb-2">
                  {newResumeFile ? (
                    <span className="font-semibold text-indigo-600">
                      {newResumeFile.name} ({(newResumeFile.size / 1024).toFixed(0)} KB)
                    </span>
                  ) : (
                    "Upload PDF document"
                  )}
                </p>
                <input
                  type="file"
                  required
                  accept=".pdf,application/pdf"
                  onChange={(e) => setNewResumeFile(e.target.files?.[0] || null)}
                  className="text-xs text-slate-500 file:mr-2 file:py-1.5 file:px-3 file:rounded-md file:border-0 file:text-xs file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
                />
              </div>
            </div>

            <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-100">
              <button
                type="button"
                onClick={() => setReplacingApp(null)}
                className="rounded-xl border border-slate-300 px-4 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isUploading || !newResumeFile}
                className="rounded-xl bg-indigo-600 px-5 py-2 text-xs font-semibold text-white shadow-sm hover:bg-indigo-500 disabled:opacity-50"
              >
                {isUploading ? "Uploading..." : "Save Resume"}
              </button>
            </div>
          </form>
        </Modal>
      )}
    </DashboardLayout>
  );
};
