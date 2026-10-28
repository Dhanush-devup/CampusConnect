import { apiRequest, downloadFile } from "./client";
import {
  AdminDashboardStats,
  Application,
  ApplicationStatusType,
  AuthResponse,
  Company,
  Opportunity,
  OpportunityStatusType,
  RecruiterRegisterResponse,
  ResumeScore,
  RecruiterDashboardStats,
  StudentDashboardStats,
  User,
} from "./types";

export const authApi = {
  login: (data: { email: string; password: string }) =>
    apiRequest<AuthResponse>("/api/auth/login", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  registerStudent: (data: {
    name: string;
    email: string;
    password: string;
    department: string;
    cgpa: number;
    graduation_year: number;
  }) =>
    apiRequest<AuthResponse>("/api/auth/register/student", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  registerRecruiter: (data: {
    name: string;
    email: string;
    password: string;
    company_name: string;
    company_email: string;
    phone?: string;
    industry?: string;
    location?: string;
    website?: string;
  }) =>
    apiRequest<RecruiterRegisterResponse>("/api/auth/register/recruiter", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  getMe: () => apiRequest<User>("/api/auth/me"),

  logout: () =>
    apiRequest("/api/auth/logout", {
      method: "POST",
    }),
};

export const opportunitiesApi = {
  list: (params: {
    search?: string;
    opportunity_type?: string;
    location?: string;
    status?: string;
    eligible_only?: boolean;
    company_id?: number;
  } = {}) => {
    const query = new URLSearchParams();
    if (params.search) query.append("search", params.search);
    if (params.opportunity_type) query.append("opportunity_type", params.opportunity_type);
    if (params.location) query.append("location", params.location);
    if (params.status) query.append("status", params.status);
    if (params.eligible_only) query.append("eligible_only", "true");
    if (params.company_id) query.append("company_id", params.company_id.toString());

    const qs = query.toString();
    return apiRequest<Opportunity[]>(`/api/opportunities${qs ? `?${qs}` : ""}`);
  },

  get: (id: number) => apiRequest<Opportunity>(`/api/opportunities/${id}`),

  create: (data: {
    title: string;
    opportunity_type: string;
    description: string;
    location?: string;
    salary_stipend?: number;
    deadline: string;
    eligibility_cgpa: number;
    status?: OpportunityStatusType;
  }) =>
    apiRequest<Opportunity>("/api/opportunities", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  update: (id: number, data: Partial<Opportunity>) =>
    apiRequest<Opportunity>(`/api/opportunities/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),

  updateStatus: (id: number, status: OpportunityStatusType) =>
    apiRequest<Opportunity>(`/api/opportunities/${id}/status`, {
      method: "PATCH",
      body: JSON.stringify({ status }),
    }),
};

export const applicationsApi = {
  apply: (opportunityId: number, resumeFile?: File) => {
    const formData = new FormData();
    if (resumeFile) {
      formData.append("resume", resumeFile);
    }
    return apiRequest<Application>(`/api/opportunities/${opportunityId}/apply`, {
      method: "POST",
      body: formData,
    });
  },

  listStudentApplications: () =>
    apiRequest<Application[]>("/api/students/applications"),

  listRecruiterApplications: (params: {
    opportunity_id?: number;
    status?: string;
    department?: string;
  } = {}) => {
    const query = new URLSearchParams();
    if (params.opportunity_id) query.append("opportunity_id", params.opportunity_id.toString());
    if (params.status) query.append("status", params.status);
    if (params.department) query.append("department", params.department);

    const qs = query.toString();
    return apiRequest<Application[]>(`/api/recruiters/applications${qs ? `?${qs}` : ""}`);
  },

  updateStatus: (applicationId: number, status: ApplicationStatusType) =>
    apiRequest<Application>(`/api/applications/${applicationId}/status`, {
      method: "PATCH",
      body: JSON.stringify({ status }),
    }),

  uploadResume: (applicationId: number, file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    return apiRequest<{ message: string; resume_path: string }>(
      `/api/applications/${applicationId}/resume`,
      {
        method: "POST",
        body: formData,
      }
    );
  },

  downloadResume: (applicationId: number, filename = "Resume.pdf") =>
    downloadFile(`/api/applications/${applicationId}/resume`, filename),

  getAtsScore: (applicationId: number) =>
    apiRequest<ResumeScore>(`/api/applications/${applicationId}/ats-score`),

  requestAtsScore: (applicationId: number) =>
    apiRequest<ResumeScore>(`/api/applications/${applicationId}/ats-score`, {
      method: "POST",
    }),
};

export const profilesApi = {
  getStudentProfile: () => apiRequest<User>("/api/students/profile"),

  updateStudentProfile: (data: {
    name?: string;
    department?: string;
    cgpa?: number;
    graduation_year?: number;
  }) =>
    apiRequest<User>("/api/students/profile", {
      method: "PUT",
      body: JSON.stringify(data),
    }),

  getStudentDashboardStats: () =>
    apiRequest<StudentDashboardStats>("/api/students/dashboard-stats"),

  listCompanies: () => apiRequest<Company[]>("/api/companies"),

  getCompany: (id: number) => apiRequest<Company>(`/api/companies/${id}`),

  updateMyCompany: (data: Partial<Company>) =>
    apiRequest<Company>("/api/companies/my-company", {
      method: "PUT",
      body: JSON.stringify(data),
    }),

  getRecruiterDashboardStats: () =>
    apiRequest<RecruiterDashboardStats>("/api/recruiters/dashboard-stats"),
};

export const adminApi = {
  listUsers: (params: { role?: string; account_status?: string; search?: string } = {}) => {
    const query = new URLSearchParams();
    if (params.role) query.append("role", params.role);
    if (params.account_status) query.append("account_status", params.account_status);
    if (params.search) query.append("search", params.search);

    const qs = query.toString();
    return apiRequest<User[]>(`/api/admin/users${qs ? `?${qs}` : ""}`);
  },

  updateUserStatus: (userId: number, account_status: "active" | "disabled") =>
    apiRequest<User>(`/api/admin/users/${userId}/status`, {
      method: "PATCH",
      body: JSON.stringify({ account_status }),
    }),

  listCompanies: () => apiRequest<Company[]>("/api/admin/companies"),

  listOpportunities: (status?: string) => {
    const qs = status ? `?status=${status}` : "";
    return apiRequest<Opportunity[]>(`/api/admin/opportunities${qs}`);
  },

  listApplications: (status?: string) => {
    const qs = status ? `?status=${status}` : "";
    return apiRequest<Application[]>(`/api/admin/applications${qs}`);
  },

  getStatistics: () => apiRequest<AdminDashboardStats>("/api/admin/statistics"),
};
