# CampusConnect: Setup & Run Guide

This guide takes you from nothing to a fully working demo on `http://localhost:5173`: clone the repo, install everything, create and fill the database with demo data, and run the app. It's written for **Windows**. Mac and Linux commands are at the end.

Total time: about 15 minutes, mostly waiting for installs.

---

## Step 0: Install the required software (one time only)

You need three programs. If you already have them, skip to Step 1.

| Software | Version | Download |
|---|---|---|
| **Git** | any recent version | https://git-scm.com/download/win |
| **Python** | **3.10 or newer** (tested on 3.14) | https://www.python.org/downloads/ |
| **Node.js** | **20.19+ or 22.12+** (the LTS version is fine; tested on 24) | https://nodejs.org/ |

> **Important when installing Python:** on the first installer screen, tick **"Add python.exe to PATH"** before clicking Install.

### Check the installs
Open **PowerShell**: press the Windows key, type `powershell`, press Enter. Then run:

```powershell
git --version
python --version
node --version
npm --version
```

Each should print a version number. If one says *"not recognized"*, reinstall that program (or restart your computer so the new PATH takes effect).

---

## Step 1: Get the code

In PowerShell, go to the folder where you want the project (the Desktop here) and clone it:

```powershell
cd $HOME\Desktop
git clone https://github.com/Dhanush-devup/CampusConnect.git
cd CampusConnect
```

You should now see the folders `backend` and `frontend` (check with `dir`).

---

## Step 2: Set up the backend

All commands in this step are run **inside the `backend` folder**.

```powershell
cd backend
```

### 2.1 Create a Python virtual environment
A virtual environment keeps this project's packages separate from the rest of your computer. **It must be named `venv`**, because the run scripts look for that name.

```powershell
python -m venv venv
```

This creates a `venv` folder inside `backend`.

### 2.2 Install the backend packages

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

This takes 1–3 minutes. It should finish without red `ERROR` lines.

### 2.3 Create the settings file

```powershell
Copy-Item .env.example .env
```

The defaults work for a local demo as-is. To turn on **AI resume scoring**, see Step 5 (optional; without it, resumes get the built-in rule-based score).

### 2.4 Create the database and fill it with demo data

```powershell
.\venv\Scripts\python.exe seed_demo_data.py
```

This single command:
- creates the database file `backend\campus_connect.db` with all 6 tables (migrations run automatically),
- creates the admin account, 5 companies with recruiters, 15 students, 15 jobs and internships, and about 39 applications,
- creates a sample resume file in `backend\uploads\resumes\`.

At the end it prints a summary like:

```
 Total Users in Database         : 21
 Total Companies in Database     : 5
 Total Opportunities in Database : 15
 Total Applications in Database  : 39
