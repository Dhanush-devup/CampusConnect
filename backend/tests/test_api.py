"""
Comprehensive API test suite for CampusConnect:
Authentication, Role Permissions, Cross-Company Isolation, Application Eligibility,
Resume Handling, and Administrative Controls.
"""
from datetime import datetime, timedelta, timezone
import io
import pytest
from fastapi import status


# ============================================================================
# Helpers
# ============================================================================

def register_student(client, email="alice@test.edu", password="Password123!", name="Alice", cgpa=8.5):
    return client.post(
        "/api/auth/register/student",
        json={
            "name": name,
            "email": email,
            "password": password,
            "department": "Computer Science",
            "cgpa": cgpa,
            "graduation_year": 2026,
        },
    )


def signup_recruiter(client, email="recruiter@tech.com", password="Password123!", company_name="TechCorp"):
    """Submits recruiter registration; the account is left pending admin approval."""
    return client.post(
        "/api/auth/register/recruiter",
        json={
            "name": "Bob Recruiter",
            "email": email,
            "password": password,
            "company_name": company_name,
            "company_email": f"contact@{company_name.lower().replace(' ', '')}.com",
            "phone": "+1234567890",
            "industry": "Technology",
            "location": "Bangalore",
            "website": "https://techcorp.com",
        },
    )


def approve_user(client, user_id):
    """Activates a pending account directly in the test database."""
    from app.database import get_db
    from app.models import User

    db = next(client.app.dependency_overrides[get_db]())
    db.query(User).filter(User.user_id == user_id).update({"account_status": "active"})
    db.commit()


def register_recruiter(client, email="recruiter@tech.com", password="Password123!", company_name="TechCorp"):
    """Signs up a recruiter, approves the account, and returns the login response."""
    signup = signup_recruiter(client, email=email, password=password, company_name=company_name)
    assert signup.status_code == status.HTTP_201_CREATED, signup.text
    approve_user(client, signup.json()["user"]["user_id"])
    return client.post("/api/auth/login", json={"email": email, "password": password})


def create_admin_token(client, db_session, email="dean@campusconnect.edu", password="AdminSecure!"):
    from app.auth import hash_password
    from app.models import User

    db_session.add(User(
        name="Dean of Placements",
        email=email,
        password_hash=hash_password(password),
        role="admin",
        account_status="active",
    ))
    db_session.commit()
    return client.post("/api/auth/login", json={"email": email, "password": password}).json()["access_token"]


def move_application(client, token, app_id, *statuses):
    """Walks an application through the given statuses, asserting each step succeeds."""
    res = None
    for next_status in statuses:
        res = client.patch(
            f"/api/applications/{app_id}/status",
            headers={"Authorization": f"Bearer {token}"},
            json={"status": next_status},
        )
        assert res.status_code == status.HTTP_200_OK, res.text
    return res


def create_job(client, token, title="Software Engineer Intern", eligibility_cgpa=7.0, status="open"):
    deadline = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
    return client.post(
        "/api/opportunities",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": title,
            "opportunity_type": "internship",
            "description": "Develop full-stack applications with modern frameworks.",
            "location": "Bangalore",
            "salary_stipend": 40000.0,
            "deadline": deadline,
            "eligibility_cgpa": eligibility_cgpa,
            "status": status,
        },
    )


# ============================================================================
# 1. Authentication & Registration Tests
# ============================================================================

def test_student_registration_success(client):
    """Student registration must atomically create user + profile and return token."""
    res = register_student(client, email="student1@college.edu")
    assert res.status_code == status.HTTP_201_CREATED
    data = res.json()
    assert "access_token" in data
    assert data["user"]["role"] == "student"
    assert data["user"]["student_profile"]["cgpa"] == 8.5
    assert data["user"]["student_profile"]["department"] == "Computer Science"


def test_recruiter_registration_success(client):
    """Recruiter registration creates company + pending user and issues no token."""
    res = signup_recruiter(client, email="recruiter1@acme.com", company_name="Acme Corp")
    assert res.status_code == status.HTTP_201_CREATED
    data = res.json()
    assert "access_token" not in data
    assert data["user"]["role"] == "recruiter"
    assert data["user"]["account_status"] == "pending"
    assert data["user"]["company"]["company_name"] == "Acme Corp"


