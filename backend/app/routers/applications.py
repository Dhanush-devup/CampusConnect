"""
Application management and secure resume handling endpoints.
Enforces CGPA eligibility, deadline checks, duplicate application prevention,
cross-company recruiter restrictions, and authorized file downloads.
"""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
from typing import List, Optional
import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session, sessionmaker

from app.ats_scoring import mark_pending, score_application
from app.auth import get_current_active_user, require_role
from app.config import get_settings
from app.database import get_db, get_session_factory
from app.models import Application, Company, Opportunity, Student, User
from app.schemas import (
    APPLICATION_STATUS_TRANSITIONS,
    ApplicationDetailResponse,
    ApplicationStatusUpdate,
    ResumeScoreResponse,
)

settings = get_settings()
router = APIRouter(prefix="/api", tags=["Applications"])


def get_upload_dir() -> Path:
    """Ensures the resume upload directory exists and returns its canonical Path."""
    upload_path = Path(settings.UPLOAD_DIR).resolve()
    upload_path.mkdir(parents=True, exist_ok=True)
    return upload_path


def can_view_application(user: User, app: Application) -> bool:
    """The applying student, recruiters of the hiring company, and admins may view an application's resume and score."""
    if user.role == "admin":
        return True
    if user.role == "student":
        return user.student_profile is not None and app.student_id == user.student_profile.student_id
    if user.role == "recruiter":
        return user.company_id is not None and app.opportunity.company_id == user.company_id
    return False


def schedule_scoring(
    db: Session,
    app: Application,
    background_tasks: BackgroundTasks,
    session_factory: sessionmaker,
) -> None:
    """Marks the application's ATS score as pending and scores the resume after the response is sent."""
    mark_pending(db, app)
    background_tasks.add_task(score_application, app.application_id, session_factory)


def format_application_detail(app: Application) -> ApplicationDetailResponse:
    """Converts Application model and its relationships into ApplicationDetailResponse."""
    student = app.student
    student_user = student.user
    opp = app.opportunity
    company = opp.company

    return ApplicationDetailResponse(
        application_id=app.application_id,
        student_id=app.student_id,
        opportunity_id=app.opportunity_id,
        application_date=app.application_date,
        status=app.status,
        resume_path=app.resume_path,
        student_name=student_user.name,
        student_email=student_user.email,
        student_department=student.department,
        student_cgpa=student.cgpa,
        student_graduation_year=student.graduation_year,
        opportunity_title=opp.title,
        opportunity_type=opp.opportunity_type,
        opportunity_location=opp.location,
        salary_stipend=opp.salary_stipend,
        deadline=opp.deadline,
        company_name=company.company_name,
        company_location=company.location,
        ats_score=app.resume_score.overall_score if app.resume_score else None,
        ats_status=app.resume_score.status if app.resume_score else None,
    )


# ============================================================================
# 1. Student Application Submission & Listing
# ============================================================================

@router.post(
    "/opportunities/{opportunity_id}/apply",
    response_model=ApplicationDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit Application (Students Only)",
)
async def apply_to_opportunity(
    opportunity_id: int,
    background_tasks: BackgroundTasks,
    resume: Optional[UploadFile] = File(None),
    current_user: User = Depends(require_role(["student"])),
    db: Session = Depends(get_db),
    session_factory: sessionmaker = Depends(get_session_factory),
):
    """
    Submits an application for an eligible opportunity.
    Strictly verifies:
    - Account is active and student profile exists
    - Opportunity exists, is 'open', and deadline has not passed
    - Student's CGPA satisfies the opportunity's eligibility requirement
    - Student has not already applied
    - Optional resume upload is validated for PDF type and <= 5MB size
    """
    student = current_user.student_profile
    if not student:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student profile not found. Please complete your profile before applying.",
        )

    # 1. Check opportunity validity
    opp = db.query(Opportunity).filter(Opportunity.opportunity_id == opportunity_id).first()
    if not opp or opp.status == "draft":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found.",
        )

    if opp.status != "open":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"This opportunity is currently {opp.status} and not accepting applications.",
        )

    # 2. Check application deadline
    deadline_utc = opp.deadline
    if deadline_utc.tzinfo is None:
        deadline_utc = deadline_utc.replace(tzinfo=timezone.utc)
    if deadline_utc < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The application deadline for this opportunity has passed.",
        )

    # 3. Check CGPA eligibility
    if student.cgpa < opp.eligibility_cgpa:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Your CGPA ({student.cgpa:.2f}) does not meet the minimum requirement "
                f"({opp.eligibility_cgpa:.2f}) for this opportunity."
            ),
        )

    # 4. Check duplicate application
    existing_app = (
        db.query(Application)
        .filter(
            Application.student_id == student.student_id,
            Application.opportunity_id == opp.opportunity_id,
        )
        .first()
    )
    if existing_app:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already applied for this opportunity.",
        )

    # 5. Handle optional resume upload
    saved_resume_path = None
    if resume and resume.filename:
        # Validate file type
        if not (resume.filename.lower().endswith(".pdf") or resume.content_type == "application/pdf"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid resume format. Only PDF files are accepted.",
            )

        content = await resume.read()
        if len(content) > settings.MAX_RESUME_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Resume file size exceeds the 5 MB limit ({len(content) / (1024*1024):.1f} MB provided).",
            )

        # Generate safe unique filename
        safe_filename = f"resume_std_{student.student_id}_opp_{opp.opportunity_id}_{uuid.uuid4().hex[:8]}.pdf"
        upload_dir = get_upload_dir()
        dest_path = upload_dir / safe_filename

        with open(dest_path, "wb") as f:
            f.write(content)

        saved_resume_path = str(dest_path)

    # 6. Create application record
    new_app = Application(
        student_id=student.student_id,
        opportunity_id=opp.opportunity_id,
        status="applied",
        resume_path=saved_resume_path,
    )
    db.add(new_app)
    db.commit()
    db.refresh(new_app)

    if saved_resume_path:
        schedule_scoring(db, new_app, background_tasks, session_factory)

    return format_application_detail(new_app)


