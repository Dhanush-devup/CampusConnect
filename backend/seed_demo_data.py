"""
CampusConnect — Comprehensive Demo Data Seeder.

Populates the development SQLite database with realistic, high-quality demo data:
- 1 Admin account (controlled setup)
- 5 Verified Companies and 5 Recruiter accounts
- 15 Diverse Student profiles (varied departments, CGPAs, and graduation years)
- 15 Job & Internship Opportunities (varied types, compensation, deadlines, statuses)
- 37 Applications with a realistic status distribution (applied, under_review, shortlisted, interview, selected, rejected)

Guarantees:
1. Strict idempotency: safe to run repeatedly without creating duplicates.
2. Canonical password hashing: uses `app.auth.hash_password` (bcrypt).
3. Database integrity: preserves all foreign keys, check constraints, and unique constraints.
4. Transactional safety: automatic rollback on failure.

Usage:
    python seed_demo_data.py
    (or from project root: python backend/seed_demo_data.py)
"""
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Ensure backend directory is in Python module search path
BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.auth import hash_password
from app.config import get_settings
from app.database import SessionLocal, init_db
from app.models import Application, Company, Opportunity, Student, User

settings = get_settings()

DEMO_STUDENT_PASSWORD = "Demo@123"
DEMO_RECRUITER_PASSWORD = "Demo@123"
DEMO_ADMIN_PASSWORD = "Admin@123"


def create_sample_resume_pdf(target_path: Path):
    """Generates a valid, minimal PDF file for realistic resume download tests."""
    target_path.parent.mkdir(parents=True, exist_ok=True)
    if not target_path.exists():
        pdf_content = (
            b"%PDF-1.4\n"
            b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
            b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
            b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >>\nendobj\n"
            b"4 0 obj\n<< /Length 57 >>\nstream\n"
            b"BT\n/F1 20 Tf\n72 710 Td\n(CampusConnect - Verified Candidate Resume) Tj\nET\n"
            b"endstream\nendobj\n"
            b"xref\n0 5\n"
            b"0000000000 65535 f \n"
            b"0000000009 00000 n \n"
            b"0000000058 00000 n \n"
            b"0000000115 00000 n \n"
            b"0000000210 00000 n \n"
            b"trailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n316\n%%EOF\n"
        )
        target_path.write_bytes(pdf_content)


