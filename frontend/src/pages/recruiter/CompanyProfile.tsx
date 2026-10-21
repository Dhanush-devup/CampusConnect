import React, { useState } from "react";
import { AlertCircle, Building2, CheckCircle2, Globe, Mail, MapPin, Phone, Save } from "lucide-react";
import { profilesApi } from "../../api/endpoints";
import { DashboardLayout } from "../../components/DashboardLayout";
import { useAuth } from "../../context/AuthContext";

export const CompanyProfilePage: React.FC = () => {
  const { user, updateUser } = useAuth();
  const company = user?.company;

  const [formData, setFormData] = useState({
    company_name: company?.company_name || "",
    email: company?.email || "",
    phone: company?.phone || "",
    industry: company?.industry || "",
    location: company?.location || "",
    website: company?.website || "",
  });

  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    setIsSaving(true);

    try {
      const updatedCompany = await profilesApi.updateMyCompany({
        company_name: formData.company_name.trim(),
        email: formData.email.trim() || undefined,
        phone: formData.phone.trim() || undefined,
        industry: formData.industry.trim() || undefined,
        location: formData.location.trim() || undefined,
        website: formData.website.trim() || undefined,
      });

      if (user) {
        updateUser({ ...user, company: updatedCompany });
      }
      setSuccess("Company profile updated successfully.");
    } catch (err: any) {
      setError(err.message || "Failed to save company information.");
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <DashboardLayout
      title="Company Profile Settings"
      subtitle="Manage your organization's public contact details, industry, and campus presence."
    >
      <div className="max-w-2xl mx-auto">
        {success && (
          <div className="mb-6 rounded-xl bg-emerald-50 border border-emerald-200 p-4 text-xs font-semibold text-emerald-800 flex items-center gap-2">
            <CheckCircle2 className="h-4 w-4 text-emerald-600" />
            <span>{success}</span>
          </div>
        )}

        {error && (
          <div className="mb-6 rounded-xl bg-rose-50 border border-rose-200 p-4 text-xs text-rose-700 flex items-center gap-2">
            <AlertCircle className="h-4 w-4 shrink-0 text-rose-600" />
            <span>{error}</span>
          </div>
        )}

        <div className="bg-white rounded-2xl border border-slate-200/80 p-8 shadow-sm">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="flex items-center gap-4 pb-6 border-b border-slate-100">
              <div className="h-16 w-16 rounded-2xl bg-gradient-to-tr from-violet-600 to-indigo-600 text-white flex items-center justify-center font-bold text-xl shadow-md shadow-violet-500/20">
                <Building2 className="h-8 w-8" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-slate-900">{company?.company_name}</h3>
                <p className="text-xs text-slate-500">Official Campus Recruitment Partner</p>
                <p className="text-[11px] text-slate-400 mt-0.5">Recruiter: {user?.name} ({user?.email})</p>
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                Company Legal Name
              </label>
              <input
                type="text"
                required
                value={formData.company_name}
                onChange={(e) => setFormData({ ...formData, company_name: e.target.value })}
                className="w-full rounded-xl border border-slate-300 px-3.5 py-2.5 text-sm text-slate-900 focus:border-violet-600 focus:outline-none focus:ring-1 focus:ring-violet-600"
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                  Official Recruitment Email
                </label>
                <div className="relative">
                  <Mail className="absolute left-3.5 top-3 h-4 w-4 text-slate-400" />
                  <input
                    type="email"
                    required
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    className="w-full rounded-xl border border-slate-300 pl-10 pr-3.5 py-2.5 text-sm text-slate-900 focus:border-violet-600 focus:outline-none focus:ring-1 focus:ring-violet-600"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                  Contact Phone
                </label>
                <div className="relative">
                  <Phone className="absolute left-3.5 top-3 h-4 w-4 text-slate-400" />
                  <input
                    type="text"
                    value={formData.phone}
                    onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                    className="w-full rounded-xl border border-slate-300 pl-10 pr-3.5 py-2.5 text-sm text-slate-900 focus:border-violet-600 focus:outline-none focus:ring-1 focus:ring-violet-600"
                  />
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                  Industry / Domain
                </label>
                <input
                  type="text"
                  value={formData.industry}
                  onChange={(e) => setFormData({ ...formData, industry: e.target.value })}
                  placeholder="e.g. Enterprise Software, FinTech"
                  className="w-full rounded-xl border border-slate-300 px-3.5 py-2.5 text-sm text-slate-900 focus:border-violet-600 focus:outline-none focus:ring-1 focus:ring-violet-600"
                />
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                  Headquarters Location
                </label>
                <div className="relative">
                  <MapPin className="absolute left-3.5 top-3 h-4 w-4 text-slate-400" />
                  <input
                    type="text"
                    value={formData.location}
                    onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                    placeholder="Bangalore, India"
                    className="w-full rounded-xl border border-slate-300 pl-10 pr-3.5 py-2.5 text-sm text-slate-900 focus:border-violet-600 focus:outline-none focus:ring-1 focus:ring-violet-600"
                  />
                </div>
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                Website
              </label>
              <div className="relative">
                <Globe className="absolute left-3.5 top-3 h-4 w-4 text-slate-400" />
                <input
                  type="url"
                  value={formData.website}
                  onChange={(e) => setFormData({ ...formData, website: e.target.value })}
                  placeholder="https://company.com"
                  className="w-full rounded-xl border border-slate-300 pl-10 pr-3.5 py-2.5 text-sm text-slate-900 focus:border-violet-600 focus:outline-none focus:ring-1 focus:ring-violet-600"
                />
              </div>
            </div>

            <div className="pt-4 border-t border-slate-100 flex justify-end">
              <button
                type="submit"
                disabled={isSaving}
                className="inline-flex items-center gap-2 rounded-xl bg-violet-600 px-6 py-2.5 text-xs font-semibold text-white shadow-sm hover:bg-violet-500 disabled:opacity-50 transition-all"
              >
                <Save className="h-4 w-4" />
                {isSaving ? "Saving..." : "Save Profile Details"}
              </button>
            </div>
          </form>
        </div>
      </div>
    </DashboardLayout>
  );
};
