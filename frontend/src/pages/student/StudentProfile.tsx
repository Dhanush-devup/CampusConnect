import React, { useState } from "react";
import { AlertCircle, CheckCircle2, GraduationCap, Save, User as UserIcon } from "lucide-react";
import { profilesApi } from "../../api/endpoints";
import { DashboardLayout } from "../../components/DashboardLayout";
import { useAuth } from "../../context/AuthContext";

export const StudentProfilePage: React.FC = () => {
  const { user, updateUser } = useAuth();
  const student = user?.student_profile;

  const [formData, setFormData] = useState({
    name: user?.name || "",
    department: student?.department || "Computer Science",
    cgpa: student?.cgpa.toString() || "8.50",
    graduation_year: student?.graduation_year.toString() || "2026",
  });

  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const departments = [
    "Computer Science",
    "Information Technology",
    "Electronics & Communication",
    "Electrical Engineering",
    "Mechanical Engineering",
    "Civil Engineering",
    "Data Science & AI",
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    const cgpaFloat = parseFloat(formData.cgpa);
    if (isNaN(cgpaFloat) || cgpaFloat < 0 || cgpaFloat > 10) {
      setError("CGPA must be a valid number between 0.00 and 10.00.");
      return;
    }

    const gradYearInt = parseInt(formData.graduation_year);
    if (isNaN(gradYearInt) || gradYearInt < 2020 || gradYearInt > 2035) {
      setError("Please enter a valid graduation year.");
      return;
    }

    setIsSaving(true);
    try {
      const updated = await profilesApi.updateStudentProfile({
        name: formData.name.trim(),
        department: formData.department.trim(),
        cgpa: cgpaFloat,
        graduation_year: gradYearInt,
      });

      updateUser(updated);
      setSuccess("Profile information saved successfully.");
    } catch (err: any) {
      setError(err.message || "Failed to update profile.");
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <DashboardLayout
      title="Academic Profile Settings"
      subtitle="Manage your personal details and academic credentials used for campus placements."
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
              <div className="h-16 w-16 rounded-2xl bg-gradient-to-tr from-indigo-600 to-indigo-500 text-white flex items-center justify-center font-bold text-xl shadow-md shadow-indigo-500/20">
                {user?.name.charAt(0) || "S"}
              </div>
              <div>
                <h3 className="text-lg font-bold text-slate-900">{user?.name}</h3>
                <p className="text-xs text-slate-500">{user?.email} (Primary login email)</p>
                <div className="mt-1 inline-flex items-center gap-1.5 text-xs text-emerald-600 font-medium">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                  Active Student Account
                </div>
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                Full Display Name
              </label>
              <input
                type="text"
                required
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full rounded-xl border border-slate-300 px-3.5 py-2.5 text-sm text-slate-900 focus:border-indigo-600 focus:outline-none focus:ring-1 focus:ring-indigo-600"
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                  Academic Department
                </label>
                <select
                  value={formData.department}
                  onChange={(e) => setFormData({ ...formData, department: e.target.value })}
                  className="w-full rounded-xl border border-slate-300 px-3.5 py-2.5 text-sm text-slate-900 bg-white focus:border-indigo-600 focus:outline-none focus:ring-1 focus:ring-indigo-600"
                >
                  {departments.map((d) => (
                    <option key={d} value={d}>
                      {d}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                  Current Cumulative CGPA (0.00 - 10.00)
                </label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  max="10"
                  required
                  value={formData.cgpa}
                  onChange={(e) => setFormData({ ...formData, cgpa: e.target.value })}
                  className="w-full rounded-xl border border-slate-300 px-3.5 py-2.5 text-sm text-slate-900 focus:border-indigo-600 focus:outline-none focus:ring-1 focus:ring-indigo-600"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                Expected Graduation Year
              </label>
              <input
                type="number"
                min="2020"
                max="2035"
                required
                value={formData.graduation_year}
                onChange={(e) => setFormData({ ...formData, graduation_year: e.target.value })}
                className="w-full rounded-xl border border-slate-300 px-3.5 py-2.5 text-sm text-slate-900 focus:border-indigo-600 focus:outline-none focus:ring-1 focus:ring-indigo-600"
              />
            </div>

            <div className="pt-4 border-t border-slate-100 flex justify-end">
              <button
                type="submit"
                disabled={isSaving}
                className="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-6 py-2.5 text-xs font-semibold text-white shadow-sm hover:bg-indigo-500 disabled:opacity-50 transition-all"
              >
                <Save className="h-4 w-4" />
                {isSaving ? "Saving Changes..." : "Save Academic Profile"}
              </button>
            </div>
          </form>
        </div>
      </div>
    </DashboardLayout>
  );
};