@router.get(
    "/students/applications",
    response_model=List[ApplicationDetailResponse],
    status_code=status.HTTP_200_OK,
    summary="List Student's Applications",
)
def list_student_applications(
    current_user: User = Depends(require_role(["student"])),
    db: Session = Depends(get_db),
):
    """Retrieves all applications submitted by the authenticated student."""
    student = current_user.student_profile
    if not student:
        return []

    applications = (
        db.query(Application)
        .filter(Application.student_id == student.student_id)
        .order_by(Application.application_date.desc())
        .all()
    )
    return [format_application_detail(app) for app in applications]


# ============================================================================
# 2. Recruiter Application Management
# ============================================================================

@router.get(
    "/recruiters/applications",
    response_model=List[ApplicationDetailResponse],
    status_code=status.HTTP_200_OK,
    summary="List Company Applications (Recruiters Only)",
)
def list_recruiter_applications(
    opportunity_id: Optional[int] = Query(None, description="Filter by opportunity ID"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status"),
    department: Optional[str] = Query(None, description="Filter by student department"),
    current_user: User = Depends(require_role(["recruiter"])),
    db: Session = Depends(get_db),
):
    """
    Lists applications received for opportunities posted by the recruiter's company.
    Guarantees cross-company isolation: recruiters cannot view other companies' applicants.
    """
    if not current_user.company_id:
        return []

    query = (
        db.query(Application)
        .join(Application.opportunity)
        .join(Application.student)
        .filter(Opportunity.company_id == current_user.company_id)
    )

    if opportunity_id:
        query = query.filter(Application.opportunity_id == opportunity_id)

    if status_filter:
        query = query.filter(Application.status == status_filter)

    if department:
        query = query.filter(Student.department.ilike(f"%{department.strip()}%"))

    query = query.order_by(Application.application_date.desc())
    applications = query.all()

    return [format_application_detail(app) for app in applications]


@router.patch(
    "/applications/{application_id}/status",
    response_model=ApplicationDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Application Status (Recruiters & Admins Only)",
)
def update_application_status(
    application_id: int,
    payload: ApplicationStatusUpdate,
    current_user: User = Depends(require_role(["recruiter", "admin"])),
    db: Session = Depends(get_db),
):
    """
    Updates the hiring status of an application.
    Students cannot alter their own status.
    Recruiters can only update candidates for their own company's opportunities,
    and only along the pipeline in APPLICATION_STATUS_TRANSITIONS. Admins may override.
    """
    app = db.query(Application).filter(Application.application_id == application_id).first()
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found.",
        )

    # Cross-company security check
    if current_user.role == "recruiter":
        if app.opportunity.company_id != current_user.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot update applications belonging to another company.",
            )

        allowed = APPLICATION_STATUS_TRANSITIONS.get(app.status, [])
        if payload.status != app.status and payload.status not in allowed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Cannot move an application from '{app.status}' to '{payload.status}'. "
                    f"Allowed next statuses: {', '.join(allowed) or 'none (final status)'}."
                ),
            )

    app.status = payload.status
    db.commit()
    db.refresh(app)

    return format_application_detail(app)


# ============================================================================
# 3. Resume Upload & Secure Download
# ============================================================================

