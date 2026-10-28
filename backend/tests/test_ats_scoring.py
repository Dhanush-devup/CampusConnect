"""
ATS resume scoring tests: rule-based scoring, Gemini integration (mocked),
fallback on failure, manipulation detection, and access control.
"""
import io
import json

import httpx
import pytest
from fastapi import status

from app import ats_scoring
from make_demo_resumes import MANIPULATED_RESUME, STRONG_RESUME, WEAK_RESUME, build_pdf
from tests.test_api import create_job, register_recruiter, register_student

FULL_STACK_JOB = (
    "Build web applications and REST APIs using FastAPI, React, and PostgreSQL/SQLite "
    "in an agile sprint environment."
)


def auth(token):
    return {"Authorization": f"Bearer {token}"}


def setup_application(client, resume_lines=None, email_suffix="1"):
    """Creates a recruiter, a full-stack job, and a student application (optionally with a resume)."""
    rec = register_recruiter(client, email=f"ats_rec{email_suffix}@acme.com", company_name=f"Acme{email_suffix}").json()
    job = create_job(client, rec["access_token"], title="Full-Stack Developer Intern", eligibility_cgpa=7.5)
    job_id = job.json()["opportunity_id"]
    client.put(
        f"/api/opportunities/{job_id}",
        headers=auth(rec["access_token"]),
        json={"description": FULL_STACK_JOB},
    )
    student = register_student(client, email=f"ats_student{email_suffix}@college.edu", cgpa=8.75).json()
    files = None
    if resume_lines is not None:
        files = {"resume": ("resume.pdf", io.BytesIO(build_pdf(resume_lines)), "application/pdf")}
    app = client.post(f"/api/opportunities/{job_id}/apply", headers=auth(student["access_token"]), files=files)
    assert app.status_code == status.HTTP_201_CREATED, app.text
    return rec, student, app.json()


def get_score(client, token, app_id):
    res = client.get(f"/api/applications/{app_id}/ats-score", headers=auth(token))
    assert res.status_code == status.HTTP_200_OK, res.text
    return res.json()


def test_resume_upload_is_scored_with_rules_without_api_key(client):
    rec, student, app = setup_application(client, STRONG_RESUME)

    report = get_score(client, student["access_token"], app["application_id"])
    assert report["status"] == "completed"
    assert report["scored_by"] == "rules"
    assert report["overall_score"] >= 80
    assert {"fastapi", "react", "postgresql"} <= set(report["matched_skills"])

    # Score summary appears in both students' and recruiters' application lists
    mine = client.get("/api/students/applications", headers=auth(student["access_token"])).json()
    theirs = client.get("/api/recruiters/applications", headers=auth(rec["access_token"])).json()
    for listing in (mine, theirs):
        assert listing[0]["ats_score"] == report["overall_score"]
        assert listing[0]["ats_status"] == "completed"


def test_strong_resume_outscores_weak_resume(client):
    _, strong_student, strong_app = setup_application(client, STRONG_RESUME, "strong")
    _, weak_student, weak_app = setup_application(client, WEAK_RESUME, "weak")

    strong = get_score(client, strong_student["access_token"], strong_app["application_id"])
    weak = get_score(client, weak_student["access_token"], weak_app["application_id"])
    assert strong["overall_score"] - weak["overall_score"] >= 40
    assert weak["improvements"]


def test_score_visible_only_to_student_hiring_recruiter_and_admin(client):
    rec, student, app = setup_application(client, STRONG_RESUME, "owner")
    other_rec = register_recruiter(client, email="ats_other@globex.com", company_name="Globex").json()
    other_student = register_student(client, email="ats_nosy@college.edu").json()

    assert get_score(client, rec["access_token"], app["application_id"])["status"] == "completed"
    for outsider in (other_rec, other_student):
        res = client.get(f"/api/applications/{app['application_id']}/ats-score", headers=auth(outsider["access_token"]))
        assert res.status_code == status.HTTP_403_FORBIDDEN


def test_application_without_resume_has_no_score(client):
    _, student, app = setup_application(client, resume_lines=None, email_suffix="noresume")
    assert app["ats_status"] is None

    res = client.get(f"/api/applications/{app['application_id']}/ats-score", headers=auth(student["access_token"]))
    assert res.status_code == status.HTTP_404_NOT_FOUND

    rescore = client.post(f"/api/applications/{app['application_id']}/ats-score", headers=auth(student["access_token"]))
    assert rescore.status_code == status.HTTP_400_BAD_REQUEST


def test_rescore_endpoint_scores_existing_resume(client):
    rec, _, app = setup_application(client, STRONG_RESUME, "rescore")
    res = client.post(f"/api/applications/{app['application_id']}/ats-score", headers=auth(rec["access_token"]))
    assert res.status_code == status.HTTP_202_ACCEPTED
    assert res.json()["status"] == "pending"
    # Background task has run by the time the test client returns
    assert get_score(client, rec["access_token"], app["application_id"])["status"] == "completed"


def fake_gemini_response(payload: dict) -> httpx.Response:
    request = httpx.Request("POST", "https://generativelanguage.googleapis.com")
    body = {"candidates": [{"content": {"parts": [{"text": json.dumps(payload)}]}}]}
    return httpx.Response(200, json=body, request=request)