```

> It's safe to run this again; it won't create duplicates. Job deadlines are set relative to the day you run it, so **re-run it the day before a demo** to keep every job open.

### 2.5 (Optional) Check that everything works

```powershell
.\venv\Scripts\python.exe -m pytest -q tests
```

Expected result: `51 passed`. This takes about 40 seconds.

### 2.6 Go back to the project folder

```powershell
cd ..
```

---

## Step 3: Set up the frontend

```powershell
cd frontend
npm install
cd ..
```

`npm install` takes 1–2 minutes and creates a `node_modules` folder. Warnings are normal; red `ERR!` lines are not.

---

## Step 4: Run the app

### Option A: one click (recommended)
In File Explorer, open the `CampusConnect` folder and **double-click `run_all.bat`**.

- Two black windows open: **"CampusConnect Backend"** and **"CampusConnect Frontend"**. **Keep them open**; closing them stops the app.
- After a few seconds your browser opens **http://localhost:5173**.

> Double-click the file in **File Explorer**. Clicking it inside VS Code only opens it as text. From a terminal you can also run `.\run_all.bat`.

### Option B: two terminals (shows any error messages)
**Terminal 1, backend:**
```powershell
cd backend
.\venv\Scripts\uvicorn.exe app.main:app --host 127.0.0.1 --port 8000
```
Wait for `Application startup complete.`

**Terminal 2, frontend:**
```powershell
cd frontend
npm run dev
```
Then open **http://localhost:5173** in your browser.

### Check it's working
| Check | URL | Expected |
|---|---|---|
| Backend health | http://127.0.0.1:8000/api/health | `"status": "healthy"`, `"database": "connected"` |
| API documentation | http://127.0.0.1:8000/docs | Interactive list of all endpoints |
| The app | http://localhost:5173 | CampusConnect landing page |

### Stop the app
Close the two black windows (Option A), or press `Ctrl + C` in each terminal (Option B).

---

## Step 5 (optional): Turn on AI resume scoring with Gemini (free)

Without this, the ATS score uses the built-in rule-based scorer. With it, Google Gemini reads each resume and writes detailed feedback.

1. Go to **https://aistudio.google.com/apikey**, sign in with a Google account, and click **Create API key**. Copy the key.
2. Open `backend\.env` in Notepad or VS Code and add this line at the bottom:
   ```
   GEMINI_API_KEY=paste-your-key-here
   ```
3. Save the file and **restart the backend** (close and reopen the black windows, or `Ctrl + C` and start it again).

The ATS report will then say **"AI-assisted score (Google Gemini)"**. Each AI score takes 15–30 seconds.

> **Privacy:** Google may use free-tier inputs to improve its products. **Use only fake resumes** (made-up names, emails, and phone numbers).
>
> **Never commit `.env` to Git.** It's already listed in `.gitignore`.

---

## Step 6: Demo accounts

| Role | Email | Password |
|---|---|---|
| **Admin** | admin@campusconnect.edu | Admin@123 |
| **Recruiter** | recruiter@techcorp.com | Demo@123 |
| **Student** | student@demo.edu | Demo@123 |

The login page also has **quick demo login** buttons. More accounts (all 5 recruiters, all 15 students) are listed in `DEMO_CREDENTIALS.md`.

---

## Step 7: Demo script (ATS resume scoring)

Sample resumes are included in `backend\demo_resumes\`:

| File | Expected score |
|---|---|
| `strong_fullstack_resume.pdf` | High (about 85–100) |
| `weak_resume.pdf` | Low (about 2–25) |
| `manipulated_resume.pdf` | Low, with a warning that the resume tried to trick the scorer |

### Score a resume on an existing application
1. Log in as the **student** (student@demo.edu / Demo@123).
2. Go to **My Applications**. The demo student has already applied to **Full-Stack Developer Intern**, **Backend Systems Engineer**, and **Clinical AI Research Intern**.
3. On **Full-Stack Developer Intern**, click **Replace Resume** and upload `strong_fullstack_resume.pdf`.
4. A **"Scoring..."** badge appears and turns into the score (a few seconds without AI, up to 30 seconds with Gemini). **Click the score** to open the full report.
5. Upload `weak_resume.pdf` to the same application to show the contrast.

### Apply to a new job with a resume
1. As the student, go to **Explore Opportunities**.
2. Pick an open job the student hasn't applied to yet (e.g. **Cloud Operations Intern** or **Bio-Informatics Data Engineer**), click **Apply Now**, and attach a PDF resume.
3. The score appears in **My Applications**.

### Recruiter view
1. Log in as the **recruiter** (recruiter@techcorp.com / Demo@123).
2. Open **Review Applications**. The **ATS Score** column shows each candidate's score; click one to open the report (marked "advisory only").
3. Older seeded applications show **"Not scored"**. Click it, then **Score now**.

### Making your own test resumes
- Make them in Word or Google Docs and export with **File → Download → PDF**.
- Check: if you can **select and copy text** in the PDF, the scorer can read it. Photos, screenshots, and scans score 0 without AI.
- Use the headings **Education, Experience, Projects, Skills**, put an email and phone number at the top, and write the CGPA on the resume.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `python` or `node` "is not recognized" | Reinstall it (tick "Add to PATH" for Python), then **open a new PowerShell window**. |
| `.\venv\Scripts\...` "cannot be loaded because running scripts is disabled" | You don't need to activate the venv; the commands above call `python.exe` directly. If you still hit this, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once. |
| Backend window opens and closes immediately | Use Option B to see the error. Usually the `venv` folder is missing or misnamed: redo Steps 2.1–2.2 inside `backend`. |
| `Address already in use` / port 8000 or 5173 busy | The app is already running in another window. Close it, or restart your computer. |
| Login fails or pages show "network error" | The backend isn't running. Check http://127.0.0.1:8000/api/health. |
| No jobs to apply for / "deadline has passed" | Re-run `.\venv\Scripts\python.exe seed_demo_data.py` in `backend` to refresh deadlines. |
| ATS score says "AI scoring unavailable" | Gemini is busy or the key is wrong. The rule-based score is still shown. Check the key in `backend\.env` and restart the backend. |
| ATS score is 0 with "no readable text" | The PDF is an image or scan. Export a text PDF from Word or Google Docs. |
| Want a completely fresh database | Stop the backend, delete `backend\campus_connect.db`, and run `seed_demo_data.py` again. |

---

## Mac / Linux commands

Same steps; only the commands differ:

```bash
git clone https://github.com/Dhanush-devup/CampusConnect.git
cd CampusConnect/backend
python3 -m venv venv
./venv/bin/python -m pip install -r requirements.txt
cp .env.example .env
./venv/bin/python seed_demo_data.py

# Terminal 1 (inside backend)
./venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000

# Terminal 2
cd CampusConnect/frontend
npm install
npm run dev
```

The `.bat` files are Windows-only; use the two-terminal method instead.