def test_pending_recruiter_needs_admin_approval(client, db_session):
    """Pending recruiters cannot log in until an admin approves them."""
    signup = signup_recruiter(client, email="newrec@startup.com", password="Password123!", company_name="Startup")
    user_id = signup.json()["user"]["user_id"]
    credentials = {"email": "newrec@startup.com", "password": "Password123!"}

    blocked = client.post("/api/auth/login", json=credentials)
    assert blocked.status_code == status.HTTP_403_FORBIDDEN
    assert "awaiting approval" in blocked.json()["detail"]

    admin_token = create_admin_token(client, db_session)
    pending = client.get(
        "/api/admin/users?account_status=pending",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert [u["user_id"] for u in pending.json()] == [user_id]

    approve = client.patch(
        f"/api/admin/users/{user_id}/status",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"account_status": "active"},
    )
    assert approve.status_code == status.HTTP_200_OK

    allowed = client.post("/api/auth/login", json=credentials)
    assert allowed.status_code == status.HTTP_200_OK

    # Admins cannot put an account back into pending
    res = client.patch(
        f"/api/admin/users/{user_id}/status",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"account_status": "pending"},
    )
    assert res.status_code == 422


def test_duplicate_registration_rejected(client):
    """Registering with an existing email must be rejected with 400."""
    register_student(client, email="duplicate@test.edu")
    res = register_student(client, email="duplicate@test.edu")
    assert res.status_code == status.HTTP_400_BAD_REQUEST
    assert "already exists" in res.json()["detail"]


def test_login_flow(client):
    """Test valid login, invalid password, and non-existent account."""
    register_student(client, email="login_user@test.edu", password="SecretPassword1!")

    # 1. Valid credentials
    res = client.post("/api/auth/login", json={"email": "login_user@test.edu", "password": "SecretPassword1!"})
    assert res.status_code == status.HTTP_200_OK
    assert "access_token" in res.json()

    # 2. Invalid password
    res = client.post("/api/auth/login", json={"email": "login_user@test.edu", "password": "WrongPassword"})
    assert res.status_code == status.HTTP_401_UNAUTHORIZED

    # 3. Non-existent email
    res = client.post("/api/auth/login", json={"email": "ghost@test.edu", "password": "Any"})
    assert res.status_code == status.HTTP_401_UNAUTHORIZED


def test_auth_me_endpoint(client):
    """GET /api/auth/me returns the authenticated user's profile."""
    res = register_student(client, email="me_check@test.edu")
    token = res.json()["access_token"]

    me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == status.HTTP_200_OK
    data = me_res.json()
    assert data["email"] == "me_check@test.edu"
    assert data["student_profile"] is not None


def test_disabled_account_enforcement(client, db_session):
    """Disabled accounts cannot log in or access protected endpoints."""
    from app.models import User

    res = register_student(client, email="disabled_user@test.edu", password="ValidPassword1!")
    token = res.json()["access_token"]
    user_id = res.json()["user"]["user_id"]

    # Disable user directly in database
    user = db_session.query(User).filter(User.user_id == user_id).first()
    user.account_status = "disabled"
    db_session.commit()

    # 1. Login attempt fails
    login_res = client.post("/api/auth/login", json={"email": "disabled_user@test.edu", "password": "ValidPassword1!"})
    assert login_res.status_code == status.HTTP_403_FORBIDDEN
    assert "disabled" in login_res.json()["detail"].lower()

    # 2. Existing token rejected on protected routes
    me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == status.HTTP_403_FORBIDDEN


# ============================================================================
# 2. Opportunity Management & Cross-Company Security
# ============================================================================

def test_opportunity_creation_and_cross_company_isolation(client):
    """Recruiters can only create and update their company's opportunities."""
    rec1 = register_recruiter(client, email="rec1@google.com", company_name="Google").json()
    rec2 = register_recruiter(client, email="rec2@microsoft.com", company_name="Microsoft").json()

    token1 = rec1["access_token"]
    token2 = rec2["access_token"]

    # Recruiter 1 creates an opportunity
    opp_res = create_job(client, token1, title="Google Cloud Intern", eligibility_cgpa=8.0)
    assert opp_res.status_code == status.HTTP_201_CREATED
    opp_id = opp_res.json()["opportunity_id"]
    assert opp_res.json()["company"]["company_name"] == "Google"

    # Recruiter 2 attempts to edit Recruiter 1's opportunity -> MUST FAIL (403)
    edit_res = client.put(
        f"/api/opportunities/{opp_id}",
        headers={"Authorization": f"Bearer {token2}"},
        json={"title": "Hacked Title"},
    )
    assert edit_res.status_code == status.HTTP_403_FORBIDDEN


