export type RoleType = "student" | "recruiter" | "admin";
export type AccountStatusType = "active" | "disabled";
export type OpportunityType = "internship" | "full_time" | "part_time";
export type OpportunityStatusType = "draft" | "open" | "closed";
export type ApplicationStatusType =
  | "applied"
  | "under_review"
  | "shortlisted"
  | "interview"
  | "selected"
  | "rejected";

export interface StudentProfile {
  student_id: number;
  user_id: number;
  department: string;
  cgpa: number;
  graduation_year: number;
}

export interface Company {
  company_id: number;
  company_name: string;
  email: string;
  phone?: string | null;
  industry?: string | null;
  location?: string | null;
  website?: string | null;
}

export interface User {
  user_id: number;
  name: string;
  email: string;
  role: RoleType;
  account_status: AccountStatusType;
  company_id?: number | null;
  created_at: string;
  student_profile?: StudentProfile | null;
  company?: Company | null;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface Opportunity {
  opportunity_id: number;
  company_id: number;
  title: string;
  opportunity_type: OpportunityType;
  description: string;
  location?: string | null;
  salary_stipend?: number | null;
  deadline: string;
  eligibility_cgpa: number;
  status: OpportunityStatusType;
  created_at: string;
  company: Company;
  has_applied?: boolean;
  is_eligible?: boolean;
  application_count?: number;
}

export interface Application {
  application_id: number;
  student_id: number;
  opportunity_id: number;
  application_date: string;
  status: ApplicationStatusType;
  resume_path?: string | null;
  student_name: string;
  student_email: string;
  student_department: string;
  student_cgpa: number;
  student_graduation_year: number;
  opportunity_title: string;
  opportunity_type: OpportunityType;
  opportunity_location?: string | null;
  salary_stipend?: number | null;
  deadline: string;
  company_name: string;
  company_location?: string | null;
}

export interface StudentDashboardStats {
  total_applications: number;
  applied: number;
  under_review: number;
  shortlisted: number;
  interview: number;
  selected: number;
  rejected: number;
  eligible_opportunities_count: number;
}

export interface RecruiterDashboardStats {
  total_opportunities: number;
  open_opportunities: number;
  closed_opportunities: number;
  total_applications: number;
  applied: number;
  under_review: number;
  shortlisted: number;
  interview: number;
  selected: number;
  rejected: number;
}

export interface AdminDashboardStats {
  total_users: number;
  students_count: number;
  recruiters_count: number;
  admins_count: number;
  total_companies: number;
  total_opportunities: number;
  open_opportunities: number;
  closed_opportunities: number;
  draft_opportunities: number;
  total_applications: number;
  applications_by_status: Record<string, number>;
  applications_by_department: Record<string, number>;
  placement_rate: number;
  top_companies: Array<{
    company_id: number;
    company_name: string;
    opportunities_count: number;
    applications_count: number;
  }>;
}
