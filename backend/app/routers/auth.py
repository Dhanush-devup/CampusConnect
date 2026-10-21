"""
Authentication endpoints: Registration, Login, Token generation, and Current User profile.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import (
    create_access_token,
    get_current_active_user,
    hash_password,
    verify_password,
)
from app.database import get_db
from app.models import Company, Student, User
from app.schemas import (
    CompanyRead,
    LoginRequest,
    RecruiterRegisterRequest,
    StudentRead,
    StudentRegisterRequest,
    TokenResponse,
    UserProfileResponse,
)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


def format_user_profile(user: User) -> UserProfileResponse:
    """Format SQLAlchemy User model into a complete UserProfileResponse."""
    student_data = None
    if user.student_profile:
        student_data = StudentRead.model_validate(user.student_profile)

    company_data = None
    if user.company:
        company_data = CompanyRead.model_validate(user.company)

    return UserProfileResponse(
        user_id=user.user_id,
        name=user.name,
        email=user.email,
        role=user.role,
        account_status=user.account_status,
        company_id=user.company_id,
        created_at=user.created_at,
        student_profile=student_data,
        company=company_data,
    )


@router.post(
    "/register/student",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Student Registration",
)
def register_student(
    payload: StudentRegisterRequest,
    db: Session = Depends(get_db),
):
    """
    Registers a new student. Atomically creates both the User and Student records
    within a single database transaction. Prevents public admin registration.
    """
    # 1. Check email uniqueness
    existing_user = db.query(User).filter(User.email == payload.email.lower().strip()).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists.",
        )

    # 2. Hash password
    hashed_pwd = hash_password(payload.password)

    # 3. Create User record
    new_user = User(
        name=payload.name.strip(),
        email=payload.email.lower().strip(),
        password_hash=hashed_pwd,
        role="student",
        account_status="active",
        company_id=None,
    )
    db.add(new_user)
    db.flush()  # Generates new_user.user_id within transaction

    # 4. Create Student profile record
    new_student = Student(
        user_id=new_user.user_id,
        department=payload.department.strip(),
        cgpa=round(payload.cgpa, 2),
        graduation_year=payload.graduation_year,
    )
    db.add(new_student)
    db.commit()
    db.refresh(new_user)

    # 5. Issue JWT access token
    token = create_access_token(
        data={
            "sub": str(new_user.user_id),
            "email": new_user.email,
            "role": new_user.role,
            "name": new_user.name,
        }
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=format_user_profile(new_user),
    )


@router.post(
    "/register/recruiter",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Recruiter & Company Registration",
)
def register_recruiter(
    payload: RecruiterRegisterRequest,
    db: Session = Depends(get_db),
):
    """
    Registers a new recruiter account along with their company profile
    in a single atomic database transaction.
    """
    # 1. Check user email uniqueness
    existing_user = db.query(User).filter(User.email == payload.email.lower().strip()).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists.",
        )

    # 2. Create Company profile
    new_company = Company(
        company_name=payload.company_name.strip(),
        email=payload.company_email.lower().strip(),
        phone=payload.phone.strip() if payload.phone else None,
        industry=payload.industry.strip() if payload.industry else None,
        location=payload.location.strip() if payload.location else None,
        website=payload.website.strip() if payload.website else None,
    )
    db.add(new_company)
    db.flush()  # Generates new_company.company_id within transaction

    # 3. Create Recruiter User record
    hashed_pwd = hash_password(payload.password)
    new_user = User(
        name=payload.name.strip(),
        email=payload.email.lower().strip(),
        password_hash=hashed_pwd,
        role="recruiter",
        account_status="active",
        company_id=new_company.company_id,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # 4. Issue JWT access token
    token = create_access_token(
        data={
            "sub": str(new_user.user_id),
            "email": new_user.email,
            "role": new_user.role,
            "name": new_user.name,
        }
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=format_user_profile(new_user),
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Account Login",
)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db),
):
    """
    Authenticates a user with email and password.
    Blocks disabled accounts and returns a signed JWT access token.
    """
    user = db.query(User).filter(User.email == payload.email.lower().strip()).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Disabled account check
    if user.account_status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been disabled. Please contact the administrator.",
        )

    # Issue JWT token
    token = create_access_token(
        data={
            "sub": str(user.user_id),
            "email": user.email,
            "role": user.role,
            "name": user.name,
        }
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=format_user_profile(user),
    )


@router.get(
    "/me",
    response_model=UserProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Current Authenticated User",
)
def get_current_user_profile(
    current_user: User = Depends(get_current_active_user),
):
    """
    Returns the profile and role details of the currently authenticated active user.
    """
    return format_user_profile(current_user)


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="User Logout",
)
def logout():
    """
    Logs out the current user. In a stateless Bearer token strategy,
    the client purges the stored access token upon receipt of this response.
    """
    return {"message": "Logged out successfully."}