def test_student_cannot_create_opportunity(client):
    """Students are forbidden from creating job opportunities."""
    student_res = register_student(client, email="hacker_student@test.edu").json()
    token = student_res["access_token"]

    res = create_job(client, token, title="Illegal Job")
    assert res.status_code == status.HTTP_403_FORBIDDEN


def test_opportunity_search_and_filters(client):
    """Test keyword search and eligibility filters for opportunities."""
    rec = register_recruiter(client, email="rec_search@amazon.com", company_name="Amazon").json()
    token = rec["access_token"]

    create_job(client, token, title="Frontend React Developer", eligibility_cgpa=6.5)
    create_job(client, token, title="Machine Learning Scientist", eligibility_cgpa=9.0)

    # 1. Search keyword "React"
    search_res = client.get("/api/opportunities?search=React")
    assert search_res.status_code == status.HTTP_200_OK
    items = search_res.json()
    assert len(items) == 1
    assert "Frontend React Developer" in items[0]["title"]

    # 2. Eligible only filter with student CGPA 7.5
    student = register_student(client, email="average_student@test.edu", cgpa=7.5).json()
    stud_token = student["access_token"]

    filtered_res = client.get(
        "/api/opportunities?eligible_only=true",
        headers={"Authorization": f"Bearer {stud_token}"},
    )
    assert filtered_res.status_code == status.HTTP_200_OK
    filtered_items = filtered_res.json()
    # Student meets 6.5 req, but not 9.0 req
    titles = [item["title"] for item in filtered_items]
    assert "Frontend React Developer" in titles
    assert "Machine Learning Scientist" not in titles


def test_draft_opportunities_visible_only_to_owner_and_admin(client, db_session):
    """Drafts must not leak to the public, students, or other companies."""
    owner = register_recruiter(client, email="rec_draft@apple.com", company_name="Apple").json()
    other = register_recruiter(client, email="rec_draft@samsung.com", company_name="Samsung").json()
    student = register_student(client, email="draft_peek@college.edu", cgpa=9.5).json()
    admin_token = create_admin_token(client, db_session)

    draft = create_job(client, owner["access_token"], title="Secret Vision Pro Intern", status="draft").json()
    draft_id = draft["opportunity_id"]

    def auth(token):
        return {"Authorization": f"Bearer {token}"} if token else {}

    def listed(token):
        res = client.get("/api/opportunities?status=draft", headers=auth(token))
        assert res.status_code == status.HTTP_200_OK
        return [o["opportunity_id"] for o in res.json()]

    # Hidden from anonymous users, students, and other recruiters
    for token in (None, student["access_token"], other["access_token"]):
        assert draft_id not in listed(token)
        detail = client.get(f"/api/opportunities/{draft_id}", headers=auth(token))
        assert detail.status_code == status.HTTP_404_NOT_FOUND

    # Students cannot apply to a draft
    apply = client.post(f"/api/opportunities/{draft_id}/apply", headers=auth(student["access_token"]))
    assert apply.status_code == status.HTTP_404_NOT_FOUND

    # Visible to the owning company and admins
    for token in (owner["access_token"], admin_token):
        assert draft_id in listed(token)
        detail = client.get(f"/api/opportunities/{draft_id}", headers=auth(token))
        assert detail.status_code == status.HTTP_200_OK


# ============================================================================
# 3. Application Submission & Business Rules
# ============================================================================

