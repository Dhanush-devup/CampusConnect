import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { AlertCircle, ArrowRight, GraduationCap, KeyRound, Mail, School, Sparkles, User as UserIcon } from "lucide-react";
import { authApi } from "../api/endpoints";
import { useAuth } from "../context/AuthContext";
import { Navbar } from "../components/Navbar";

export const RegisterStudentPage: React.FC = () => {
  const { login } = useAuth();
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
    department: "Computer Science",
    cgpa: "8.50",
    graduation_year: "2026",
  });
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

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

    setIsSubmitting(true);
    try {
      const res = await authApi.registerStudent({
        name: formData.name.trim(),
        email: formData.email.trim(),
        password: formData.password,
        department: formData.department.trim(),
        cgpa: cgpaFloat,
        graduation_year: gradYearInt,
      });

      login(res.access_token, res.user);
      navigate("/student");
    } catch (err: any) {
      setError(err.message || "Registration failed. Please check your information.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <Navbar />

      <div className="flex-1 flex items-center justify-center p-4 sm:p-6 lg:p-8">
        <div className="w-full max-w-lg">
          <div className="bg-white rounded-2xl shadow-xl shadow-slate-200/50 border border-slate-200/80 p-8">
            <div className="text-center mb-8">
              <div className="mx-auto w-12 h-12 rounded-2xl bg-indigo-600 text-white flex items-center justify-center shadow-lg shadow-indigo-500/30 mb-4">
                <GraduationCap className="h-6 w-6" />
              </div>
              <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Student Registration</h2>
              <p className="mt-1 text-xs text-slate-500">
                Create your student profile to explore campus placements and internships
              </p>
            </div>

            {error && (
              <div className="mb-6 rounded-xl bg-rose-50 border border-rose-200 p-3.5 text-xs text-rose-700 flex items-start gap-2.5">
                <AlertCircle className="h-4 w-4 shrink-0 mt-0.5 text-rose-600" />
                <span>{error}</span>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                  Full Name
                </label>
                <div className="relative">
                  <UserIcon className="absolute left-3.5 top-3 h-4 w-4 text-slate-400" />
                  <input
                    type="text"
                    required
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    placeholder="Alice Smith"
                    className="w-full rounded-xl border border-slate-300 pl-10 pr-3.5 py-2.5 text-sm text-slate-900 placeholder:text-slate-400 focus:border-indigo-600 focus:outline-none focus:ring-1 focus:ring-indigo-600"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                  College Email Address
                </label>
                <div className="relative">
                  <Mail className="absolute left-3.5 top-3 h-4 w-4 text-slate-400" />
                  <input
                    type="email"
                    required
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    placeholder="alice@college.edu"
                    className="w-full rounded-xl border border-slate-300 pl-10 pr-3.5 py-2.5 text-sm text-slate-900 placeholder:text-slate-400 focus:border-indigo-600 focus:outline-none focus:ring-1 focus:ring-indigo-600"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                  Password
                </label>
                <div className="relative">
                  <KeyRound className="absolute left-3.5 top-3 h-4 w-4 text-slate-400" />
                  <input
                    type="password"
                    required
                    minLength={6}
                    value={formData.password}
                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                    placeholder="Minimum 6 characters"
                    className="w-full rounded-xl border border-slate-300 pl-10 pr-3.5 py-2.5 text-sm text-slate-900 placeholder:text-slate-400 focus:border-indigo-600 focus:outline-none focus:ring-1 focus:ring-indigo-600"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="sm:col-span-3">
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                    Department
                  </label>
                  <select
                    value={formData.department}
                    onChange={(e) => setFormData({ ...formData, department: e.target.value })}
                    className="w-full rounded-xl border border-slate-300 px-3.5 py-2.5 text-sm text-slate-900 focus:border-indigo-600 focus:outline-none focus:ring-1 focus:ring-indigo-600 bg-white"
                  >
                    {departments.map((dept) => (
                      <option key={dept} value={dept}>
                        {dept}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="sm:col-span-2">
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                    Current CGPA (0.0 - 10.0)
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    max="10"
                    required
                    value={formData.cgpa}
                    onChange={(e) => setFormData({ ...formData, cgpa: e.target.value })}
                    placeholder="8.50"
                    className="w-full rounded-xl border border-slate-300 px-3.5 py-2.5 text-sm text-slate-900 focus:border-indigo-600 focus:outline-none focus:ring-1 focus:ring-indigo-600"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                    Grad Year
                  </label>
                  <input
                    type="number"
                    required
                    min="2020"
                    max="2035"
                    value={formData.graduation_year}
                    onChange={(e) => setFormData({ ...formData, graduation_year: e.target.value })}
                    className="w-full rounded-xl border border-slate-300 px-3.5 py-2.5 text-sm text-slate-900 focus:border-indigo-600 focus:outline-none focus:ring-1 focus:ring-indigo-600"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={isSubmitting}
                className="w-full mt-4 flex items-center justify-center gap-2 rounded-xl bg-indigo-600 py-3 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-600 disabled:opacity-50 transition-all"
              >
                {isSubmitting ? "Creating Student Account..." : "Complete Registration"}
                {!isSubmitting && <ArrowRight className="h-4 w-4" />}
              </button>
            </form>

            <div className="mt-6 text-center text-xs text-slate-500">
              Already have an account?{" "}
              <Link to="/login" className="font-semibold text-indigo-600 hover:underline">
                Sign in here
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
