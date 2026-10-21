import React, { useEffect, useState } from "react";
import {
  AlertCircle,
  Briefcase,
  Calendar,
  CheckCircle2,
  DollarSign,
  Edit2,
  MapPin,
  Plus,
  Power,
  Users,
} from "lucide-react";
import { opportunitiesApi } from "../../api/endpoints";
import { Opportunity, OpportunityStatusType, OpportunityType } from "../../api/types";
import { DashboardLayout } from "../../components/DashboardLayout";
import { Modal } from "../../components/Modal";
import { StatusBadge } from "../../components/StatusBadge";
import { useAuth } from "../../context/AuthContext";

export const ManageOpportunities: React.FC = () => {
  const { user } = useAuth();
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Modal states
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingOpp, setEditingOpp] = useState<Opportunity | null>(null);
  const [formSubmitting, setFormSubmitting] = useState(false);
  const [modalError, setModalError] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    title: "",
    opportunity_type: "internship" as OpportunityType,
    description: "",
    location: "Bangalore, India",
    salary_stipend: "35000",
    deadline: "",
    eligibility_cgpa: "7.00",
    status: "open" as OpportunityStatusType,
  });

  const fetchCompanyOpportunities = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await opportunitiesApi.list({
        company_id: user?.company_id || undefined,
      });
      setOpportunities(data);
    } catch (err: any) {
      setError(err.message || "Failed to load company opportunities.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchCompanyOpportunities();
  }, [user]);

  const openCreateModal = () => {
    setEditingOpp(null);
    const futureDate = new Date();
    futureDate.setDate(futureDate.getDate() + 30);
    setFormData({
      title: "",
      opportunity_type: "internship",
      description: "",
      location: "Bangalore, India",
      salary_stipend: "35000",
      deadline: futureDate.toISOString().slice(0, 16),
      eligibility_cgpa: "7.00",
      status: "open",
    });
    setModalError(null);
    setIsModalOpen(true);
  };

  const openEditModal = (opp: Opportunity) => {
    setEditingOpp(opp);
    setFormData({
      title: opp.title,
      opportunity_type: opp.opportunity_type,
      description: opp.description,
      location: opp.location || "",
      salary_stipend: opp.salary_stipend?.toString() || "",
      deadline: new Date(opp.deadline).toISOString().slice(0, 16),
      eligibility_cgpa: opp.eligibility_cgpa.toString(),
      status: opp.status,
    });
    setModalError(null);
    setIsModalOpen(true);
  };

  const handleFormSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setModalError(null);

    const cgpaFloat = parseFloat(formData.eligibility_cgpa);
    if (isNaN(cgpaFloat) || cgpaFloat < 0 || cgpaFloat > 10) {
      setModalError("Eligibility CGPA must be between 0.00 and 10.00.");
      return;
    }

    const stipendFloat = formData.salary_stipend ? parseFloat(formData.salary_stipend) : undefined;
    if (stipendFloat !== undefined && stipendFloat < 0) {
      setModalError("Salary/Stipend cannot be negative.");
      return;
    }

    const deadlineDate = new Date(formData.deadline);
    if (isNaN(deadlineDate.getTime()) || deadlineDate <= new Date()) {
      setModalError("Deadline must be a future date and time.");
      return;
    }

    setFormSubmitting(true);
    try {
      if (editingOpp) {
        await opportunitiesApi.update(editingOpp.opportunity_id, {
          title: formData.title.trim(),
          opportunity_type: formData.opportunity_type,
          description: formData.description.trim(),
          location: formData.location.trim() || undefined,
          salary_stipend: stipendFloat,
          deadline: deadlineDate.toISOString(),
          eligibility_cgpa: cgpaFloat,
          status: formData.status,
        });
        setSuccess("Opportunity updated successfully.");
      } else {
        await opportunitiesApi.create({
          title: formData.title.trim(),
          opportunity_type: formData.opportunity_type,
          description: formData.description.trim(),
          location: formData.location.trim() || undefined,
          salary_stipend: stipendFloat,
          deadline: deadlineDate.toISOString(),
          eligibility_cgpa: cgpaFloat,
          status: formData.status,
        });
        setSuccess("New opportunity drive published successfully.");
      }

      setIsModalOpen(false);
      fetchCompanyOpportunities();
    } catch (err: any) {
      setModalError(err.message || "Failed to save opportunity.");
    } finally {
      setFormSubmitting(false);
    }
  };

  const handleToggleStatus = async (opp: Opportunity) => {
    const nextStatus: OpportunityStatusType = opp.status === "open" ? "closed" : "open";
    try {
      await opportunitiesApi.updateStatus(opp.opportunity_id, nextStatus);
      setSuccess(`Opportunity status changed to ${nextStatus}.`);
      fetchCompanyOpportunities();
    } catch (err: any) {
      setError(err.message || "Failed to update status.");
    }
  };

  return (
    <DashboardLayout
      title="Company Hiring Drives"
      subtitle="Create and manage job and internship postings for your organization."
      actions={
        <button
          onClick={openCreateModal}
          className="inline-flex items-center gap-2 rounded-xl bg-violet-600 px-4 py-2.5 text-xs font-semibold text-white shadow-sm hover:bg-violet-500 transition-all"
        >
          <Plus className="h-4 w-4" />
          Post New Opportunity
        </button>
      }
    >
      {success && (
        <div className="mb-6 rounded-xl bg-emerald-50 border border-emerald-200 p-4 text-xs font-semibold text-emerald-800 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="h-4 w-4 text-emerald-600" />
            <span>{success}</span>
          </div>
          <button onClick={() => setSuccess(null)} className="text-emerald-600 hover:underline">
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

      {isLoading ? (
        <div className="py-20 text-center">
          <div className="mx-auto h-8 w-8 animate-spin rounded-full border-4 border-violet-600 border-t-transparent mb-3" />
          <p className="text-xs text-slate-500">Loading your company's opportunities...</p>
        </div>
      ) : opportunities.length === 0 ? (
        <div className="rounded-2xl bg-white border border-dashed border-slate-300 p-12 text-center">
          <Briefcase className="mx-auto h-10 w-10 text-slate-300 mb-3" />
          <h3 className="text-sm font-bold text-slate-800">No opportunities posted yet</h3>
          <p className="text-xs text-slate-500 mt-1">
            Click "Post New Opportunity" above to publish your first hiring requisition.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {opportunities.map((opp) => (
            <div
              key={opp.opportunity_id}
              className="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-sm hover:border-slate-300 transition-all"
            >
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div>
                  <div className="flex items-center gap-2.5 mb-1.5">
                    <span className="text-base font-bold text-slate-900">{opp.title}</span>
                    <StatusBadge status={opp.status} size="sm" />
                    <StatusBadge status={opp.opportunity_type} size="sm" />
                  </div>
                  <p className="text-xs text-slate-600 line-clamp-2 max-w-3xl leading-relaxed">
                    {opp.description}
                  </p>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => openEditModal(opp)}
                    className="inline-flex items-center gap-1.5 rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-50 transition-colors"
                  >
                    <Edit2 className="h-3.5 w-3.5 text-slate-500" />
                    Edit
                  </button>

                  <button
                    onClick={() => handleToggleStatus(opp)}
                    className={`inline-flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-xs font-semibold transition-colors ${
                      opp.status === "open"
                        ? "border-amber-200 bg-amber-50 text-amber-700 hover:bg-amber-100"
                        : "border-emerald-200 bg-emerald-50 text-emerald-700 hover:bg-emerald-100"
                    }`}
                  >
                    <Power className="h-3.5 w-3.5" />
                    {opp.status === "open" ? "Close Drive" : "Reopen Drive"}
                  </button>
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-100 flex flex-wrap items-center gap-4 text-xs text-slate-500">
                <div className="flex items-center gap-1.5">
                  <MapPin className="h-3.5 w-3.5 text-slate-400" />
                  <span>{opp.location || "Remote"}</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <DollarSign className="h-3.5 w-3.5 text-slate-400" />
                  <span>₹{opp.salary_stipend?.toLocaleString() || "Unspecified"} / mo</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <Calendar className="h-3.5 w-3.5 text-slate-400" />
                  <span>Deadline: {new Date(opp.deadline).toLocaleDateString()}</span>
                </div>
                <div className="flex items-center gap-1.5 text-indigo-600 font-medium">
                  <span>Min CGPA: {opp.eligibility_cgpa.toFixed(2)}</span>
                </div>
                <div className="flex items-center gap-1.5 text-violet-600 font-medium ml-auto">
                  <Users className="h-3.5 w-3.5" />
                  <span>{opp.application_count ?? 0} Applications Received</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Post / Edit Opportunity Modal */}
      {isModalOpen && (
        <Modal
          isOpen={true}
          onClose={() => setIsModalOpen(false)}
          title={editingOpp ? "Edit Opportunity" : "Post New Opportunity"}
          subtitle="Define eligibility criteria, description, and application deadline"
          maxWidth="xl"
        >
          {modalError && (
            <div className="mb-4 rounded-xl bg-rose-50 border border-rose-200 p-3 text-xs text-rose-700 flex items-center gap-2">
              <AlertCircle className="h-4 w-4 shrink-0 text-rose-600" />
              <span>{modalError}</span>
            </div>
          )}

          <form onSubmit={handleFormSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                Job / Internship Title
              </label>
              <input
                type="text"
                required
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                placeholder="Software Engineering Intern"
                className="w-full rounded-xl border border-slate-300 px-3.5 py-2 text-sm text-slate-900 focus:border-violet-600 focus:outline-none focus:ring-1 focus:ring-violet-600"
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                  Opportunity Type
                </label>
                <select
                  value={formData.opportunity_type}
                  onChange={(e) => setFormData({ ...formData, opportunity_type: e.target.value as OpportunityType })}
                  className="w-full rounded-xl border border-slate-300 px-3.5 py-2 text-sm text-slate-900 bg-white focus:border-violet-600 focus:outline-none"
                >
                  <option value="internship">Internship</option>
                  <option value="full_time">Full Time</option>
                  <option value="part_time">Part Time</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                  Drive Status
                </label>
                <select
                  value={formData.status}
                  onChange={(e) => setFormData({ ...formData, status: e.target.value as OpportunityStatusType })}
                  className="w-full rounded-xl border border-slate-300 px-3.5 py-2 text-sm text-slate-900 bg-white focus:border-violet-600 focus:outline-none"
                >
                  <option value="open">Open (Accepting Applications)</option>
                  <option value="draft">Draft (Hidden from Students)</option>
                  <option value="closed">Closed</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                Description & Requirements
              </label>
              <textarea
                rows={4}
                required
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Describe role responsibilities, required skills, and interview process..."
                className="w-full rounded-xl border border-slate-300 px-3.5 py-2 text-sm text-slate-900 focus:border-violet-600 focus:outline-none focus:ring-1 focus:ring-violet-600"
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                  Location
                </label>
                <input
                  type="text"
                  value={formData.location}
                  onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                  placeholder="Bangalore, Remote"
                  className="w-full rounded-xl border border-slate-300 px-3.5 py-2 text-sm text-slate-900 focus:border-violet-600 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                  Monthly Stipend / CTC (₹)
                </label>
                <input
                  type="number"
                  min="0"
                  value={formData.salary_stipend}
                  onChange={(e) => setFormData({ ...formData, salary_stipend: e.target.value })}
                  placeholder="35000"
                  className="w-full rounded-xl border border-slate-300 px-3.5 py-2 text-sm text-slate-900 focus:border-violet-600 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                  Min CGPA (0 - 10)
                </label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  max="10"
                  required
                  value={formData.eligibility_cgpa}
                  onChange={(e) => setFormData({ ...formData, eligibility_cgpa: e.target.value })}
                  className="w-full rounded-xl border border-slate-300 px-3.5 py-2 text-sm text-slate-900 focus:border-violet-600 focus:outline-none"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                Application Deadline
              </label>
              <input
                type="datetime-local"
                required
                value={formData.deadline}
                onChange={(e) => setFormData({ ...formData, deadline: e.target.value })}
                className="w-full rounded-xl border border-slate-300 px-3.5 py-2 text-sm text-slate-900 focus:border-violet-600 focus:outline-none"
              />
            </div>

            <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-100">
              <button
                type="button"
                onClick={() => setIsModalOpen(false)}
                className="rounded-xl border border-slate-300 px-4 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={formSubmitting}
                className="rounded-xl bg-violet-600 px-5 py-2 text-xs font-semibold text-white shadow-sm hover:bg-violet-500 disabled:opacity-50"
              >
                {formSubmitting ? "Saving..." : editingOpp ? "Save Changes" : "Publish Opportunity"}
              </button>
            </div>
          </form>
        </Modal>
      )}
    </DashboardLayout>
  );
};