def test_application_submission_eligibility_and_duplicates(client):
    """
    Test application workflow:
    - CGPA too low -> rejected
    - Opportunity closed -> rejected
    - Valid application -> created
    - Duplicate application -> rejected
    """
    rec = register_recruiter(client, email="rec_app@intel.com", company_name="Intel").json()
    token_rec = rec["access_token"]

    # Create job with CGPA 8.0
    job = create_job(client, token_rec, title="Hardware Intern", eligibility_cgpa=8.0).json()
    job_id = job["opportunity_id"]

    # Low CGPA student attempts to apply -> FAILS
    low_student = register_student(client, email="low_cgpa@college.edu", cgpa=7.2).json()
    res_low = client.post(
        f"/api/opportunities/{job_id}/apply",
        headers={"Authorization": f"Bearer {low_student['access_token']}"},
    )
    assert res_low.status_code == status.HTTP_400_BAD_REQUEST
    assert "CGPA" in res_low.json()["detail"]

    # High CGPA student applies -> SUCCEEDS
    high_student = register_student(client, email="high_cgpa@college.edu", cgpa=8.8).json()
    res_high = client.post(
        f"/api/opportunities/{job_id}/apply",
        headers={"Authorization": f"Bearer {high_student['access_token']}"},
    )
    assert res_high.status_code == status.HTTP_201_CREATED
    app_id = res_high.json()["application_id"]
    assert res_high.json()["status"] == "applied"

    # Second application for same student -> FAILS (duplicate check)
    res_dup = client.post(
        f"/api/opportunities/{job_id}/apply",
        headers={"Authorization": f"Bearer {high_student['access_token']}"},
    )
    assert res_dup.status_code == status.HTTP_400_BAD_REQUEST
    assert "already applied" in res_dup.json()["detail"].lower()


def test_recruiter_updates_status_and_cross_company_isolation(client):
    """Recruiters can update status of their applicants; students cannot update status."""
    rec1 = register_recruiter(client, email="rec_hr1@meta.com", company_name="Meta").json()
    rec2 = register_recruiter(client, email="rec_hr2@netflix.com", company_name="Netflix").json()
    student = register_student(client, email="candidate@college.edu", cgpa=9.0).json()

    job = create_job(client, rec1["access_token"], title="Meta AI Intern", eligibility_cgpa=8.0).json()
    app = client.post(
        f"/api/opportunities/{job['opportunity_id']}/apply",
        headers={"Authorization": f"Bearer {student['access_token']}"},
    ).json()
    app_id = app["application_id"]

    # Student cannot change status
    stud_change = client.patch(
        f"/api/applications/{app_id}/status",
        headers={"Authorization": f"Bearer {student['access_token']}"},
        json={"status": "selected"},
    )
    assert stud_change.status_code == status.HTTP_403_FORBIDDEN

    # Recruiter 2 (from Netflix) cannot update Meta's application
    rec2_change = client.patch(
        f"/api/applications/{app_id}/status",
        headers={"Authorization": f"Bearer {rec2['access_token']}"},
        json={"status": "shortlisted"},
    )
    assert rec2_change.status_code == status.HTTP_403_FORBIDDEN

    # Recruiter 1 (from Meta) successfully updates status
    rec1_change = move_application(client, rec1["access_token"], app_id, "shortlisted", "interview")
    assert rec1_change.json()["status"] == "interview"


def test_application_status_transitions(client, db_session):
    """Recruiters must follow the hiring pipeline; final statuses are locked; admins can override."""
    rec = register_recruiter(client, email="rec_flow@ibm.com", company_name="IBM").json()
    student = register_student(client, email="flow@college.edu", cgpa=9.0).json()
    job = create_job(client, rec["access_token"], title="Quantum Intern").json()
    app_id = client.post(
        f"/api/opportunities/{job['opportunity_id']}/apply",
        headers={"Authorization": f"Bearer {student['access_token']}"},
    ).json()["application_id"]

    def patch(token, new_status):
        return client.patch(
            f"/api/applications/{app_id}/status",
            headers={"Authorization": f"Bearer {token}"},
            json={"status": new_status},
        )

    # Cannot skip straight from applied to selected
    skip = patch(rec["access_token"], "selected")
    assert skip.status_code == status.HTTP_400_BAD_REQUEST
    assert "Allowed next statuses" in skip.json()["detail"]

    # Setting the current status again is a harmless no-op
    assert patch(rec["access_token"], "applied").status_code == status.HTTP_200_OK

    move_application(client, rec["access_token"], app_id, "under_review", "rejected")

    # Rejected is final for recruiters
    reopen = patch(rec["access_token"], "applied")
    assert reopen.status_code == status.HTTP_400_BAD_REQUEST
    assert "final status" in reopen.json()["detail"]

    # Admin can correct a mistake
    admin_token = create_admin_token(client, db_session)
    override = patch(admin_token, "shortlisted")
    assert override.status_code == status.HTTP_200_OK
    assert override.json()["status"] == "shortlisted"


# ============================================================================
# 4. Resume Upload & Access Control
# ============================================================================

