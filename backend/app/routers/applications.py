"""
Application management and secure resume handling endpoints.
Enforces CGPA eligibility, deadline checks, duplicate application prevention,
cross-company recruiter restrictions, and authorized file downloads.
"""
from datetime import datetime, timezone
import os
from pathlib import Path
from typing import List, Optional
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.auth import get_current_active_user, require_role
from app.config import get_settings
from app.database import get_db
from app.models import Application, Company, Opportunity, Student, User
from app.schemas import (
    ApplicationDetailResponse,
    ApplicationStatusUpdate,
)

settings = get_settings()
router = APIRouter(prefix="/api", tags=["Applications"])


def get_upload_dir() -> Path:
    """Ensures the resume upload directory exists and returns its canonical Path."""
    upload_path = Path(settings.UPLOAD_DIR).resolve()
    upload_path.mkdir(parents=True, exist_ok=True)
    return upload_path


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
    resume: Optional[UploadFile] = File(None),
    current_user: User = Depends(require_role(["student"])),
    db: Session = Depends(get_db),
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
    if not opp:
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
    Recruiters can only update candidates for their own company's opportunities.
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
    file: UploadFile = File(...),
    current_user: User = Depends(require_role(["student"])),
    db: Session = Depends(get_db),
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

    # Delete old file if present
    if app.resume_path and os.path.exists(app.resume_path):
        try:
            os.remove(app.resume_path)
        except OSError:
            pass

    with open(dest_path, "wb") as f:
        f.write(content)

    app.resume_path = str(dest_path)
    db.commit()

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

    # Access authorization check
    is_owner_student = (
        current_user.role == "student"
        and current_user.student_profile
        and app.student_id == current_user.student_profile.student_id
    )
    is_hiring_recruiter = (
        current_user.role == "recruiter"
        and current_user.company_id is not None
        and app.opportunity.company_id == current_user.company_id
    )
    is_admin = current_user.role == "admin"

    if not (is_owner_student or is_hiring_recruiter or is_admin):
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