@pytest.fixture
def gemini_enabled(monkeypatch):
    monkeypatch.setattr(ats_scoring.settings, "GEMINI_API_KEY", "test-key")
    calls = []

    def install(handler):
        def fake_post(url, **kwargs):
            calls.append({"url": url, **kwargs})
            return handler()
        monkeypatch.setattr(ats_scoring.httpx, "post", fake_post)
        return calls

    return install


def test_gemini_scores_and_overall_is_computed_from_subscores(client, gemini_enabled):
    calls = gemini_enabled(lambda: fake_gemini_response({
        "skills_score": 90, "experience_score": 80, "education_score": 70, "formatting_score": 60,
        "matched_skills": ["FastAPI", "React"], "missing_skills": ["Kubernetes"],
        "strengths": ["Relevant internship"], "improvements": ["Add a summary line"],
        "summary": "Strong fit.",
        "overall_score": 5,  # ignored: the overall is always weighted in code
    }))
    _, student, app = setup_application(client, STRONG_RESUME, "gemini")

    report = get_score(client, student["access_token"], app["application_id"])
    assert report["scored_by"] == "gemini"
    assert report["overall_score"] == round((90 * 40 + 80 * 30 + 70 * 15 + 60 * 15) / 100)
    assert report["missing_skills"] == ["Kubernetes"]
    assert report["summary"] == "Strong fit."

    # Key goes in a header (not the URL) and the PDF itself is sent, so image resumes can be read
    assert calls[0]["headers"] == {"x-goog-api-key": "test-key"}
    assert "test-key" not in calls[0]["url"]
    pdf_part = calls[0]["json"]["contents"][0]["parts"][0]
    assert pdf_part["inlineData"]["mimeType"] == "application/pdf"


def test_gemini_failure_falls_back_to_rules(client, gemini_enabled):
    def boom():
        request = httpx.Request("POST", "https://generativelanguage.googleapis.com")
        return httpx.Response(429, json={"error": "quota"}, request=request)

    gemini_enabled(boom)
    _, student, app = setup_application(client, STRONG_RESUME, "fallback")

    report = get_score(client, student["access_token"], app["application_id"])
    assert report["status"] == "completed"
    assert report["scored_by"] == "rules"
    assert report["overall_score"] >= 80
    assert "AI scoring unavailable" in report["error_message"]


def test_manipulation_attempt_is_flagged_and_never_sent_to_gemini(client, gemini_enabled):
    calls = gemini_enabled(lambda: fake_gemini_response({}))
    _, student, app = setup_application(client, MANIPULATED_RESUME, "inject")

    report = get_score(client, student["access_token"], app["application_id"])
    assert "possible_manipulation" in report["flags"]
    assert report["scored_by"] == "rules"
    assert report["overall_score"] < 60
    assert calls == []


def test_unreadable_pdf_scores_zero_without_ai(client):
    """A title-only or image-only PDF is a blank page to an ATS: no credit from profile data."""
    _, student, app = setup_application(client, ["Resume"], "scan")
    report = get_score(client, student["access_token"], app["application_id"])
    assert "low_text" in report["flags"]
    assert report["overall_score"] == 0
    assert report["education_score"] == 0
    assert "No readable text" in report["summary"]


def test_unreadable_pdf_is_read_by_gemini_with_formatting_penalty(client, gemini_enabled):
    calls = gemini_enabled(lambda: fake_gemini_response({
        "skills_score": 80, "experience_score": 70, "education_score": 90, "formatting_score": 85,
        "matched_skills": ["React"], "missing_skills": [], "strengths": ["Good projects"],
        "improvements": [], "summary": "Read from the image.",
    }))
    _, student, app = setup_application(client, ["Resume"], "scanai")

    report = get_score(client, student["access_token"], app["application_id"])
    assert len(calls) == 1
    assert report["scored_by"] == "gemini"
    assert report["skills_score"] == 80
    assert report["formatting_score"] == 20  # capped: real ATS can't read image-only PDFs
    assert "low_text" in report["flags"]
    assert "selectable text" in report["improvements"][0]


def test_education_needs_evidence_on_the_resume(client):
    """A high profile CGPA alone must not produce a good education score."""
    _, student, app = setup_application(client, WEAK_RESUME, "edu")
    report = get_score(client, student["access_token"], app["application_id"])
    assert report["education_score"] <= 30


def test_busy_gemini_model_falls_back_to_next_model(client, gemini_enabled):
    replies = iter([
        httpx.Response(503, json={"error": "high demand"}, request=httpx.Request("POST", "https://g")),
        fake_gemini_response({
            "skills_score": 70, "experience_score": 70, "education_score": 70, "formatting_score": 70,
            "matched_skills": [], "missing_skills": [], "strengths": [], "improvements": [],
            "summary": "From the fallback model.",
        }),
    ])
    calls = gemini_enabled(lambda: next(replies))
    _, student, app = setup_application(client, STRONG_RESUME, "busy")

    report = get_score(client, student["access_token"], app["application_id"])
    assert report["scored_by"] == "gemini"
    assert report["summary"] == "From the fallback model."
    assert [call["url"].split("/models/")[1].split(":")[0] for call in calls] == [
        ats_scoring.settings.GEMINI_MODEL,
        "gemini-3.5-flash-lite",
    ]
