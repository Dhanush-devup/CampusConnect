import React, { useEffect, useState } from "react";
import {
  AlertCircle,
  Briefcase,
  Calendar,
  CheckCircle2,
  DollarSign,
  FileCheck2,
  Filter,
  MapPin,
  Search,
  Upload,
  XCircle,
} from "lucide-react";
import { applicationsApi, opportunitiesApi } from "../../api/endpoints";
import { Opportunity } from "../../api/types";
import { DashboardLayout } from "../../components/DashboardLayout";
import { Modal } from "../../components/Modal";
import { StatusBadge } from "../../components/StatusBadge";
import { useAuth } from "../../context/AuthContext";

export const OpportunitiesExplore: React.FC = () => {
  const { user } = useAuth();
  const student = user?.student_profile;

  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Filters
  const [search, setSearch] = useState("");
  const [typeFilter, setTypeFilter] = useState("");
  const [eligibleOnly, setEligibleOnly] = useState(false);

  // Apply Modal state
  const [selectedOpp, setSelectedOpp] = useState<Opportunity | null>(null);
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [isApplying, setIsApplying] = useState(false);
  const [applyError, setApplyError] = useState<string | null>(null);

  const fetchOpportunities = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await opportunitiesApi.list({
        search: search.trim() || undefined,
        opportunity_type: typeFilter || undefined,
        eligible_only: eligibleOnly,
        status: "open",
      });
      setOpportunities(data);
    } catch (err: any) {
      setError(err.message || "Failed to load opportunities.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchOpportunities();
  }, [typeFilter, eligibleOnly]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchOpportunities();
  };

  const handleApplySubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedOpp) return;

    setIsApplying(true);
    setApplyError(null);

    try {
      await applicationsApi.apply(selectedOpp.opportunity_id, resumeFile || undefined);
      setSuccessMessage(`Successfully applied to ${selectedOpp.title} at ${selectedOpp.company.company_name}!`);
      setSelectedOpp(null);
      setResumeFile(null);
      // Refresh list to show "Applied" status
      fetchOpportunities();
    } catch (err: any) {
      setApplyError(err.message || "Failed to submit application.");
    } finally {
      setIsApplying(false);
    }
  };

  return (
    <DashboardLayout
      title="Explore Campus Opportunities"
      subtitle="Browse open internship and full-time hiring drives from partner companies."
    >
      {/* Notifications */}
      {successMessage && (
        <div className="mb-6 rounded-xl bg-emerald-50 border border-emerald-200 p-4 text-xs font-semibold text-emerald-800 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="h-4 w-4 text-emerald-600" />
            <span>{successMessage}</span>
          </div>
          <button onClick={() => setSuccessMessage(null)} className="text-emerald-600 hover:underline">
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
      <div className="bg-white rounded-2xl border border-slate-200/80 p-4 mb-8 shadow-xs">
        <form onSubmit={handleSearchSubmit} className="flex flex-col md:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="absolute left-3.5 top-3 h-4 w-4 text-slate-400" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search by role, company name, or keywords..."
              className="w-full rounded-xl border border-slate-300 pl-10 pr-3.5 py-2.5 text-xs text-slate-900 placeholder:text-slate-400 focus:border-indigo-600 focus:outline-none focus:ring-1 focus:ring-indigo-600"
            />
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              className="rounded-xl border border-slate-300 px-3 py-2.5 text-xs text-slate-700 bg-white focus:border-indigo-600 focus:outline-none"
            >
              <option value="">All Opportunity Types</option>
              <option value="internship">Internship</option>
              <option value="full_time">Full Time</option>
              <option value="part_time">Part Time</option>
            </select>

            <button
              type="button"
              onClick={() => setEligibleOnly(!eligibleOnly)}
              className={`inline-flex items-center gap-1.5 rounded-xl border px-3 py-2.5 text-xs font-semibold transition-colors ${
                eligibleOnly
                  ? "bg-indigo-600 text-white border-indigo-600"
                  : "bg-white text-slate-700 border-slate-300 hover:bg-slate-50"
              }`}
            >
              <Filter className="h-3.5 w-3.5" />
              Eligible for my CGPA ({student?.cgpa.toFixed(2) || "0.00"})
            </button>

            <button
              type="submit"
              className="rounded-xl bg-slate-900 text-white px-4 py-2.5 text-xs font-semibold hover:bg-slate-800 transition-colors"
            >
              Search
            </button>
          </div>
        </form>
      </div>

      {/* Opportunities Grid */}
      {isLoading ? (
        <div className="py-20 text-center">
          <div className="mx-auto h-8 w-8 animate-spin rounded-full border-4 border-indigo-600 border-t-transparent mb-3" />
          <p className="text-xs text-slate-500">Searching active campus opportunities...</p>
        </div>
      ) : opportunities.length === 0 ? (
        <div className="rounded-2xl bg-white border border-dashed border-slate-300 p-12 text-center">
          <Briefcase className="mx-auto h-10 w-10 text-slate-300 mb-3" />
          <h3 className="text-sm font-bold text-slate-800">No opportunities found</h3>
          <p className="text-xs text-slate-500 mt-1">Try adjusting your filters or search keywords.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {opportunities.map((opp) => {
            const hasApplied = opp.has_applied;
            const meetsCgpa = student ? student.cgpa >= opp.eligibility_cgpa : false;
            const isDeadlinePassed = new Date(opp.deadline) < new Date();

            return (
              <div
                key={opp.opportunity_id}
                className="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-sm hover:shadow-md transition-all flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-start justify-between gap-2 mb-3">
                    <StatusBadge status={opp.opportunity_type} size="sm" />
                    {hasApplied ? (
                      <span className="inline-flex items-center gap-1 rounded-full bg-emerald-50 px-2.5 py-0.5 text-xs font-bold text-emerald-700 border border-emerald-200">
                        <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600" />
                        Applied
                      </span>
                    ) : !meetsCgpa ? (
                      <span className="inline-flex items-center gap-1 rounded-full bg-rose-50 px-2.5 py-0.5 text-xs font-semibold text-rose-700 border border-rose-200">
                        <XCircle className="h-3.5 w-3.5 text-rose-500" />
                        Req. CGPA {opp.eligibility_cgpa.toFixed(2)}
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 rounded-full bg-indigo-50 px-2.5 py-0.5 text-xs font-semibold text-indigo-700 border border-indigo-200">
                        Eligible
                      </span>
                    )}
                  </div>

                  <h3 className="text-lg font-bold text-slate-900 mb-1">{opp.title}</h3>
                  <p className="text-xs font-semibold text-indigo-600 mb-3">{opp.company.company_name}</p>

                  <p className="text-xs text-slate-600 line-clamp-3 mb-4 leading-relaxed">
                    {opp.description}
                  </p>

                  <div className="space-y-1.5 text-xs text-slate-500 border-t border-slate-100 pt-3">
                    {opp.location && (
                      <div className="flex items-center gap-2">
                        <MapPin className="h-3.5 w-3.5 text-slate-400" />
                        <span>{opp.location}</span>
                      </div>
                    )}
                    {opp.salary_stipend && (
                      <div className="flex items-center gap-2">
                        <DollarSign className="h-3.5 w-3.5 text-slate-400" />
                        <span>Compensation: ₹{opp.salary_stipend.toLocaleString()}/mo</span>
                      </div>
                    )}
                    <div className="flex items-center gap-2">
                      <Calendar className="h-3.5 w-3.5 text-slate-400" />
                      <span>Deadline: {new Date(opp.deadline).toLocaleDateString()}</span>
                    </div>
                  </div>
                </div>

                <div className="mt-6 pt-4 border-t border-slate-100 flex items-center justify-between">
                  <span className="text-[11px] text-slate-400">
                    Min CGPA: <strong className="text-slate-700">{opp.eligibility_cgpa.toFixed(2)}</strong>
                  </span>

                  {hasApplied ? (
                    <button
                      disabled
                      className="rounded-xl bg-slate-100 px-4 py-2 text-xs font-semibold text-slate-400 cursor-not-allowed"
                    >
                      Already Applied
                    </button>
                  ) : !meetsCgpa ? (
                    <button
                      disabled
                      className="rounded-xl bg-slate-100 px-4 py-2 text-xs font-semibold text-slate-400 cursor-not-allowed"
                      title="Your CGPA is below the minimum required for this opportunity"
                    >
                      Ineligible
                    </button>
                  ) : isDeadlinePassed ? (
                    <button
                      disabled
                      className="rounded-xl bg-slate-100 px-4 py-2 text-xs font-semibold text-slate-400 cursor-not-allowed"
                    >
                      Expired
                    </button>
                  ) : (
                    <button
                      onClick={() => {
                        setSelectedOpp(opp);
                        setApplyError(null);
                        setResumeFile(null);
                      }}
                      className="rounded-xl bg-indigo-600 px-4 py-2 text-xs font-semibold text-white shadow-sm hover:bg-indigo-500 transition-colors"
                    >
                      Apply Now
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Apply Modal */}
      {selectedOpp && (
        <Modal
          isOpen={true}
          onClose={() => setSelectedOpp(null)}
          title={`Apply for ${selectedOpp.title}`}
          subtitle={`${selectedOpp.company.company_name} • ${selectedOpp.opportunity_type}`}
        >
          {applyError && (
            <div className="mb-4 rounded-xl bg-rose-50 border border-rose-200 p-3 text-xs text-rose-700 flex items-center gap-2">
              <AlertCircle className="h-4 w-4 shrink-0 text-rose-600" />
              <span>{applyError}</span>
            </div>
          )}

          <div className="mb-5 bg-slate-50 rounded-xl p-4 border border-slate-200/80 text-xs space-y-2">
            <div className="flex justify-between">
              <span className="text-slate-500">Applicant:</span>
              <span className="font-semibold text-slate-800">{user?.name} ({user?.email})</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Your CGPA:</span>
              <span className="font-semibold text-emerald-600">{student?.cgpa.toFixed(2)} (Req: {selectedOpp.eligibility_cgpa.toFixed(2)})</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Deadline:</span>
              <span className="font-semibold text-slate-800">{new Date(selectedOpp.deadline).toLocaleDateString()}</span>
            </div>
          </div>

          <form onSubmit={handleApplySubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                Attach Resume (Optional PDF, Max 5MB)
              </label>
              <div className="rounded-xl border-2 border-dashed border-slate-300 p-4 text-center hover:border-indigo-400 transition-colors">
                <Upload className="mx-auto h-6 w-6 text-slate-400 mb-1" />
                <p className="text-xs text-slate-600 mb-1">
                  {resumeFile ? (
                    <span className="font-semibold text-indigo-600">{resumeFile.name} ({(resumeFile.size / 1024).toFixed(0)} KB)</span>
                  ) : (
                    "Upload your latest PDF resume"
                  )}
                </p>
                <input
                  type="file"
                  accept=".pdf,application/pdf"
                  onChange={(e) => setResumeFile(e.target.files?.[0] || null)}
                  className="text-xs text-slate-500 file:mr-2 file:py-1 file:px-2.5 file:rounded-md file:border-0 file:text-xs file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
                />
              </div>
            </div>

            <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-100">
              <button
                type="button"
                onClick={() => setSelectedOpp(null)}
                className="rounded-xl border border-slate-300 px-4 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isApplying}
                className="rounded-xl bg-indigo-600 px-5 py-2 text-xs font-semibold text-white shadow-sm hover:bg-indigo-500 disabled:opacity-50"
              >
                {isApplying ? "Submitting..." : "Confirm & Submit Application"}
              </button>
            </div>
          </form>
        </Modal>
      )}
    </DashboardLayout>
  );
};