def seed_demo_data():
    """Main idempotent seeder function."""
    init_db()
    session = SessionLocal()

    # Ensure uploads directory and sample resume exist
    upload_dir = Path(settings.UPLOAD_DIR).resolve()
    upload_dir.mkdir(parents=True, exist_ok=True)
    sample_resume_file = upload_dir / "demo_resume.pdf"
    create_sample_resume_pdf(sample_resume_file)
    rel_resume_path = f"uploads/resumes/{sample_resume_file.name}"

    now = datetime.now(timezone.utc)

    stats = {
        "admin": {"created": 0, "reused": 0},
        "companies": {"created": 0, "reused": 0},
        "recruiters": {"created": 0, "reused": 0},
        "students": {"created": 0, "reused": 0},
        "opportunities": {"created": 0, "reused": 0},
        "applications": {"created": 0, "reused": 0},
    }

    try:
        # ====================================================================
        # 1. Admin Account
        # ====================================================================
        admin_email = "admin@campusconnect.edu"
        admin_user = session.query(User).filter(User.email == admin_email).first()
        admin_hash = hash_password(DEMO_ADMIN_PASSWORD)

        if not admin_user:
            admin_user = User(
                name="Placement Administrator",
                email=admin_email,
                password_hash=admin_hash,
                role="admin",
                account_status="active",
                company_id=None,
            )
            session.add(admin_user)
            session.flush()
            stats["admin"]["created"] += 1
        else:
            admin_user.name = "Placement Administrator"
            admin_user.password_hash = admin_hash
            admin_user.account_status = "active"
            admin_user.role = "admin"
            stats["admin"]["reused"] += 1

        # ====================================================================
        # 2. Companies & Recruiters (5 pairs)
        # ====================================================================
        companies_data = [
            {
                "company_name": "TechCorp Solutions",
                "email": "careers@techcorp.com",
                "phone": "+91 80 4123 4567",
                "industry": "Software & Cloud Services",
                "location": "Bangalore, Karnataka",
                "website": "https://techcorp.example.com",
                "recruiter": {
                    "name": "Vikram Sharma",
                    "email": "recruiter@techcorp.com",
                },
            },
            {
                "company_name": "CloudScale Networks",
                "email": "talent@cloudscale.io",
                "phone": "+91 40 6789 0123",
                "industry": "Cloud Infrastructure & DevOps",
                "location": "Hyderabad, Telangana",
                "website": "https://cloudscale.example.io",
                "recruiter": {
                    "name": "Sarah Jenkins",
                    "email": "recruiter@cloudscale.io",
                },
            },
            {
                "company_name": "FinTech Dynamics",
                "email": "careers@fintechdynamics.com",
                "phone": "+91 22 2456 7890",
                "industry": "Financial Technology & Banking",
                "location": "Mumbai, Maharashtra",
                "website": "https://fintechdynamics.example.com",
                "recruiter": {
                    "name": "Arjun Kapoor",
                    "email": "recruiter@fintechdynamics.com",
                },
            },
            {
                "company_name": "HealthPulse Analytics",
                "email": "jobs@healthpulse.ai",
                "phone": "+91 20 5678 9012",
                "industry": "Healthcare AI & Bioinformatics",
                "location": "Pune, Maharashtra",
                "website": "https://healthpulse.example.ai",
                "recruiter": {
                    "name": "Dr. Elena Rostova",
                    "email": "recruiter@healthpulse.ai",
                },
            },
            {
                "company_name": "QuantumByte Robotics",
                "email": "hr@quantumbyte.tech",
                "phone": "+91 44 3456 7891",
                "industry": "Autonomous Systems & Robotics",
                "location": "Chennai, Tamil Nadu",
                "website": "https://quantumbyte.example.tech",
                "recruiter": {
                    "name": "Marcus Vance",
                    "email": "recruiter@quantumbyte.tech",
                },
            },
        ]

        recruiter_hash = hash_password(DEMO_RECRUITER_PASSWORD)
        seeded_companies = {}  # company_name -> Company object
        seeded_recruiters = {}  # email -> User object

        for c_data in companies_data:
            # Check or create Company
            company = session.query(Company).filter(Company.company_name == c_data["company_name"]).first()
            if not company:
                company = Company(
                    company_name=c_data["company_name"],
                    email=c_data["email"],
                    phone=c_data["phone"],
                    industry=c_data["industry"],
                    location=c_data["location"],
                    website=c_data["website"],
                )
                session.add(company)
                session.flush()
                stats["companies"]["created"] += 1
            else:
                company.email = c_data["email"]
                company.phone = c_data["phone"]
                company.industry = c_data["industry"]
                company.location = c_data["location"]
                company.website = c_data["website"]
                stats["companies"]["reused"] += 1

            seeded_companies[c_data["company_name"]] = company

            # Check or create Recruiter User
            r_data = c_data["recruiter"]
            recruiter = session.query(User).filter(User.email == r_data["email"]).first()
            if not recruiter:
                recruiter = User(
                    name=r_data["name"],
                    email=r_data["email"],
                    password_hash=recruiter_hash,
                    role="recruiter",
                    account_status="active",
                    company_id=company.company_id,
                )
                session.add(recruiter)
                session.flush()
                stats["recruiters"]["created"] += 1
            else:
                recruiter.name = r_data["name"]
                recruiter.password_hash = recruiter_hash
                recruiter.role = "recruiter"
                recruiter.account_status = "active"
                recruiter.company_id = company.company_id
                stats["recruiters"]["reused"] += 1

            seeded_recruiters[r_data["email"]] = recruiter

        # ====================================================================
        # 3. Students & Student Profiles (15 total)
        # ====================================================================
        students_data = [
            {"email": "student@demo.edu", "name": "Ananya Rao", "dept": "Computer Science", "cgpa": 8.75, "grad": 2026},
            {"email": "rohan.v@campus.edu", "name": "Rohan Verma", "dept": "Computer Science", "cgpa": 9.20, "grad": 2026},
            {"email": "priya.s@campus.edu", "name": "Priya Sharma", "dept": "Information Science", "cgpa": 8.45, "grad": 2026},
            {"email": "siddharth.n@campus.edu", "name": "Siddharth Nair", "dept": "Electronics & Communication", "cgpa": 7.80, "grad": 2025},
            {"email": "sneha.p@campus.edu", "name": "Sneha Patel", "dept": "AI & Data Science", "cgpa": 9.10, "grad": 2026},
            {"email": "karthik.i@campus.edu", "name": "Karthik Iyer", "dept": "Computer Science", "cgpa": 7.40, "grad": 2025},
            {"email": "neha.g@campus.edu", "name": "Neha Gupta", "dept": "Information Science", "cgpa": 8.90, "grad": 2026},
            {"email": "aditya.k@campus.edu", "name": "Aditya Kulkarni", "dept": "Electronics & Communication", "cgpa": 8.15, "grad": 2026},
            {"email": "pooja.h@campus.edu", "name": "Pooja Hegde", "dept": "AI & Data Science", "cgpa": 8.60, "grad": 2026},
            {"email": "vikram.j@campus.edu", "name": "Vikram Joshi", "dept": "Mechanical Engineering", "cgpa": 7.20, "grad": 2025},
            {"email": "divya.m@campus.edu", "name": "Divya Menon", "dept": "Electrical & Electronics", "cgpa": 7.95, "grad": 2026},
            {"email": "rahul.d@campus.edu", "name": "Rahul Deshmukh", "dept": "Computer Science", "cgpa": 6.90, "grad": 2025},
            {"email": "meera.n@campus.edu", "name": "Meera Nambiar", "dept": "Information Science", "cgpa": 8.30, "grad": 2027},
            {"email": "varun.r@campus.edu", "name": "Varun Reddy", "dept": "Computer Science", "cgpa": 8.85, "grad": 2026},
            {"email": "tanvi.s@campus.edu", "name": "Tanvi Shah", "dept": "AI & Data Science", "cgpa": 9.40, "grad": 2026},
        ]

        student_hash = hash_password(DEMO_STUDENT_PASSWORD)
        seeded_students = []  # list of Student objects ordered 0..14

        for s_info in students_data:
            s_user = session.query(User).filter(User.email == s_info["email"]).first()
            if not s_user:
                s_user = User(
                    name=s_info["name"],
                    email=s_info["email"],
                    password_hash=student_hash,
                    role="student",
                    account_status="active",
                    company_id=None,
                )
                session.add(s_user)
                session.flush()

                s_profile = Student(
                    user_id=s_user.user_id,
                    department=s_info["dept"],
                    cgpa=s_info["cgpa"],
                    graduation_year=s_info["grad"],
                )
                session.add(s_profile)
                session.flush()
                stats["students"]["created"] += 1
            else:
                s_user.name = s_info["name"]
                s_user.password_hash = student_hash
                s_user.account_status = "active"
                s_user.role = "student"

                s_profile = session.query(Student).filter(Student.user_id == s_user.user_id).first()
                if not s_profile:
                    s_profile = Student(
                        user_id=s_user.user_id,
                        department=s_info["dept"],
                        cgpa=s_info["cgpa"],
                        graduation_year=s_info["grad"],
                    )
                    session.add(s_profile)
                    session.flush()
                else:
                    s_profile.department = s_info["dept"]
                    s_profile.cgpa = s_info["cgpa"]
                    s_profile.graduation_year = s_info["grad"]
                stats["students"]["reused"] += 1

            seeded_students.append(s_profile)

        # ====================================================================
        # 4. Opportunities (15 total: 3 per company)
        # ====================================================================
        opportunities_data = [
            # TechCorp Solutions
            {
                "company_name": "TechCorp Solutions",
                "title": "Full-Stack Developer Intern",
                "type": "internship",
                "description": "Build high-throughput web applications and REST APIs using FastAPI, React, and PostgreSQL/SQLite in an agile sprint environment.",
                "location": "Bangalore (Hybrid)",
                "salary": 35000.0,
                "deadline": now + timedelta(days=25),
                "min_cgpa": 7.5,
                "status": "open",
            },
            {
                "company_name": "TechCorp Solutions",
                "title": "Associate Software Engineer",
                "type": "full_time",
                "description": "Full-time campus graduate hire for core backend infrastructure, distributed storage, and service integration.",
                "location": "Hyderabad",
                "salary": 75000.0,
                "deadline": now + timedelta(days=40),
                "min_cgpa": 8.0,
                "status": "open",
            },
            {
                "company_name": "TechCorp Solutions",
                "title": "Machine Learning Research Intern",
                "type": "internship",
                "description": "Collaborate with applied scientists on multimodal AI models, RAG architectures, and model quantization pipelines.",
                "location": "Bangalore",
                "salary": 45000.0,
                "deadline": now + timedelta(days=15),
                "min_cgpa": 8.5,
                "status": "open",
            },
            # CloudScale Networks
            {
                "company_name": "CloudScale Networks",
                "title": "Site Reliability Engineer",
                "type": "full_time",
                "description": "Deploy and monitor distributed cloud platforms, configure Kubernetes clusters, and automate observability dashboards.",
                "location": "Hyderabad",
                "salary": 85000.0,
                "deadline": now + timedelta(days=30),
                "min_cgpa": 7.5,
                "status": "open",
            },
            {
                "company_name": "CloudScale Networks",
                "title": "Cloud Operations Intern",
                "type": "internship",
                "description": "Hands-on internship working with Terraform, AWS/GCP resources, and zero-downtime CI/CD deployment pipelines.",
                "location": "Remote",
                "salary": 30000.0,
                "deadline": now + timedelta(days=20),
                "min_cgpa": 7.0,
                "status": "open",
            },
            {
                "company_name": "CloudScale Networks",
                "title": "Network Security Analyst",
                "type": "full_time",
                "description": "Conduct vulnerability assessments, monitor perimeter firewalls, and perform automated penetration testing.",
                "location": "Hyderabad",
                "salary": 80000.0,
                "deadline": now - timedelta(days=5),
                "min_cgpa": 7.5,
                "status": "closed",
            },
            # FinTech Dynamics
            {
                "company_name": "FinTech Dynamics",
                "title": "Backend Systems Engineer",
                "type": "full_time",
                "description": "Engineer low-latency settlement systems, payment gateways, and cryptographic ledger integrity protocols.",
                "location": "Mumbai",
                "salary": 90000.0,
                "deadline": now + timedelta(days=35),
                "min_cgpa": 8.0,
                "status": "open",
            },
            {
                "company_name": "FinTech Dynamics",
                "title": "Quantitative Risk Analyst Intern",
                "type": "internship",
                "description": "Develop algorithmic models for transaction risk profiling, credit scoring, and predictive financial analytics.",
                "location": "Mumbai",
                "salary": 50000.0,
                "deadline": now + timedelta(days=18),
                "min_cgpa": 8.5,
                "status": "open",
            },
            {
                "company_name": "FinTech Dynamics",
                "title": "Core Banking Solutions Intern",
                "type": "internship",
                "description": "Modernize enterprise transactional interfaces and audit log reporting tools. (Requisition currently in review).",
                "location": "Mumbai",
                "salary": 32000.0,
                "deadline": now + timedelta(days=60),
                "min_cgpa": 7.0,
                "status": "draft",
            },
            # HealthPulse Analytics
            {
                "company_name": "HealthPulse Analytics",
                "title": "Bio-Informatics Data Engineer",
                "type": "full_time",
                "description": "Build scalable data pipelines processing clinical telemetry, genomic sequencing streams, and electronic health records.",
                "location": "Pune",
                "salary": 82000.0,
                "deadline": now + timedelta(days=28),
                "min_cgpa": 7.8,
                "status": "open",
            },
            {
                "company_name": "HealthPulse Analytics",
                "title": "Clinical AI Research Intern",
                "type": "internship",
                "description": "Train and evaluate diagnostic computer vision models and patient symptom prediction models.",
                "location": "Pune (Hybrid)",
                "salary": 40000.0,
                "deadline": now + timedelta(days=22),
                "min_cgpa": 8.0,
                "status": "open",
            },
            {
                "company_name": "HealthPulse Analytics",
                "title": "Health Informatics Trainee",
                "type": "internship",
                "description": "Support data quality validation, clinical schema mapping, and compliance verification across healthcare datasets.",
                "location": "Remote",
                "salary": 28000.0,
                "deadline": now + timedelta(days=45),
                "min_cgpa": 6.5,
                "status": "open",
            },
            # QuantumByte Robotics
            {
                "company_name": "QuantumByte Robotics",
                "title": "Embedded Systems Firmware Engineer",
                "type": "full_time",
                "description": "Design deterministic real-time firmware in C/C++ on ARM microcontrollers for robotic motor controllers and sensor fusion.",
                "location": "Chennai",
                "salary": 78000.0,
                "deadline": now + timedelta(days=32),
                "min_cgpa": 7.5,
                "status": "open",
            },
            {
                "company_name": "QuantumByte Robotics",
                "title": "Computer Vision Intern",
                "type": "internship",
                "description": "Implement visual odometry, SLAM, and real-time obstacle avoidance algorithms for autonomous mobile robots.",
                "location": "Chennai",
                "salary": 42000.0,
                "deadline": now + timedelta(days=19),
                "min_cgpa": 8.2,
                "status": "open",
            },
            {
                "company_name": "QuantumByte Robotics",
                "title": "Robotics Controls Specialist",
                "type": "full_time",
                "description": "Develop feedback control laws, inverse kinematics algorithms, and state estimation filters. (Draft upcoming drive).",
                "location": "Chennai",
                "salary": 95000.0,
                "deadline": now + timedelta(days=50),
                "min_cgpa": 8.0,
                "status": "draft",
            },
        ]

        seeded_opportunities = []  # list of Opportunity objects ordered 0..14

        for opp_info in opportunities_data:
            comp = seeded_companies[opp_info["company_name"]]
            opp = (
                session.query(Opportunity)
                .filter(
                    Opportunity.company_id == comp.company_id,
                    Opportunity.title == opp_info["title"],
                )
                .first()
            )
            if not opp:
                opp = Opportunity(
                    company_id=comp.company_id,
                    title=opp_info["title"],
                    opportunity_type=opp_info["type"],
                    description=opp_info["description"],
                    location=opp_info["location"],
                    salary_stipend=opp_info["salary"],
                    deadline=opp_info["deadline"],
                    eligibility_cgpa=opp_info["min_cgpa"],
                    status=opp_info["status"],
                )
                session.add(opp)
                session.flush()
                stats["opportunities"]["created"] += 1
            else:
                opp.opportunity_type = opp_info["type"]
                opp.description = opp_info["description"]
                opp.location = opp_info["location"]
                opp.salary_stipend = opp_info["salary"]
                opp.deadline = opp_info["deadline"]
                opp.eligibility_cgpa = opp_info["min_cgpa"]
                opp.status = opp_info["status"]
                stats["opportunities"]["reused"] += 1

            seeded_opportunities.append(opp)

        # ====================================================================
        # 5. Applications (37 realistic applications across the students & opps)
        # ====================================================================
        # Format: (student_index 0..14, opp_index 0..14, status, days_ago, with_resume)
        applications_plan = [
            # Student 0: Ananya Rao (CGPA 8.75)
            (0, 0, "under_review", 14, True),
            (0, 6, "shortlisted", 10, True),
            (0, 10, "interview", 8, True),
            # Student 1: Rohan Verma (CGPA 9.20)
            (1, 1, "selected", 18, True),
            (1, 2, "interview", 12, True),
            (1, 7, "shortlisted", 7, True),
            # Student 2: Priya Sharma (CGPA 8.45)
            (2, 0, "shortlisted", 11, True),
            (2, 3, "under_review", 5, True),
            (2, 9, "applied", 2, False),
            # Student 3: Siddharth Nair (CGPA 7.80)
            (3, 4, "selected", 16, True),
            (3, 12, "interview", 9, True),
            # Student 4: Sneha Patel (CGPA 9.10)
            (4, 2, "selected", 20, True),
            (4, 7, "interview", 11, True),
            (4, 13, "shortlisted", 6, True),
            # Student 5: Karthik Iyer (CGPA 7.40)
            (5, 4, "under_review", 8, True),
            (5, 11, "rejected", 15, True),
            # Student 6: Neha Gupta (CGPA 8.90)
            (6, 6, "selected", 19, True),
            (6, 0, "shortlisted", 12, True),
            (6, 1, "interview", 9, True),
            # Student 7: Aditya Kulkarni (CGPA 8.15)
            (7, 3, "under_review", 6, True),
            (7, 12, "selected", 17, True),
            (7, 5, "rejected", 22, True),
            # Student 8: Pooja Hegde (CGPA 8.60)
            (8, 10, "shortlisted", 10, True),
            (8, 13, "under_review", 4, True),
            (8, 9, "applied", 1, False),
            # Student 9: Vikram Joshi (CGPA 7.20)
            (9, 11, "under_review", 7, True),
            (9, 4, "applied", 3, False),
            # Student 10: Divya Menon (CGPA 7.95)
            (10, 9, "shortlisted", 8, True),
            (10, 12, "under_review", 5, True),
            # Student 11: Rahul Deshmukh (CGPA 6.90)
            (11, 11, "under_review", 9, True),
            (11, 5, "rejected", 21, True),
            # Student 12: Meera Nambiar (CGPA 8.30)
            (12, 0, "applied", 3, True),
            (12, 3, "under_review", 4, True),
            # Student 13: Varun Reddy (CGPA 8.85)
            (13, 1, "shortlisted", 11, True),
            (13, 6, "under_review", 6, True),
            (13, 13, "applied", 2, False),
            # Student 14: Tanvi Shah (CGPA 9.40)
            (14, 2, "shortlisted", 13, True),
            (14, 7, "under_review", 7, True),
            (14, 10, "applied", 1, True),
        ]

        for s_idx, o_idx, app_status, days_ago, has_resume in applications_plan:
            stud = seeded_students[s_idx]
            opp = seeded_opportunities[o_idx]

            existing_app = (
                session.query(Application)
                .filter(
                    Application.student_id == stud.student_id,
                    Application.opportunity_id == opp.opportunity_id,
                )
                .first()
            )

            app_date = now - timedelta(days=days_ago)
            resume_val = rel_resume_path if has_resume else None

            if not existing_app:
                new_app = Application(
                    student_id=stud.student_id,
                    opportunity_id=opp.opportunity_id,
                    application_date=app_date,
                    status=app_status,
                    resume_path=resume_val,
                )
                session.add(new_app)
                stats["applications"]["created"] += 1
            else:
                existing_app.status = app_status
                existing_app.application_date = app_date
                if resume_val and not existing_app.resume_path:
                    existing_app.resume_path = resume_val
                stats["applications"]["reused"] += 1

        # Commit all entities atomically
        session.commit()

        # ====================================================================
        # Summary Report
        # ====================================================================
        print("\n" + "=" * 65)
        print(" CampusConnect Demo Data Seeding Completed Successfully")
        print("=" * 65)
        print(f" * Admin Account    : {stats['admin']['created']} created, {stats['admin']['reused']} verified/reused")
        print(f" * Companies        : {stats['companies']['created']} created, {stats['companies']['reused']} verified/reused")
        print(f" * Recruiters       : {stats['recruiters']['created']} created, {stats['recruiters']['reused']} verified/reused")
        print(f" * Student Profiles : {stats['students']['created']} created, {stats['students']['reused']} verified/reused")
        print(f" * Opportunities    : {stats['opportunities']['created']} created, {stats['opportunities']['reused']} verified/reused")
        print(f" * Applications     : {stats['applications']['created']} created, {stats['applications']['reused']} verified/reused")
        print("-" * 65)
        print(f" Total Users in Database         : {session.query(User).count()}")
        print(f" Total Companies in Database     : {session.query(Company).count()}")
        print(f" Total Opportunities in Database : {session.query(Opportunity).count()}")
        print(f" Total Applications in Database  : {session.query(Application).count()}")
        print("=" * 65 + "\n")

    except Exception as exc:
        session.rollback()
        print(f"\n[ERROR] Seeding encountered an error and rolled back: {exc}", file=sys.stderr)
        raise exc
    finally:
        session.close()


if __name__ == "__main__":
    seed_demo_data()
