"""
Opportunity endpoints: Browse, search, filter, create, update, and status controls.
"""
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.auth import get_current_active_user, oauth2_scheme, require_role, decode_access_token
from app.database import get_db
from app.models import Application, Company, Opportunity, Student, User
from app.schemas import (
    CompanyRead,
    OpportunityCreateByRecruiter,
    OpportunityDetailResponse,
    OpportunityStatusUpdate,
    OpportunityUpdate,
)

router = APIRouter(prefix="/api/opportunities", tags=["Opportunities"])


def get_optional_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """Optional authentication dependency: returns User if valid token is provided, else None."""
    if not token:
        return None
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if user_id:
            return db.query(User).filter(User.user_id == int(user_id)).first()
    except Exception:
        return None
    return None


def format_opportunity_detail(
    opp: Opportunity,
    current_user: Optional[User] = None,
    db: Optional[Session] = None,
) -> OpportunityDetailResponse:
    """Helper to convert Opportunity model into OpportunityDetailResponse with context."""
    has_applied = False
    is_eligible = True

    if current_user and current_user.role == "student" and current_user.student_profile and db:
        student = current_user.student_profile
        is_eligible = student.cgpa >= opp.eligibility_cgpa
        app_exists = (
            db.query(Application)
            .filter(
                Application.student_id == student.student_id,
                Application.opportunity_id == opp.opportunity_id,
            )
            .first()
        )
        has_applied = app_exists is not None

    app_count = len(opp.applications) if opp.applications is not None else 0

    return OpportunityDetailResponse(
        opportunity_id=opp.opportunity_id,
        company_id=opp.company_id,
        title=opp.title,
        opportunity_type=opp.opportunity_type,
        description=opp.description,
        location=opp.location,
        salary_stipend=opp.salary_stipend,
        deadline=opp.deadline,
        eligibility_cgpa=opp.eligibility_cgpa,
        status=opp.status,
        created_at=opp.created_at,
        company=CompanyRead.model_validate(opp.company),
        has_applied=has_applied,
        is_eligible=is_eligible,
        application_count=app_count,
    )


@router.get(
    "",
    response_model=List[OpportunityDetailResponse],
    status_code=status.HTTP_200_OK,
    summary="Browse and Search Opportunities",
)
def list_opportunities(
    search: Optional[str] = Query(None, description="Search keyword in title or description"),
    opportunity_type: Optional[str] = Query(None, description="Filter by type (internship, full_time, part_time)"),
    location: Optional[str] = Query(None, description="Filter by location"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status (open, closed, draft)"),
    eligible_only: bool = Query(False, description="Filter for opportunities matching student CGPA"),
    company_id: Optional[int] = Query(None, description="Filter by specific company"),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    """
    Lists opportunities with search and filter capabilities.
    For unauthenticated users and students, defaults to 'open' opportunities.
    """
    query = db.query(Opportunity).join(Opportunity.company)

    # Status filter logic
    if status_filter:
        query = query.filter(Opportunity.status == status_filter)
    elif not current_user or current_user.role == "student":
        query = query.filter(Opportunity.status == "open")

    if company_id:
        query = query.filter(Opportunity.company_id == company_id)

    if opportunity_type:
        query = query.filter(Opportunity.opportunity_type == opportunity_type)

    if location:
        query = query.filter(Opportunity.location.ilike(f"%{location.strip()}%"))

    if search:
        search_term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Opportunity.title.ilike(search_term),
                Opportunity.description.ilike(search_term),
                Company.company_name.ilike(search_term),
            )
        )

    # CGPA eligibility filter
    if eligible_only and current_user and current_user.role == "student" and current_user.student_profile:
        student_cgpa = current_user.student_profile.cgpa
        query = query.filter(Opportunity.eligibility_cgpa <= student_cgpa)

    query = query.order_by(Opportunity.created_at.desc())
    opportunities = query.all()

    return [format_opportunity_detail(opp, current_user, db) for opp in opportunities]


