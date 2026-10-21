# CampusConnect — Demo Evaluation Credentials

> **CRITICAL SECURITY NOTICE**  
> These credentials are provided exclusively for local testing, evaluation, and demonstration of the **CampusConnect** Internship and Placement Management System. **Never use or reuse these credentials, keys, or passwords in production or public environments.**  
> Plaintext passwords are **never** stored in the database; all passwords are cryptographically hashed using industry-standard **bcrypt** salts.

---

## 🚀 Quick Evaluation Accounts

Use these pre-configured accounts to evaluate each role immediately (also available via the 1-click **Quick Demo Login** buttons on the Login page):

| Role | Account Name | Email Address | Password | Organization / Notes |
| :--- | :--- | :--- | :--- | :--- |
| **Admin** | Placement Administrator | `admin@campusconnect.edu` | `Admin@123` | Institutional Oversight & Analytics |
| **Recruiter** | Vikram Sharma | `recruiter@techcorp.com` | `Demo@123` | **TechCorp Solutions** (3 Active Job Postings) |
| **Student** | Ananya Rao | `student@demo.edu` | `Demo@123` | **Computer Science** (CGPA: 8.75, 3 Applications) |

---

## 🏢 Recruiter & Company Accounts (5 Partners)

All recruiter demo accounts use the standard password: **`Demo@123`**

| Recruiter Name | Recruiter Email | Company Name | Industry | Location | Postings |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Vikram Sharma** | `recruiter@techcorp.com` | **TechCorp Solutions** | Software & Cloud Services | Bangalore | 3 Jobs |
| **Sarah Jenkins** | `recruiter@cloudscale.io` | **CloudScale Networks** | Cloud Infrastructure & DevOps | Hyderabad | 3 Jobs |
| **Arjun Kapoor** | `recruiter@fintechdynamics.com` | **FinTech Dynamics** | Financial Technology & Banking | Mumbai | 3 Jobs |
| **Dr. Elena Rostova** | `recruiter@healthpulse.ai` | **HealthPulse Analytics** | Healthcare AI & Bioinformatics | Pune | 3 Jobs |
| **Marcus Vance** | `recruiter@quantumbyte.tech` | **QuantumByte Robotics** | Autonomous Systems & Robotics | Chennai | 3 Jobs |

---

## 🎓 Student Accounts (15 Candidates)

All student demo accounts use the standard password: **`Demo@123`**

| # | Student Name | Email Address | Department | CGPA | Grad Year | Active Applications |
| :-: | :--- | :--- | :--- | :-: | :-: | :--- |
| 1 | **Ananya Rao** | `student@demo.edu` | Computer Science | 8.75 | 2026 | 3 (Review, Shortlisted, Interview) |
| 2 | **Rohan Verma** | `rohan.v@campus.edu` | Computer Science | 9.20 | 2026 | 3 (Selected, Interview, Shortlisted) |
| 3 | **Priya Sharma** | `priya.s@campus.edu` | Information Science | 8.45 | 2026 | 3 (Shortlisted, In Review, Applied) |
| 4 | **Siddharth Nair** | `siddharth.n@campus.edu` | Electronics & Comm. | 7.80 | 2025 | 2 (Selected, Interview) |
| 5 | **Sneha Patel** | `sneha.p@campus.edu` | AI & Data Science | 9.10 | 2026 | 3 (Selected, Interview, Shortlisted) |
| 6 | **Karthik Iyer** | `karthik.i@campus.edu` | Computer Science | 7.40 | 2025 | 2 (In Review, Rejected) |
| 7 | **Neha Gupta** | `neha.g@campus.edu` | Information Science | 8.90 | 2026 | 3 (Selected, Shortlisted, Interview) |
| 8 | **Aditya Kulkarni** | `aditya.k@campus.edu` | Electronics & Comm. | 8.15 | 2026 | 3 (In Review, Selected, Rejected) |
| 9 | **Pooja Hegde** | `pooja.h@campus.edu` | AI & Data Science | 8.60 | 2026 | 3 (Shortlisted, In Review, Applied) |
| 10 | **Vikram Joshi** | `vikram.j@campus.edu` | Mechanical Eng. | 7.20 | 2025 | 2 (In Review, Applied) |
| 11 | **Divya Menon** | `divya.m@campus.edu` | Electrical & Electronics | 7.95 | 2026 | 2 (Shortlisted, In Review) |
| 12 | **Rahul Deshmukh** | `rahul.d@campus.edu` | Computer Science | 6.90 | 2025 | 2 (In Review, Rejected) |
| 13 | **Meera Nambiar** | `meera.n@campus.edu` | Information Science | 8.30 | 2027 | 2 (Applied, In Review) |
| 14 | **Varun Reddy** | `varun.r@campus.edu` | Computer Science | 8.85 | 2026 | 3 (Shortlisted, In Review, Applied) |
| 15 | **Tanvi Shah** | `tanvi.s@campus.edu` | AI & Data Science | 9.40 | 2026 | 3 (Shortlisted, In Review, Applied) |

---

## 🛠️ How to Re-run or Reset the Seeder

The seeding script is completely idempotent and safe to run multiple times. It updates existing records without duplicating entities:

```powershell
# From the backend directory
cd C:\Users\dhanu\OneDrive\Desktop\CampusConnect\backend
.\venv\Scripts\python seed_demo_data.py

# Or from the project root directory
cd C:\Users\dhanu\OneDrive\Desktop\CampusConnect
.\backend\venv\Scripts\python backend\seed_demo_data.py
```

### Quick Database Inspection
To view all 5 tables in your terminal at any time, run:
```powershell
cd C:\Users\dhanu\OneDrive\Desktop\CampusConnect\backend
.\venv\Scripts\python view_db.py
```
