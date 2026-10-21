"""
Pydantic schemas for request and response validation.
Defines data structures for Authentication, Users, Students, Companies,
Opportunities, Applications, Profiles, and Dashboard Analytics.
"""
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ============================================================================
# System & Health Check Schema
# ============================================================================

class HealthCheckResponse(BaseModel):
    status: str = Field(default="healthy", description="Application operational status")
    database: str = Field(default="connected", description="Database connection status")
    app_name: str
    environment: str


# ============================================================================
# Core Type Literals
# ============================================================================

RoleType = Literal["student", "recruiter", "admin"]
AccountStatusType = Literal["active", "disabled"]
OpportunityType = Literal["internship", "full_time", "part_time"]
OpportunityStatusType = Literal["draft", "open", "closed"]
ApplicationStatusType = Literal[
    "applied",
    "under_review",
    "shortlisted",
    "interview",
    "selected",
    "rejected",
]


# ============================================================================
# Base Entity Schemas
# ============================================================================

class UserBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr = Field(...)
    role: RoleType = Field(...)
    account_status: AccountStatusType = Field(default="active")
    company_id: Optional[int] = Field(default=None)


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="Plaintext password to be securely hashed")


class UserRead(UserBase):
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StudentBase(BaseModel):
    department: str = Field(..., min_length=1, max_length=100)
    cgpa: float = Field(..., ge=0.0, le=10.0, description="CGPA on a 0.0 to 10.0 scale")
    graduation_year: int = Field(..., ge=2000, le=2100)


class StudentCreate(StudentBase):
    user_id: int


class StudentRead(StudentBase):
    student_id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)


class CompanyBase(BaseModel):
    company_name: str = Field(..., min_length=1, max_length=150)
    email: EmailStr = Field(...)
    phone: Optional[str] = Field(default=None, max_length=30)
    industry: Optional[str] = Field(default=None, max_length=100)
    location: Optional[str] = Field(default=None, max_length=150)
    website: Optional[str] = Field(default=None, max_length=255)


class CompanyCreate(CompanyBase):
    pass


class CompanyRead(CompanyBase):
    company_id: int

    model_config = ConfigDict(from_attributes=True)


class OpportunityBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=150)
    opportunity_type: OpportunityType = Field(...)
    description: str = Field(..., min_length=1)
    location: Optional[str] = Field(default=None, max_length=150)
    salary_stipend: Optional[float] = Field(default=None, ge=0.0)
    deadline: datetime
    eligibility_cgpa: float = Field(..., ge=0.0, le=10.0)
    status: OpportunityStatusType = Field(default="open")


class OpportunityCreate(OpportunityBase):
    company_id: int


class OpportunityRead(OpportunityBase):
    opportunity_id: int
    company_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ApplicationBase(BaseModel):
    status: ApplicationStatusType = Field(default="applied")
    resume_path: Optional[str] = Field(default=None, max_length=500)


class ApplicationCreate(ApplicationBase):
    student_id: int
    opportunity_id: int


class ApplicationRead(ApplicationBase):
    application_id: int
    student_id: int
    opportunity_id: int
    application_date: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Authentication & Registration Request/Response Schemas
# ============================================================================

class StudentRegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr = Field(...)
    password: str = Field(..., min_length=6, max_length=100)
    department: str = Field(..., min_length=2, max_length=100)
    cgpa: float = Field(..., ge=0.0, le=10.0)
    graduation_year: int = Field(..., ge=2020, le=2035)


class RecruiterRegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr = Field(..., description="Recruiter individual login email")
    password: str = Field(..., min_length=6, max_length=100)
    company_name: str = Field(..., min_length=2, max_length=150)
    company_email: EmailStr = Field(..., description="Company primary contact email")
    phone: Optional[str] = Field(default=None, max_length=30)
    industry: Optional[str] = Field(default=None, max_length=100)
    location: Optional[str] = Field(default=None, max_length=150)
    website: Optional[str] = Field(default=None, max_length=255)


