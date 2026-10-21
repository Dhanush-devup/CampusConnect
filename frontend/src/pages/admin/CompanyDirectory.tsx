import React, { useEffect, useState } from "react";
import { AlertCircle, Building2, Globe, Mail, MapPin, Phone, Users } from "lucide-react";
import { adminApi } from "../../api/endpoints";
import { Company } from "../../api/types";
import { DashboardLayout } from "../../components/DashboardLayout";

export const CompanyDirectory: React.FC = () => {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchCompanies = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const data = await adminApi.listCompanies();
        setCompanies(data);
      } catch (err: any) {
        setError(err.message || "Failed to load companies.");
      } finally {
        setIsLoading(false);
      }
    };

    fetchCompanies();
  }, []);

  return (
    <DashboardLayout
      title="Partner Company Directory"
      subtitle="Overview of all corporate partners registered on CampusConnect for placement recruitment."
    >
      {error && (
        <div className="mb-6 rounded-xl bg-rose-50 border border-rose-200 p-4 text-xs text-rose-700 flex items-center gap-2">
          <AlertCircle className="h-4 w-4 shrink-0 text-rose-600" />
          <span>{error}</span>
        </div>
      )}

      {isLoading ? (
        <div className="py-20 text-center">
          <div className="mx-auto h-8 w-8 animate-spin rounded-full border-4 border-indigo-600 border-t-transparent mb-3" />
          <p className="text-xs text-slate-500">Loading company directory...</p>
        </div>
      ) : companies.length === 0 ? (
        <div className="rounded-2xl bg-white border border-dashed border-slate-300 p-12 text-center">
          <Building2 className="mx-auto h-10 w-10 text-slate-300 mb-3" />
          <h3 className="text-sm font-bold text-slate-800">No partner companies registered yet</h3>
          <p className="text-xs text-slate-500 mt-1">Employers will appear here upon registration.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {companies.map((co) => (
            <div
              key={co.company_id}
              className="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-sm hover:shadow-md transition-all flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-12 h-12 rounded-xl bg-violet-50 text-violet-600 flex items-center justify-center font-bold">
                    <Building2 className="h-6 w-6" />
                  </div>
                  <div>
                    <h3 className="text-base font-bold text-slate-900">{co.company_name}</h3>
                    <p className="text-xs text-violet-600 font-semibold">{co.industry || "General Industry"}</p>
                  </div>
                </div>

                <div className="space-y-2 text-xs text-slate-500 border-t border-slate-100 pt-3">
                  <div className="flex items-center gap-2">
                    <Mail className="h-3.5 w-3.5 text-slate-400" />
                    <span>{co.email}</span>
                  </div>
                  {co.phone && (
                    <div className="flex items-center gap-2">
                      <Phone className="h-3.5 w-3.5 text-slate-400" />
                      <span>{co.phone}</span>
                    </div>
                  )}
                  {co.location && (
                    <div className="flex items-center gap-2">
                      <MapPin className="h-3.5 w-3.5 text-slate-400" />
                      <span>{co.location}</span>
                    </div>
                  )}
                </div>
              </div>

              {co.website && (
                <div className="mt-5 pt-3 border-t border-slate-100">
                  <a
                    href={co.website}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-1.5 text-xs font-semibold text-indigo-600 hover:text-indigo-700"
                  >
                    <Globe className="h-3.5 w-3.5" />
                    Visit Website &rarr;
                  </a>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </DashboardLayout>
  );
};