@router.post(
    "/applications/{application_id}/resume",
    status_code=status.HTTP_200_OK,
    summary="Upload or Replace Application Resume",
)
async def upload_application_resume(
    application_id: int,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: User = Depends(require_role(["student"])),
    db: Session = Depends(get_db),
    session_factory: sessionmaker = Depends(get_session_factory),
):
    """
    Allows a student to upload or replace the resume for their existing application.
    Enforces PDF format, <= 5MB size limit, and path safety.
    """
    student = current_user.student_profile
    if not student:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student profile not found.",
        )

    app = db.query(Application).filter(Application.application_id == application_id).first()
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found.",
        )

    if app.student_id != student.student_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only manage resumes for your own applications.",
        )

    # Validate PDF
    if not (file.filename.lower().endswith(".pdf") or file.content_type == "application/pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Only PDF files are accepted.",
        )

    content = await file.read()
    if len(content) > settings.MAX_RESUME_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Resume file size exceeds the 5 MB limit ({len(content) / (1024*1024):.1f} MB provided).",
        )

    # Generate safe unique filename
    safe_filename = f"resume_std_{student.student_id}_app_{app.application_id}_{uuid.uuid4().hex[:8]}.pdf"
    upload_dir = get_upload_dir()
    dest_path = upload_dir / safe_filename

    # Delete the old file if present and no other application uses it (seeded demo data shares one file)
    shared = (
        db.query(Application)
        .filter(Application.resume_path == app.resume_path, Application.application_id != app.application_id)
        .first()
    )
    if app.resume_path and not shared and os.path.exists(app.resume_path):
        try:
            os.remove(app.resume_path)
        except OSError:
            pass

    with open(dest_path, "wb") as f:
        f.write(content)

    app.resume_path = str(dest_path)
    db.commit()
    schedule_scoring(db, app, background_tasks, session_factory)

    return {
        "message": "Resume uploaded successfully.",
        "application_id": app.application_id,
        "resume_path": app.resume_path,
    }


@router.get(
    "/applications/{application_id}/resume",
    summary="Download / View Application Resume",
)
def download_application_resume(
    application_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Secure resume download with role-based access control.
    Authorized viewers:
    - The student who submitted the application
    - The recruiter belonging to the hiring company
    - System administrator
    Guards against path traversal attacks.
    """
    app = db.query(Application).filter(Application.application_id == application_id).first()
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found.",
        )

    if not app.resume_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No resume has been uploaded for this application.",
        )

    if not can_view_application(current_user, app):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to access this resume.",
        )

    # Path traversal protection
    upload_dir = get_upload_dir()
    resolved_file_path = Path(app.resume_path).resolve()

    # Verify that resolved_file_path is strictly within upload_dir
    try:
        resolved_file_path.relative_to(upload_dir)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid file path detected.",
        )

    if not resolved_file_path.exists() or not resolved_file_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume file could not be found on the server.",
        )

    clean_download_name = f"{app.student.user.name.replace(' ', '_')}_Resume.pdf"

    return FileResponse(
        path=str(resolved_file_path),
        media_type="application/pdf",
        filename=clean_download_name,
    )


# ============================================================================
# 4. ATS Resume Score
# ============================================================================

def get_viewable_application(application_id: int, current_user: User, db: Session) -> Application:
    app = db.query(Application).filter(Application.application_id == application_id).first()
    if not app:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found.")
    if not can_view_application(current_user, app):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view this application.",
        )
    return app


def format_resume_score(app: Application) -> ResumeScoreResponse:
    record = app.resume_score

    def as_list(value: Optional[str]) -> List[str]:
        return json.loads(value) if value else []

    return ResumeScoreResponse(
        application_id=app.application_id,
        status=record.status,
        overall_score=record.overall_score,
        skills_score=record.skills_score,
        experience_score=record.experience_score,
        education_score=record.education_score,
        formatting_score=record.formatting_score,
        matched_skills=as_list(record.matched_skills),
        missing_skills=as_list(record.missing_skills),
        strengths=as_list(record.strengths),
        improvements=as_list(record.improvements),
        flags=as_list(record.flags),
        summary=record.summary,
        scored_by=record.scored_by,
        error_message=record.error_message,
        updated_at=record.updated_at,
    )


@router.get(
    "/applications/{application_id}/ats-score",
    response_model=ResumeScoreResponse,
    status_code=status.HTTP_200_OK,
    summary="Get ATS Resume Score Report",
)
def get_ats_score(
    application_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Returns the ATS score report for an application's resume.
    Visible to the applying student, the hiring company's recruiters, and admins.
    """
    app = get_viewable_application(application_id, current_user, db)
    if not app.resume_score:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This resume has not been scored yet.",
        )
    return format_resume_score(app)


@router.post(
    "/applications/{application_id}/ats-score",
    response_model=ResumeScoreResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Score or Re-score an Application's Resume",
)
def request_ats_score(
    application_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    session_factory: sessionmaker = Depends(get_session_factory),
):
    """
    Queues ATS scoring for an application's resume (e.g. resumes uploaded before
    scoring existed, or after a failure). Returns the pending score record.
    """
    app = get_viewable_application(application_id, current_user, db)
    if not app.resume_path:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No resume has been uploaded for this application.",
        )
    if app.resume_score and app.resume_score.status == "pending":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This resume is already being scored.",
        )
    schedule_scoring(db, app, background_tasks, session_factory)
    db.refresh(app)
    return format_resume_score(app)