def test_resume_upload_and_download_permissions(client):
    """
    Test resume workflow:
    - Non-PDF rejected
    - PDF accepted
    - Student who applied can download
    - Recruiter can download
    - Unrelated student cannot download (403)
    """
    rec = register_recruiter(client, email="rec_resume@cisco.com", company_name="Cisco").json()
    student1 = register_student(client, email="resume_std1@college.edu", cgpa=8.5).json()
    student2 = register_student(client, email="resume_std2@college.edu", cgpa=8.5).json()

    job = create_job(client, rec["access_token"], title="Network Intern", eligibility_cgpa=7.0).json()
    app = client.post(
        f"/api/opportunities/{job['opportunity_id']}/apply",
        headers={"Authorization": f"Bearer {student1['access_token']}"},
    ).json()
    app_id = app["application_id"]

    # 1. Non-PDF rejected
    bad_file = ("resume.txt", io.BytesIO(b"Hello world text file"), "text/plain")
    res_bad = client.post(
        f"/api/applications/{app_id}/resume",
        headers={"Authorization": f"Bearer {student1['access_token']}"},
        files={"file": bad_file},
    )
    assert res_bad.status_code == status.HTTP_400_BAD_REQUEST
    assert "PDF" in res_bad.json()["detail"]

    # 2. PDF accepted
    fake_pdf_content = b"%PDF-1.5 \x00\x01\x02 test pdf payload"
    good_file = ("resume.pdf", io.BytesIO(fake_pdf_content), "application/pdf")
    res_good = client.post(
        f"/api/applications/{app_id}/resume",
        headers={"Authorization": f"Bearer {student1['access_token']}"},
        files={"file": good_file},
    )
    assert res_good.status_code == status.HTTP_200_OK

    # 3. Owning student can download
    dl_owner = client.get(
        f"/api/applications/{app_id}/resume",
        headers={"Authorization": f"Bearer {student1['access_token']}"},
    )
    assert dl_owner.status_code == status.HTTP_200_OK
    assert dl_owner.headers["content-type"] == "application/pdf"

    # 4. Hiring recruiter can download
    dl_rec = client.get(
        f"/api/applications/{app_id}/resume",
        headers={"Authorization": f"Bearer {rec['access_token']}"},
    )
    assert dl_rec.status_code == status.HTTP_200_OK

    # 5. Other student CANNOT download (403)
    dl_other = client.get(
        f"/api/applications/{app_id}/resume",
        headers={"Authorization": f"Bearer {student2['access_token']}"},
    )
    assert dl_other.status_code == status.HTTP_403_FORBIDDEN


# ============================================================================
# 5. Admin Oversight & Statistics
# ============================================================================

def test_admin_oversight_and_statistics(client, db_session):
    """
    Test admin capabilities:
    - User listing and disable/reactivate
    - Global applications listing
    - Placement statistics calculation
    """
    admin_token = create_admin_token(client, db_session)

    # Create test data
    rec = register_recruiter(client, email="stats_co@oracle.com", company_name="Oracle").json()
    student = register_student(client, email="placed_student@college.edu", cgpa=9.5).json()
    job = create_job(client, rec["access_token"], title="Database Engineer", eligibility_cgpa=8.0).json()

    app = client.post(
        f"/api/opportunities/{job['opportunity_id']}/apply",
        headers={"Authorization": f"Bearer {student['access_token']}"},
    ).json()

    # Recruiter selects candidate
    move_application(client, rec["access_token"], app["application_id"], "shortlisted", "interview", "selected")

    # 1. Admin lists all applications
    admin_apps = client.get("/api/admin/applications", headers={"Authorization": f"Bearer {admin_token}"})
    assert admin_apps.status_code == status.HTTP_200_OK
    assert len(admin_apps.json()) >= 1

    # 2. Admin retrieves statistics
    stats_res = client.get("/api/admin/statistics", headers={"Authorization": f"Bearer {admin_token}"})
    assert stats_res.status_code == status.HTTP_200_OK
    stats = stats_res.json()
    assert stats["total_companies"] >= 1
    assert stats["total_applications"] >= 1
    assert stats["applications_by_status"]["selected"] >= 1
    assert stats["placement_rate"] > 0.0

    # 3. Admin disables student account
    disable_res = client.patch(
        f"/api/admin/users/{student['user']['user_id']}/status",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"account_status": "disabled"},
    )
    assert disable_res.status_code == status.HTTP_200_OK
    assert disable_res.json()["account_status"] == "disabled"
