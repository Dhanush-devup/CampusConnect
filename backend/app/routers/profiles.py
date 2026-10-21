"""
Profile management and user dashboard statistics endpoints.
Handles student profiles, company management, and role-specific analytics.
"""
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_active_user, require_role
from app.database import get_db
from app.models import Application, Company, Opportunity, Student, User
from app.schemas import (
    CompanyProfileUpdate,
    CompanyRead,
    RecruiterDashboardStats,
    StudentDashboardStats,
    StudentProfileUpdate,
    UserProfileResponse,
)

router = APIRouter(prefix="/api", tags=["Profiles & Analytics"])


# ============================================================================
# 1. Student Profile & Dashboard Statistics
# ============================================================================

@router.get(
    "/students/profile",
    response_model=UserProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Student Profile",
)
def get_student_profile(
    current_user: User = Depends(require_role(["student"])),
):
    """Returns the profile of the authenticated student."""
    from app.routers.auth import format_user_profile
    return format_user_profile(current_user)


@router.put(
    "/students/profile",
    response_model=UserProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Student Profile",
)
def update_student_profile(
    payload: StudentProfileUpdate,
    current_user: User = Depends(require_role(["student"])),
    db: Session = Depends(get_db),
):
    """
    Updates the student's academic and profile details.
    Enforces CGPA constraints and updates both User and Student tables.
    """
    student = current_user.student_profile
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found.",
        )

    if payload.name is not None:
        current_user.name = payload.name.strip()

    if payload.department is not None:
        student.department = payload.department.strip()

    if payload.cgpa is not None:
        student.cgpa = round(payload.cgpa, 2)

    if payload.graduation_year is not None:
        student.graduation_year = payload.graduation_year

    db.commit()
    db.refresh(current_user)

    from app.routers.auth import format_user_profile
    return format_user_profile(current_user)


@router.get(
    "/students/dashboard-stats",
    response_model=StudentDashboardStats,
    status_code=status.HTTP_200_OK,
    summary="Get Student Dashboard Statistics",
)
def get_student_dashboard_stats(
    current_user: User = Depends(require_role(["student"])),
    db: Session = Depends(get_db),
):
    """
    Computes real-time database statistics for the student's dashboard:
    Total applications, counts by status, and currently eligible open opportunities.
    """
    student = current_user.student_profile
    if not student:
        return StudentDashboardStats()

    # Query all applications for this student
    applications = db.query(Application).filter(Application.student_id == student.student_id).all()

    counts = {
        "applied": 0,
        "under_review": 0,
        "shortlisted": 0,
        "interview": 0,
        "selected": 0,
        "rejected": 0,
    }
    for app in applications:
        if app.status in counts:
            counts[app.status] += 1

    # Count eligible open opportunities
    now_utc = datetime.now(timezone.utc)
    eligible_count = (
        db.query(Opportunity)
        .filter(
            Opportunity.status == "open",
            Opportunity.deadline > now_utc,
            Opportunity.eligibility_cgpa <= student.cgpa,
        )
        .count()
    )

    return StudentDashboardStats(
        total_applications=len(applications),
        applied=counts["applied"],
        under_review=counts["under_review"],
        shortlisted=counts["shortlisted"],
        interview=counts["interview"],
        selected=counts["selected"],
        rejected=counts["rejected"],
        eligible_opportunities_count=eligible_count,
    )


# ============================================================================
# 2. Company Management & Recruiter Dashboard
# ============================================================================

@router.get(
    "/companies",
    response_model=List[CompanyRead],
    status_code=status.HTTP_200_OK,
    summary="List Registered Companies",
)
def list_companies(
    db: Session = Depends(get_db),
):
    """Returns a list of all registered partner companies."""
    companies = db.query(Company).order_by(Company.company_name.asc()).all()
    return [CompanyRead.model_validate(c) for c in companies]


@router.get(
    "/companies/{company_id}",
    response_model=CompanyRead,
    status_code=status.HTTP_200_OK,
    summary="Get Company Profile",
)
def get_company(
    company_id: int,
    db: Session = Depends(get_db),
):
    """Retrieves public details for a single company."""
    company = db.query(Company).filter(Company.company_id == company_id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found.",
        )
    return CompanyRead.model_validate(company)


@router.put(
    "/companies/my-company",
    response_model=CompanyRead,
    status_code=status.HTTP_200_OK,
    summary="Update Recruiter's Company Profile",
)
def update_my_company(
    payload: CompanyProfileUpdate,
    current_user: User = Depends(require_role(["recruiter"])),
    db: Session = Depends(get_db),
):
    """
    Updates the contact and profile information for the recruiter's company.
    """
    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No company associated with this recruiter account.",
        )

    company = db.query(Company).filter(Company.company_id == current_user.company_id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company record not found.",
        )

    if payload.company_name is not None:
        company.company_name = payload.company_name.strip()
    if payload.email is not None:
        company.email = payload.email.lower().strip()
    if payload.phone is not None:
        company.phone = payload.phone.strip()
    if payload.industry is not None:
        company.industry = payload.industry.strip()
    if payload.location is not None:
        company.location = payload.location.strip()
    if payload.website is not None:
        company.website = payload.website.strip()

    db.commit()
    db.refresh(company)

    return CompanyRead.model_validate(company)


@router.get(
    "/recruiters/dashboard-stats",
    response_model=RecruiterDashboardStats,
    status_code=status.HTTP_200_OK,
    summary="Get Recruiter Dashboard Statistics",
)
def get_recruiter_dashboard_stats(
    current_user: User = Depends(require_role(["recruiter"])),
    db: Session = Depends(get_db),
):
    """
    Returns real database metrics for the recruiter's dashboard:
    Total postings, open/closed split, total applicants, and application breakdown.
    """
    if not current_user.company_id:
        return RecruiterDashboardStats()

    # Opportunities metrics
    opps = db.query(Opportunity).filter(Opportunity.company_id == current_user.company_id).all()
    total_opps = len(opps)
    open_opps = sum(1 for o in opps if o.status == "open")
    closed_opps = sum(1 for o in opps if o.status == "closed")

    # Applications metrics
    opp_ids = [o.opportunity_id for o in opps]
    applications = (
        db.query(Application)
        .filter(Application.opportunity_id.in_(opp_ids))
        .all()
        if opp_ids
        else []
    )

    counts = {
        "applied": 0,
        "under_review": 0,
        "shortlisted": 0,
        "interview": 0,
        "selected": 0,
        "rejected": 0,
    }
    for app in applications:
        if app.status in counts:
            counts[app.status] += 1

    return RecruiterDashboardStats(
        total_opportunities=total_opps,
        open_opportunities=open_opps,
        closed_opportunities=closed_opps,
        total_applications=len(applications),
        applied=counts["applied"],
        under_review=counts["under_review"],
        shortlisted=counts["shortlisted"],
        interview=counts["interview"],
        selected=counts["selected"],
        rejected=counts["rejected"],
    )
