import React, { useEffect, useState } from "react";
import {
  AlertCircle,
  CheckCircle2,
  Filter,
  Lock,
  Mail,
  Power,
  Search,
  ShieldCheck,
  UserCheck,
  Users,
} from "lucide-react";
import { adminApi } from "../../api/endpoints";
import { User } from "../../api/types";
import { DashboardLayout } from "../../components/DashboardLayout";
import { StatusBadge } from "../../components/StatusBadge";
import { useAuth } from "../../context/AuthContext";

export const UserManagement: React.FC = () => {
  const { user: currentUser } = useAuth();
  const [users, setUsers] = useState<User[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Filters
  const [search, setSearch] = useState("");
  const [roleFilter, setRoleFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");

  const fetchUsers = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await adminApi.listUsers({
        search: search.trim() || undefined,
        role: roleFilter || undefined,
        account_status: statusFilter || undefined,
      });
      setUsers(data);
    } catch (err: any) {
      setError(err.message || "Failed to load user accounts.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, [roleFilter, statusFilter]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchUsers();
  };

  const handleToggleStatus = async (targetUser: User) => {
    if (targetUser.user_id === currentUser?.user_id) {
      alert("You cannot disable your own administrator account.");
      return;
    }

    const nextStatus = targetUser.account_status === "active" ? "disabled" : "active";
    try {
      await adminApi.updateUserStatus(targetUser.user_id, nextStatus);
      setSuccess(`Account status for ${targetUser.name} changed to ${nextStatus}.`);
      setUsers((prev) =>
        prev.map((u) => (u.user_id === targetUser.user_id ? { ...u, account_status: nextStatus } : u))
      );
    } catch (err: any) {
      alert(err.message || "Failed to update account status.");
    }
  };

  return (
    <DashboardLayout
      title="User Account Management"
      subtitle="Approve new recruiters and supervise user accounts across students, recruiters, and administrators."
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

      {/* Filter Toolbar */}
      <div className="bg-white rounded-2xl border border-slate-200/80 p-4 mb-6 shadow-xs flex flex-col md:flex-row gap-3">
        <form onSubmit={handleSearchSubmit} className="relative flex-1">
          <Search className="absolute left-3.5 top-3 h-4 w-4 text-slate-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by user name or email..."
            className="w-full rounded-xl border border-slate-300 pl-10 pr-3.5 py-2.5 text-xs text-slate-900 placeholder:text-slate-400 focus:border-indigo-600 focus:outline-none"
          />
        </form>

        <div className="flex items-center gap-2">
          <select
            value={roleFilter}
            onChange={(e) => setRoleFilter(e.target.value)}
            className="rounded-xl border border-slate-300 px-3 py-2.5 text-xs text-slate-700 bg-white focus:border-indigo-600 focus:outline-none"
          >
            <option value="">All Roles</option>
            <option value="student">Student</option>
            <option value="recruiter">Recruiter</option>
            <option value="admin">Administrator</option>
          </select>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="rounded-xl border border-slate-300 px-3 py-2.5 text-xs text-slate-700 bg-white focus:border-indigo-600 focus:outline-none"
          >
            <option value="">All Statuses</option>
            <option value="pending">Pending Approval</option>
            <option value="active">Active Only</option>
            <option value="disabled">Disabled Only</option>
          </select>

          <button
            type="button"
            onClick={fetchUsers}
            className="rounded-xl bg-slate-900 text-white px-4 py-2.5 text-xs font-semibold hover:bg-slate-800 transition-colors"
          >
            Search
          </button>
        </div>
      </div>

      {/* Users Table */}
      {isLoading ? (
        <div className="py-20 text-center">
          <div className="mx-auto h-8 w-8 animate-spin rounded-full border-4 border-indigo-600 border-t-transparent mb-3" />
          <p className="text-xs text-slate-500">Loading user directory...</p>
        </div>
      ) : users.length === 0 ? (
        <div className="rounded-2xl bg-white border border-dashed border-slate-300 p-12 text-center">
          <Users className="mx-auto h-10 w-10 text-slate-300 mb-3" />
          <h3 className="text-sm font-bold text-slate-800">No matching users found</h3>
          <p className="text-xs text-slate-500 mt-1">Try broadening your search query or filter criteria.</p>
        </div>
      ) : (
        <div className="bg-white rounded-2xl border border-slate-200/80 shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50/80 border-b border-slate-200 text-slate-500 font-bold uppercase tracking-wider">
                <tr>
                  <th className="py-3.5 px-6">User Name</th>
                  <th className="py-3.5 px-4">Email</th>
                  <th className="py-3.5 px-4">Role</th>
                  <th className="py-3.5 px-4">Affiliation / Profile</th>
                  <th className="py-3.5 px-4">Status</th>
                  <th className="py-3.5 px-6 text-right">Account Control</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {users.map((u) => {
                  const isCurrentAdmin = u.user_id === currentUser?.user_id;

                  return (
                    <tr key={u.user_id} className="hover:bg-slate-50/70 transition-colors">
                      <td className="py-4 px-6 font-bold text-slate-900">
                        {u.name}
                        {isCurrentAdmin && (
                          <span className="ml-2 text-[10px] bg-slate-100 text-slate-600 font-semibold px-1.5 py-0.5 rounded">
                            You
                          </span>
                        )}
                      </td>
                      <td className="py-4 px-4 text-slate-600">{u.email}</td>
                      <td className="py-4 px-4">
                        <StatusBadge status={u.role} size="sm" />
                      </td>
                      <td className="py-4 px-4 text-slate-600">
                        {u.student_profile && (
                          <span>
                            {u.student_profile.department} (CGPA: {u.student_profile.cgpa.toFixed(2)})
                          </span>
                        )}
                        {u.company && <span>{u.company.company_name}</span>}
                        {u.role === "admin" && <span className="text-slate-400">Placement Cell</span>}
                      </td>
                      <td className="py-4 px-4">
                        <StatusBadge status={u.account_status} size="sm" />
                      </td>
                      <td className="py-4 px-6 text-right">
                        {isCurrentAdmin ? (
                          <span className="text-slate-400 text-[11px] italic">Self Protected</span>
                        ) : (
                          <button
                            onClick={() => handleToggleStatus(u)}
                            className={`inline-flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-xs font-semibold transition-colors ${
                              u.account_status === "active"
                                ? "border-rose-200 bg-rose-50 text-rose-700 hover:bg-rose-100"
                                : "border-emerald-200 bg-emerald-50 text-emerald-700 hover:bg-emerald-100"
                            }`}
                          >
                            <Power className="h-3.5 w-3.5" />
                            {u.account_status === "active"
                              ? "Disable Account"
                              : u.account_status === "pending"
                                ? "Approve"
                                : "Reactivate"}
                          </button>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </DashboardLayout>
  );
};