class LoginRequest(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(..., min_length=1)


class UserProfileResponse(BaseModel):
    user_id: int
    name: str
    email: str
    role: RoleType
    account_status: AccountStatusType
    company_id: Optional[int] = None
    created_at: datetime
    student_profile: Optional[StudentRead] = None
    company: Optional[CompanyRead] = None

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserProfileResponse


# ============================================================================
# Profile & Account Management Schemas
# ============================================================================

class StudentProfileUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    department: Optional[str] = Field(default=None, min_length=2, max_length=100)
    cgpa: Optional[float] = Field(default=None, ge=0.0, le=10.0)
    graduation_year: Optional[int] = Field(default=None, ge=2020, le=2035)


class CompanyProfileUpdate(BaseModel):
    company_name: Optional[str] = Field(default=None, min_length=2, max_length=150)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, max_length=30)
    industry: Optional[str] = Field(default=None, max_length=100)
    location: Optional[str] = Field(default=None, max_length=150)
    website: Optional[str] = Field(default=None, max_length=255)


class UserStatusUpdate(BaseModel):
    account_status: AccountStatusType


# ============================================================================
# Opportunity Schemas (Extended)
# ============================================================================

class OpportunityCreateByRecruiter(BaseModel):
    title: str = Field(..., min_length=2, max_length=150)
    opportunity_type: OpportunityType = Field(...)
    description: str = Field(..., min_length=10)
    location: Optional[str] = Field(default=None, max_length=150)
    salary_stipend: Optional[float] = Field(default=None, ge=0.0)
    deadline: datetime
    eligibility_cgpa: float = Field(..., ge=0.0, le=10.0)
    status: OpportunityStatusType = Field(default="open")


class OpportunityUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=2, max_length=150)
    opportunity_type: Optional[OpportunityType] = None
    description: Optional[str] = Field(default=None, min_length=10)
    location: Optional[str] = Field(default=None, max_length=150)
    salary_stipend: Optional[float] = Field(default=None, ge=0.0)
    deadline: Optional[datetime] = None
    eligibility_cgpa: Optional[float] = Field(default=None, ge=0.0, le=10.0)
    status: Optional[OpportunityStatusType] = None


class OpportunityStatusUpdate(BaseModel):
    status: OpportunityStatusType


class OpportunityDetailResponse(BaseModel):
    opportunity_id: int
    company_id: int
    title: str
    opportunity_type: OpportunityType
    description: str
    location: Optional[str]
    salary_stipend: Optional[float]
    deadline: datetime
    eligibility_cgpa: float
    status: OpportunityStatusType
    created_at: datetime
    company: CompanyRead
    has_applied: Optional[bool] = None
    is_eligible: Optional[bool] = None
    application_count: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Application Schemas (Extended)
# ============================================================================

class ApplicationStatusUpdate(BaseModel):
    status: ApplicationStatusType


class ApplicationDetailResponse(BaseModel):
    application_id: int
    student_id: int
    opportunity_id: int
    application_date: datetime
    status: ApplicationStatusType
    resume_path: Optional[str] = None
    # Nested Student Info
    student_name: str
    student_email: str
    student_department: str
    student_cgpa: float
    student_graduation_year: int
    # Nested Opportunity & Company Info
    opportunity_title: str
    opportunity_type: OpportunityType
    opportunity_location: Optional[str] = None
    salary_stipend: Optional[float] = None
    deadline: datetime
    company_name: str
    company_location: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Dashboard Analytics Schemas
# ============================================================================

class StudentDashboardStats(BaseModel):
    total_applications: int = 0
    applied: int = 0
    under_review: int = 0
    shortlisted: int = 0
    interview: int = 0
    selected: int = 0
    rejected: int = 0
    eligible_opportunities_count: int = 0


class RecruiterDashboardStats(BaseModel):
    total_opportunities: int = 0
    open_opportunities: int = 0
    closed_opportunities: int = 0
    total_applications: int = 0
    applied: int = 0
    under_review: int = 0
    shortlisted: int = 0
    interview: int = 0
    selected: int = 0
    rejected: int = 0


class AdminDashboardStats(BaseModel):
    total_users: int = 0
    students_count: int = 0
    recruiters_count: int = 0
    admins_count: int = 0
    total_companies: int = 0
    total_opportunities: int = 0
    open_opportunities: int = 0
    closed_opportunities: int = 0
    draft_opportunities: int = 0
    total_applications: int = 0
    applications_by_status: Dict[str, int] = {}
    applications_by_department: Dict[str, int] = {}
    placement_rate: float = 0.0
    top_companies: List[Dict[str, Any]] = []
