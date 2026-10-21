import httpx
import sys

BASE_URL = "http://127.0.0.1:8000"

def test_live_system():
    print("Testing live FastAPI system on", BASE_URL)
    
    # 1. Health check
    res = httpx.get(f"{BASE_URL}/api/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    print("[PASS] 1. API Health Check OK:", res.json())

    # 2. Student Login
    login_data = {"email": "student@demo.edu", "password": "Demo@123"}
    res = httpx.post(f"{BASE_URL}/api/auth/login", json=login_data)
    assert res.status_code == 200, f"Student login failed: {res.text}"
    student_token = res.json()["access_token"]
    student_headers = {"Authorization": f"Bearer {student_token}"}
    print("[PASS] 2. Student Login OK. User:", res.json()["user"]["email"])

    # 3. Student Me & Profile
    res = httpx.get(f"{BASE_URL}/api/auth/me", headers=student_headers)
    assert res.status_code == 200
    user_me = res.json()
    assert user_me["role"] == "student"
    print("[PASS] 3. /api/auth/me OK for Student:", user_me["name"], user_me["student_profile"]["department"], f"CGPA: {user_me['student_profile']['cgpa']}")

    # 4. Student Dashboard Stats
    res = httpx.get(f"{BASE_URL}/api/students/dashboard-stats", headers=student_headers)
    assert res.status_code == 200
    stats = res.json()
    print("[PASS] 4. Student Dashboard Stats OK:", stats)

    # 5. Browse Opportunities
    res = httpx.get(f"{BASE_URL}/api/opportunities?status=open", headers=student_headers)
    assert res.status_code == 200
    opps = res.json()
    assert len(opps) > 0
    print(f"[PASS] 5. Browse Opportunities OK: {len(opps)} open opportunities found")

    # 6. Recruiter Login
    res = httpx.post(f"{BASE_URL}/api/auth/login", json={"email": "recruiter@techcorp.com", "password": "Demo@123"})
    assert res.status_code == 200
    recruiter_token = res.json()["access_token"]
    recruiter_headers = {"Authorization": f"Bearer {recruiter_token}"}
    print("[PASS] 6. Recruiter Login OK. Company:", res.json()["user"]["company"]["company_name"])

    # 7. Recruiter Dashboard Stats
    res = httpx.get(f"{BASE_URL}/api/recruiters/dashboard-stats", headers=recruiter_headers)
    assert res.status_code == 200
    print("[PASS] 7. Recruiter Dashboard Stats OK:", res.json())

    # 8. Recruiter Review Applications
    res = httpx.get(f"{BASE_URL}/api/recruiters/applications", headers=recruiter_headers)
    assert res.status_code == 200
    apps = res.json()
    print(f"[PASS] 8. Recruiter Company Applications OK: {len(apps)} applications retrieved")

    # 9. Admin Login
    res = httpx.post(f"{BASE_URL}/api/auth/login", json={"email": "admin@campusconnect.edu", "password": "Admin@123"})
    assert res.status_code == 200
    admin_token = res.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    print("[PASS] 9. Admin Login OK. Role:", res.json()["user"]["role"])

    # 10. Admin Stats & Oversight
    res = httpx.get(f"{BASE_URL}/api/admin/stats", headers=admin_headers)
    assert res.status_code == 200
    admin_stats = res.json()
    print("[PASS] 10. Admin Placement Stats OK:")
    print("      Total Students:", admin_stats["students_count"])
    print("      Total Companies:", admin_stats["total_companies"])
    print("      Total Applications:", admin_stats["total_applications"])
    print("      Placement Rate:", f"{admin_stats['placement_rate']}%")

    # 11. Admin User Directory
    res = httpx.get(f"{BASE_URL}/api/admin/users", headers=admin_headers)
    assert res.status_code == 200
    users = res.json()
    print(f"[PASS] 11. Admin User Directory OK: {len(users)} users found")

    print("\nALL 11 END-TO-END SYSTEM INTEGRATION CHECKS PASSED PERFECTLY!")

if __name__ == "__main__":
    test_live_system()
