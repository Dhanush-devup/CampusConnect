import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { AlertCircle, ArrowRight, Building2, Globe, KeyRound, Mail, MapPin, Phone, User as UserIcon } from "lucide-react";
import { authApi } from "../api/endpoints";
import { useAuth } from "../context/AuthContext";
import { Navbar } from "../components/Navbar";

export const RegisterRecruiterPage: React.FC = () => {
  const { login } = useAuth();
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
    company_name: "",
    company_email: "",
    phone: "",
    industry: "Information Technology",
    location: "Bangalore, India",
    website: "https://",
  });
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      const res = await authApi.registerRecruiter({
        name: formData.name.trim(),
        email: formData.email.trim(),
        password: formData.password,
        company_name: formData.company_name.trim(),
        company_email: formData.company_email.trim(),
        phone: formData.phone.trim() || undefined,
        industry: formData.industry.trim() || undefined,
        location: formData.location.trim() || undefined,
        website: formData.website.trim() || undefined,
      });

      login(res.access_token, res.user);
      navigate("/recruiter");
    } catch (err: any) {
      setError(err.message || "Registration failed. Please check company and recruiter details.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <Navbar />

      <div className="flex-1 flex items-center justify-center p-4 sm:p-6 lg:p-8">
        <div className="w-full max-w-xl">
          <div className="bg-white rounded-2xl shadow-xl shadow-slate-200/50 border border-slate-200/80 p-8">
            <div className="text-center mb-8">
              <div className="mx-auto w-12 h-12 rounded-2xl bg-violet-600 text-white flex items-center justify-center shadow-lg shadow-violet-500/30 mb-4">
                <Building2 className="h-6 w-6" />
              </div>
              <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Partner Employer Registration</h2>
              <p className="mt-1 text-xs text-slate-500">
                Register your organization and recruiter profile to recruit top college talent
              </p>
            </div>

            {error && (
              <div className="mb-6 rounded-xl bg-rose-50 border border-rose-200 p-3.5 text-xs text-rose-700 flex items-start gap-2.5">
                <AlertCircle className="h-4 w-4 shrink-0 mt-0.5 text-rose-600" />
                <span>{error}</span>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="border-b border-slate-100 pb-2">
                <span className="text-xs font-bold uppercase tracking-wider text-violet-600">
                  1. Recruiter Account Credentials
                </span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                    Your Name
                  </label>
                  <div className="relative">
                    <UserIcon className="absolute left-3.5 top-3 h-4 w-4 text-slate-400" />
                    <input
                      type="text"
                      required
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      placeholder="Jane Doe"
                      className="w-full rounded-xl border border-slate-300 pl-10 pr-3.5 py-2.5 text-sm text-slate-900 focus:border-violet-600 focus:outline-none focus:ring-1 focus:ring-violet-600"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                    Login Email
                  </label>
                  <div className="relative">
                    <Mail className="absolute left-3.5 top-3 h-4 w-4 text-slate-400" />
                    <input
                      type="email"
                      required
                      value={formData.email}
                      onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                      placeholder="jane@company.com"
                      className="w-full rounded-xl border border-slate-300 pl-10 pr-3.5 py-2.5 text-sm text-slate-900 focus:border-violet-600 focus:outline-none focus:ring-1 focus:ring-violet-600"
                    />
                  </div>
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
                    className="w-full rounded-xl border border-slate-300 pl-10 pr-3.5 py-2.5 text-sm text-slate-900 focus:border-violet-600 focus:outline-none focus:ring-1 focus:ring-violet-600"
                  />
                </div>
              </div>

              <div className="border-b border-slate-100 pt-3 pb-2">
                <span className="text-xs font-bold uppercase tracking-wider text-violet-600">
                  2. Company Profile Information
                </span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                    Company Name
                  </label>
                  <div className="relative">
                    <Building2 className="absolute left-3.5 top-3 h-4 w-4 text-slate-400" />
                    <input
                      type="text"
                      required
                      value={formData.company_name}
                      onChange={(e) => setFormData({ ...formData, company_name: e.target.value })}
                      placeholder="Acme Innovations"
                      className="w-full rounded-xl border border-slate-300 pl-10 pr-3.5 py-2.5 text-sm text-slate-900 focus:border-violet-600 focus:outline-none focus:ring-1 focus:ring-violet-600"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                    Official Contact Email
                  </label>
                  <div className="relative">
                    <Mail className="absolute left-3.5 top-3 h-4 w-4 text-slate-400" />
                    <input
                      type="email"
                      required
                      value={formData.company_email}
                      onChange={(e) => setFormData({ ...formData, company_email: e.target.value })}
                      placeholder="careers@acme.com"
                      className="w-full rounded-xl border border-slate-300 pl-10 pr-3.5 py-2.5 text-sm text-slate-900 focus:border-violet-600 focus:outline-none focus:ring-1 focus:ring-violet-600"
                    />
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                    Industry
                  </label>
                  <input
                    type="text"
                    value={formData.industry}
                    onChange={(e) => setFormData({ ...formData, industry: e.target.value })}
                    placeholder="Software, Fintech"
                    className="w-full rounded-xl border border-slate-300 px-3.5 py-2.5 text-sm text-slate-900 focus:border-violet-600 focus:outline-none focus:ring-1 focus:ring-violet-600"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                    Location
                  </label>
                  <input
                    type="text"
                    value={formData.location}
                    onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                    placeholder="City, Country"
                    className="w-full rounded-xl border border-slate-300 px-3.5 py-2.5 text-sm text-slate-900 focus:border-violet-600 focus:outline-none focus:ring-1 focus:ring-violet-600"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                    Contact Phone
                  </label>
                  <input
                    type="text"
                    value={formData.phone}
                    onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                    placeholder="+1 555-0199"
                    className="w-full rounded-xl border border-slate-300 px-3.5 py-2.5 text-sm text-slate-900 focus:border-violet-600 focus:outline-none focus:ring-1 focus:ring-violet-600"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                  Company Website
                </label>
                <div className="relative">
                  <Globe className="absolute left-3.5 top-3 h-4 w-4 text-slate-400" />
                  <input
                    type="url"
                    value={formData.website}
                    onChange={(e) => setFormData({ ...formData, website: e.target.value })}
                    placeholder="https://acme.com"
                    className="w-full rounded-xl border border-slate-300 pl-10 pr-3.5 py-2.5 text-sm text-slate-900 focus:border-violet-600 focus:outline-none focus:ring-1 focus:ring-violet-600"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={isSubmitting}
                className="w-full mt-4 flex items-center justify-center gap-2 rounded-xl bg-violet-600 py-3 text-sm font-semibold text-white shadow-sm hover:bg-violet-500 focus:outline-none focus:ring-2 focus:ring-violet-600 disabled:opacity-50 transition-all"
              >
                {isSubmitting ? "Registering Company & Recruiter..." : "Complete Recruiter Registration"}
                {!isSubmitting && <ArrowRight className="h-4 w-4" />}
              </button>
            </form>

            <div className="mt-6 text-center text-xs text-slate-500">
              Already registered?{" "}
              <Link to="/login" className="font-semibold text-violet-600 hover:underline">
                Sign in here
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
