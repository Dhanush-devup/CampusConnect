"""
Administrative oversight, user account management, and institutional statistics endpoints.
Strictly protected: Accessible only to users with the 'admin' role.
"""
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.auth import require_role
from app.database import get_db
from app.models import Application, Company, Opportunity, Student, User
from app.schemas import (
    AdminDashboardStats,
    ApplicationDetailResponse,
    CompanyRead,
    OpportunityDetailResponse,
    UserProfileResponse,
    UserStatusUpdate,
)

router = APIRouter(prefix="/api/admin", tags=["Admin Oversight"])


# ============================================================================
# 1. User & Account Management
# ============================================================================

@router.get(
    "/users",
    response_model=List[UserProfileResponse],
    status_code=status.HTTP_200_OK,
    summary="List All Users (Admin Only)",
)
def list_all_users(
    role: Optional[str] = Query(None, description="Filter by role: student, recruiter, admin"),
    account_status: Optional[str] = Query(None, description="Filter by account status: pending, active, disabled"),
    search: Optional[str] = Query(None, description="Search user name or email"),
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db),
):
    """Lists all user accounts in the system with optional role and status filters."""
    from app.routers.auth import format_user_profile

    query = db.query(User)
    if role:
        query = query.filter(User.role == role)
    if account_status:
        query = query.filter(User.account_status == account_status)
    if search:
        search_term = f"%{search.strip()}%"
        query = query.filter(or_(User.name.ilike(search_term), User.email.ilike(search_term)))

    users = query.order_by(User.created_at.desc()).all()
    return [format_user_profile(u) for u in users]


@router.patch(
    "/users/{user_id}/status",
    response_model=UserProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Enable or Disable User Account (Admin Only)",
)
def update_user_account_status(
    user_id: int,
    payload: UserStatusUpdate,
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db),
):
    """
    Approves a pending recruiter (-> 'active') or toggles an account between 'active' and 'disabled'.
    Disabled users are immediately prevented from authenticating or performing actions.
    Prevents an admin from accidentally disabling their own account.
    """
    if user_id == current_user.user_id and payload.account_status == "disabled":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot disable your own administrator account.",
        )

    target_user = db.query(User).filter(User.user_id == user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    target_user.account_status = payload.account_status
    db.commit()
    db.refresh(target_user)

    from app.routers.auth import format_user_profile
    return format_user_profile(target_user)


# ============================================================================
# 2. Institutional Oversight: Companies, Opportunities, Applications
# ============================================================================

@router.get(
    "/companies",
    response_model=List[CompanyRead],
    status_code=status.HTTP_200_OK,
    summary="List Partner Companies (Admin Only)",
)
def admin_list_companies(
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db),
):
    """Lists all registered partner companies for administrator review."""
    companies = db.query(Company).order_by(Company.company_name.asc()).all()
    return [CompanyRead.model_validate(c) for c in companies]


@router.get(
    "/opportunities",
    response_model=List[OpportunityDetailResponse],
    status_code=status.HTTP_200_OK,
    summary="List All Opportunities System-Wide (Admin Only)",
)
def admin_list_opportunities(
    status_filter: Optional[str] = Query(None, alias="status"),
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db),
):
    """Lists all opportunities across all companies regardless of status."""
    from app.routers.opportunities import format_opportunity_detail

    query = db.query(Opportunity)
    if status_filter:
        query = query.filter(Opportunity.status == status_filter)

    opps = query.order_by(Opportunity.created_at.desc()).all()
    return [format_opportunity_detail(o, current_user, db) for o in opps]


@router.get(
    "/applications",
    response_model=List[ApplicationDetailResponse],
    status_code=status.HTTP_200_OK,
    summary="List All Applications System-Wide (Admin Only)",
)
def admin_list_applications(
    status_filter: Optional[str] = Query(None, alias="status"),
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db),
):
    """Lists all student applications across the entire college."""
    from app.routers.applications import format_application_detail

    query = db.query(Application)
    if status_filter:
        query = query.filter(Application.status == status_filter)

    apps = query.order_by(Application.application_date.desc()).all()
    return [format_application_detail(a) for a in apps]


# ============================================================================
# 3. System-Wide Placement Analytics
# ============================================================================

@router.get(
    "/statistics",
    response_model=AdminDashboardStats,
    status_code=status.HTTP_200_OK,
    summary="Get System-Wide Placement Statistics (Admin Only)",
)
@router.get(
    "/stats",
    response_model=AdminDashboardStats,
    status_code=status.HTTP_200_OK,
    summary="Get System-Wide Placement Statistics Alias (Admin Only)",
)
def get_admin_system_statistics(
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db),
):
    """
    Computes real aggregate placement statistics from the SQLite database.
    No mock data: All numbers derive strictly from database rows.
    """
    # 1. User counts
    users = db.query(User).all()
    total_users = len(users)
    students_count = sum(1 for u in users if u.role == "student")
    recruiters_count = sum(1 for u in users if u.role == "recruiter")
    admins_count = sum(1 for u in users if u.role == "admin")

    # 2. Company count
    total_companies = db.query(Company).count()

    # 3. Opportunities breakdown
    opps = db.query(Opportunity).all()
    total_opps = len(opps)
    open_opps = sum(1 for o in opps if o.status == "open")
    closed_opps = sum(1 for o in opps if o.status == "closed")
    draft_opps = sum(1 for o in opps if o.status == "draft")

    # 4. Applications breakdown
    apps = db.query(Application).join(Application.student).all()
    total_apps = len(apps)

    status_counts = {
        "applied": 0,
        "under_review": 0,
        "shortlisted": 0,
        "interview": 0,
        "selected": 0,
        "rejected": 0,
    }
    dept_counts: Dict[str, int] = {}
    selected_students = set()

    for a in apps:
        if a.status in status_counts:
            status_counts[a.status] += 1
        dept = a.student.department if a.student else "Unknown"
        dept_counts[dept] = dept_counts.get(dept, 0) + 1

        if a.status == "selected":
            selected_students.add(a.student_id)

    # 5. Placement rate: % of total students placed
    placement_rate = 0.0
    if students_count > 0:
        placement_rate = round((len(selected_students) / students_count) * 100, 1)

    # 6. Top recruiting companies
    top_companies_data: List[Dict[str, Any]] = []
    companies = db.query(Company).all()
    for c in companies:
        c_opps = len(c.opportunities) if c.opportunities else 0
        c_apps = sum(len(o.applications) for o in c.opportunities) if c.opportunities else 0
        top_companies_data.append(
            {
                "company_id": c.company_id,
                "company_name": c.company_name,
                "opportunities_count": c_opps,
                "applications_count": c_apps,
            }
        )
    top_companies_data.sort(key=lambda x: (x["opportunities_count"], x["applications_count"]), reverse=True)
    top_companies_data = top_companies_data[:5]

    return AdminDashboardStats(
        total_users=total_users,
        students_count=students_count,
        recruiters_count=recruiters_count,
        admins_count=admins_count,
        total_companies=total_companies,
        total_opportunities=total_opps,
        open_opportunities=open_opps,
        closed_opportunities=closed_opps,
        draft_opportunities=draft_opps,
        total_applications=total_apps,
        applications_by_status=status_counts,
        applications_by_department=dept_counts,
        placement_rate=placement_rate,
        top_companies=top_companies_data,
    )