@router.get(
    "/{opportunity_id}",
    response_model=OpportunityDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Opportunity Details",
)
def get_opportunity(
    opportunity_id: int,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    """Retrieves full details for a single opportunity."""
    opp = db.query(Opportunity).filter(Opportunity.opportunity_id == opportunity_id).first()
    if not opp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found.",
        )
    return format_opportunity_detail(opp, current_user, db)


@router.post(
    "",
    response_model=OpportunityDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Opportunity (Recruiters Only)",
)
def create_opportunity(
    payload: OpportunityCreateByRecruiter,
    current_user: User = Depends(require_role(["recruiter"])),
    db: Session = Depends(get_db),
):
    """
    Allows a recruiter to post a new job or internship.
    Company association is strictly established from the recruiter's account.
    """
    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Recruiter account is not associated with any company.",
        )

    # Ensure deadline is in the future
    deadline_utc = payload.deadline
    if deadline_utc.tzinfo is None:
        deadline_utc = deadline_utc.replace(tzinfo=timezone.utc)
    now_utc = datetime.now(timezone.utc)
    if deadline_utc <= now_utc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Application deadline must be a future date and time.",
        )

    new_opp = Opportunity(
        company_id=current_user.company_id,
        title=payload.title.strip(),
        opportunity_type=payload.opportunity_type,
        description=payload.description.strip(),
        location=payload.location.strip() if payload.location else None,
        salary_stipend=payload.salary_stipend,
        deadline=payload.deadline,
        eligibility_cgpa=round(payload.eligibility_cgpa, 2),
        status=payload.status,
    )
    db.add(new_opp)
    db.commit()
    db.refresh(new_opp)

    return format_opportunity_detail(new_opp, current_user, db)


@router.put(
    "/{opportunity_id}",
    response_model=OpportunityDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Opportunity (Recruiters Only)",
)
def update_opportunity(
    opportunity_id: int,
    payload: OpportunityUpdate,
    current_user: User = Depends(require_role(["recruiter", "admin"])),
    db: Session = Depends(get_db),
):
    """
    Updates an opportunity's details.
    Enforces that recruiters can only update opportunities belonging to their own company.
    """
    opp = db.query(Opportunity).filter(Opportunity.opportunity_id == opportunity_id).first()
    if not opp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found.",
        )

    # Cross-company ownership check
    if current_user.role == "recruiter" and opp.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to modify opportunities belonging to another company.",
        )

    if payload.title is not None:
        opp.title = payload.title.strip()
    if payload.opportunity_type is not None:
        opp.opportunity_type = payload.opportunity_type
    if payload.description is not None:
        opp.description = payload.description.strip()
    if payload.location is not None:
        opp.location = payload.location.strip()
    if payload.salary_stipend is not None:
        opp.salary_stipend = payload.salary_stipend
    if payload.deadline is not None:
        opp.deadline = payload.deadline
    if payload.eligibility_cgpa is not None:
        opp.eligibility_cgpa = round(payload.eligibility_cgpa, 2)
    if payload.status is not None:
        opp.status = payload.status

    db.commit()
    db.refresh(opp)

    return format_opportunity_detail(opp, current_user, db)


@router.patch(
    "/{opportunity_id}/status",
    response_model=OpportunityDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Change Opportunity Status (Open/Close)",
)
def change_opportunity_status(
    opportunity_id: int,
    payload: OpportunityStatusUpdate,
    current_user: User = Depends(require_role(["recruiter", "admin"])),
    db: Session = Depends(get_db),
):
    """
    Opens, closes, or sets an opportunity to draft.
    Prefers closing opportunities over deleting historical records.
    """
    opp = db.query(Opportunity).filter(Opportunity.opportunity_id == opportunity_id).first()
    if not opp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found.",
        )

    if current_user.role == "recruiter" and opp.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update opportunities belonging to another company.",
        )

    opp.status = payload.status
    db.commit()
    db.refresh(opp)

    return format_opportunity_detail(opp, current_user, db)
