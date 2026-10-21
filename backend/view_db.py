"""
Utility script to display all records across the 5 CampusConnect database tables.
"""
from app.database import SessionLocal
from app.models import User, Student, Company, Opportunity, Application

def display_database():
    session = SessionLocal()
    try:
        print("\n" + "=" * 80)
        print(" CAMPUSCONNECT DATABASE OVERVIEW")
        print("=" * 80)

        # 1. USERS
        users = session.query(User).all()
        print(f"\n[1] USERS TABLE ({len(users)} records):")
        print(f"{'ID':<4} | {'Name':<22} | {'Email':<26} | {'Role':<10} | {'Status':<8}")
        print("-" * 80)
        for u in users:
            print(f"{u.user_id:<4} | {u.name:<22} | {u.email:<26} | {u.role:<10} | {u.account_status:<8}")

        # 2. STUDENTS
        students = session.query(Student).all()
        print(f"\n[2] STUDENTS TABLE ({len(students)} records):")
        print(f"{'ID':<4} | {'User ID':<8} | {'Department':<20} | {'CGPA':<6} | {'Grad Year':<10}")
        print("-" * 80)
        for s in students:
            print(f"{s.student_id:<4} | {s.user_id:<8} | {s.department:<20} | {s.cgpa:<6.2f} | {s.graduation_year:<10}")

        # 3. COMPANIES
        companies = session.query(Company).all()
        print(f"\n[3] COMPANIES TABLE ({len(companies)} records):")
        print(f"{'ID':<4} | {'Company Name':<22} | {'Email':<26} | {'Location':<20}")
        print("-" * 80)
        for c in companies:
            print(f"{c.company_id:<4} | {c.company_name:<22} | {c.email:<26} | {c.location or 'N/A':<20}")

        # 4. OPPORTUNITIES
        opps = session.query(Opportunity).all()
        print(f"\n[4] OPPORTUNITIES TABLE ({len(opps)} records):")
        print(f"{'ID':<4} | {'Title':<30} | {'Type':<12} | {'Min CGPA':<9} | {'Status':<8}")
        print("-" * 80)
        for o in opps:
            print(f"{o.opportunity_id:<4} | {o.title[:28]:<30} | {o.opportunity_type:<12} | {o.eligibility_cgpa:<9.2f} | {o.status:<8}")

        # 5. APPLICATIONS
        apps = session.query(Application).all()
        print(f"\n[5] APPLICATIONS TABLE ({len(apps)} records):")
        print(f"{'ID':<4} | {'Student ID':<10} | {'Opportunity ID':<15} | {'Status':<14} | {'Resume':<20}")
        print("-" * 80)
        for a in apps:
            resume_display = (a.resume_path or 'No Resume')[-20:]
            print(f"{a.application_id:<4} | {a.student_id:<10} | {a.opportunity_id:<15} | {a.status:<14} | {resume_display:<20}")

        print("\n" + "=" * 80 + "\n")
    finally:
        session.close()

if __name__ == "__main__":
    display_database()
