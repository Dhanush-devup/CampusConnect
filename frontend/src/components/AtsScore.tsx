import React, { useCallback, useEffect, useRef, useState } from "react";
import { AlertTriangle, Bot, CheckCircle2, Gauge, Loader2, RefreshCw, Sparkles, XCircle } from "lucide-react";
import { applicationsApi } from "../api/endpoints";
import { Application, ResumeScore } from "../api/types";
import { Modal } from "./Modal";

const POLL_INTERVAL_MS = 3000;

const FLAG_MESSAGES: Record<string, string> = {
  low_text:
    "This PDF has no selectable text. It's an image, scan, or photo of a resume, so most ATS systems can't read it.",
  long_document: "The document is unusually long; only the first part was scored.",
  possible_manipulation:
    "This resume contains text that tries to instruct the scoring system. AI scoring was skipped.",
};

const scoreColor = (score: number) =>
  score >= 75
    ? "bg-emerald-50 text-emerald-700 border-emerald-200"
    : score >= 50
      ? "bg-amber-50 text-amber-700 border-amber-200"
      : "bg-rose-50 text-rose-700 border-rose-200";

const barColor = (score: number) =>
  score >= 75 ? "bg-emerald-500" : score >= 50 ? "bg-amber-500" : "bg-rose-500";

interface AtsScoreBadgeProps {
  app: Application;
  onClick: () => void;
}

export const AtsScoreBadge: React.FC<AtsScoreBadgeProps> = ({ app, onClick }) => {
  if (!app.resume_path) {
    return <span className="text-slate-400 text-[11px]">No resume</span>;
  }

  const base = "inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-semibold transition-colors hover:opacity-80";

  if (app.ats_status === "pending") {
    return (
      <button onClick={onClick} className={`${base} bg-slate-50 text-slate-600 border-slate-200`}>
        <Loader2 className="h-3.5 w-3.5 animate-spin" />
        Scoring...
      </button>
    );
  }
  if (app.ats_status === "completed" && app.ats_score != null) {
    return (
      <button onClick={onClick} className={`${base} ${scoreColor(app.ats_score)}`} title="View ATS report">
        <Gauge className="h-3.5 w-3.5" />
        ATS {app.ats_score}/100
      </button>
    );
  }
  return (
    <button onClick={onClick} className={`${base} bg-slate-50 text-slate-600 border-slate-200`}>
      <Gauge className="h-3.5 w-3.5" />
      {app.ats_status === "failed" ? "Scoring failed" : "Not scored"}
    </button>
  );
};

// Render with key={app?.application_id} so each application starts with fresh state.
interface AtsReportModalProps {
  app: Application | null;
  viewer: "student" | "recruiter";
  onClose: () => void;
  /** Called when a score is requested or finishes, so the page can refresh its list. */
  onScoreChange?: () => void;
}

export const AtsReportModal: React.FC<AtsReportModalProps> = ({ app, viewer, onClose, onScoreChange }) => {
  const [report, setReport] = useState<ResumeScore | null>(null);
  const [notScored, setNotScored] = useState(false);
  const [isLoading, setIsLoading] = useState(app !== null);
  const [error, setError] = useState<string | null>(null);
  const applicationId = app?.application_id;

  const load = useCallback(async () => {
    if (!applicationId) return;
    try {
      const data = await applicationsApi.getAtsScore(applicationId);
      setReport(data);
      setNotScored(false);
      setError(null);
    } catch (err: any) {
      if (err.status === 404) {
        setNotScored(true);
      } else {
        setError(err.message || "Could not load the ATS report.");
      }
    } finally {
      setIsLoading(false);
    }
  }, [applicationId]);

  useEffect(() => {
    load();
  }, [load]);

  // Poll while scoring runs in the background
  const isPending = report?.status === "pending";
  useEffect(() => {
    if (!isPending) return;
    const id = window.setInterval(load, POLL_INTERVAL_MS);
    return () => window.clearInterval(id);
  }, [isPending, load]);

  const wasPending = useRef(false);
  useEffect(() => {
    if (wasPending.current && !isPending) onScoreChange?.();
    wasPending.current = isPending;
  }, [isPending, onScoreChange]);

  const requestScore = async () => {
    if (!applicationId) return;
    setError(null);
    try {
      setReport(await applicationsApi.requestAtsScore(applicationId));
      setNotScored(false);
      onScoreChange?.();
    } catch (err: any) {
      setError(err.message || "Could not start scoring.");
    }
  };

  const subScores: [string, number | null | undefined, string][] = report
    ? [
        ["Skills match", report.skills_score, "40%"],
        ["Experience & projects", report.experience_score, "30%"],
        ["Education & CGPA", report.education_score, "15%"],
        ["Formatting & ATS readability", report.formatting_score, "15%"],
      ]
    : [];

  return (
    <Modal
      isOpen={app !== null}
      onClose={onClose}
      title="ATS Resume Score"
      subtitle={app ? `${viewer === "student" ? app.company_name : app.student_name} · ${app.opportunity_title}` : undefined}
      maxWidth="2xl"
    >
      {isLoading ? (
        <div className="py-12 text-center text-xs text-slate-500">
          <Loader2 className="mx-auto h-6 w-6 animate-spin text-indigo-600 mb-2" />
          Loading report...
        </div>
      ) : error ? (
        <div className="rounded-xl bg-rose-50 border border-rose-200 p-3 text-xs text-rose-700">{error}</div>
      ) : notScored ? (
        <div className="py-8 text-center">
          <Gauge className="mx-auto h-8 w-8 text-slate-300 mb-2" />
          <p className="text-sm font-semibold text-slate-800">This resume hasn't been scored yet</p>
          <p className="text-xs text-slate-500 mt-1 mb-4">Resumes uploaded before ATS scoring existed need a first score.</p>
          <button
            onClick={requestScore}
            className="inline-flex items-center gap-1.5 rounded-xl bg-indigo-600 px-4 py-2 text-xs font-semibold text-white hover:bg-indigo-500"
          >
            <Sparkles className="h-3.5 w-3.5" />
            Score now
          </button>
        </div>
      ) : report?.status === "pending" ? (
        <div className="py-12 text-center">
          <Loader2 className="mx-auto h-8 w-8 animate-spin text-indigo-600 mb-3" />
          <p className="text-sm font-semibold text-slate-800">Scoring resume against the job...</p>
          <p className="text-xs text-slate-500 mt-1">AI scoring can take up to 30 seconds. You can close this window; the score will appear on its own.</p>
        </div>
      ) : report?.status === "failed" ? (
        <div className="py-8 text-center">
          <XCircle className="mx-auto h-8 w-8 text-rose-400 mb-2" />
          <p className="text-sm font-semibold text-slate-800">Scoring failed</p>
          <p className="text-xs text-slate-500 mt-1 mb-4">{report.error_message}</p>
          <button
            onClick={requestScore}
            className="inline-flex items-center gap-1.5 rounded-xl border border-slate-300 px-4 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-50"
          >
            <RefreshCw className="h-3.5 w-3.5" />
            Try again
          </button>
        </div>
      ) : report ? (
        <div className="space-y-5 text-xs">
          {/* Headline */}
          <div className="flex items-center gap-4">
            <div
              className={`flex h-20 w-20 shrink-0 flex-col items-center justify-center rounded-2xl border ${scoreColor(report.overall_score ?? 0)}`}
            >
              <span className="text-2xl font-bold">{report.overall_score}</span>
              <span className="text-[10px] font-semibold opacity-70">/ 100</span>
            </div>
            <div className="min-w-0">
              <p className="text-sm text-slate-700">{report.summary}</p>
              <p className="mt-1.5 inline-flex items-center gap-1 text-[11px] text-slate-500">
                <Bot className="h-3.5 w-3.5" />
                {report.scored_by === "gemini" ? "AI-assisted score (Google Gemini)" : "Rule-based score (keyword & structure checks)"}
              </p>
            </div>
          </div>

          {viewer === "recruiter" && (
            <div className="rounded-xl bg-slate-50 border border-slate-200 p-3 text-[11px] text-slate-600">
              Advisory only. Automated scores can miss context or be wrong, so review the resume before making decisions.
            </div>
          )}

          {report.error_message && (
            <div className="rounded-xl bg-amber-50 border border-amber-200 p-3 text-[11px] text-amber-800">
              {report.error_message}
            </div>
          )}
          {report.flags.map((flag) => (
            <div key={flag} className="flex items-start gap-2 rounded-xl bg-amber-50 border border-amber-200 p-3 text-[11px] text-amber-800">
              <AlertTriangle className="h-4 w-4 shrink-0 text-amber-600" />
              <span>{FLAG_MESSAGES[flag] ?? flag}</span>
            </div>
          ))}

          {/* Sub-scores */}
          <div className="space-y-2.5">
            {subScores.map(([label, value, weight]) => (
              <div key={label}>
                <div className="flex justify-between mb-1">
                  <span className="font-semibold text-slate-700">
                    {label} <span className="font-normal text-slate-400">({weight})</span>
                  </span>
                  <span className="font-bold text-slate-800">{value ?? 0}</span>
                </div>
                <div className="h-2 rounded-full bg-slate-100">
                  <div className={`h-2 rounded-full ${barColor(value ?? 0)}`} style={{ width: `${value ?? 0}%` }} />
                </div>
              </div>
            ))}
          </div>

          {/* Skills */}
          {(report.matched_skills.length > 0 || report.missing_skills.length > 0) && (
            <div className="grid sm:grid-cols-2 gap-4">
              <div>
                <p className="font-bold uppercase tracking-wider text-[10px] text-slate-500 mb-2">Matched skills</p>
                <div className="flex flex-wrap gap-1.5">
                  {report.matched_skills.map((skill) => (
                    <span key={skill} className="rounded-full bg-emerald-50 border border-emerald-200 px-2 py-0.5 text-emerald-700">
                      {skill}
                    </span>
                  ))}
                  {report.matched_skills.length === 0 && <span className="text-slate-400">None found</span>}
                </div>
              </div>
              <div>
                <p className="font-bold uppercase tracking-wider text-[10px] text-slate-500 mb-2">Missing skills</p>
                <div className="flex flex-wrap gap-1.5">
                  {report.missing_skills.map((skill) => (
                    <span key={skill} className="rounded-full bg-rose-50 border border-rose-200 px-2 py-0.5 text-rose-700">
                      {skill}
                    </span>
                  ))}
                  {report.missing_skills.length === 0 && <span className="text-slate-400">None</span>}
                </div>
              </div>
            </div>
          )}

          {/* Feedback */}
          <div className="grid sm:grid-cols-2 gap-4">
            {report.strengths.length > 0 && (
              <div>
                <p className="font-bold uppercase tracking-wider text-[10px] text-slate-500 mb-2">Strengths</p>
                <ul className="space-y-1.5">
                  {report.strengths.map((item) => (
                    <li key={item} className="flex gap-1.5 text-slate-700">
                      <CheckCircle2 className="h-3.5 w-3.5 shrink-0 text-emerald-500 mt-0.5" />
                      {item}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            {report.improvements.length > 0 && (
              <div>
                <p className="font-bold uppercase tracking-wider text-[10px] text-slate-500 mb-2">
                  {viewer === "student" ? "How to improve" : "Gaps"}
                </p>
                <ul className="space-y-1.5">
                  {report.improvements.map((item) => (
                    <li key={item} className="flex gap-1.5 text-slate-700">
                      <Sparkles className="h-3.5 w-3.5 shrink-0 text-indigo-500 mt-0.5" />
                      {item}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          <div className="flex items-center justify-between pt-3 border-t border-slate-100 text-[11px] text-slate-400">
            <span>Scored {new Date(report.updated_at).toLocaleString()}</span>
            <button onClick={requestScore} className="inline-flex items-center gap-1 font-semibold text-indigo-600 hover:underline">
              <RefreshCw className="h-3 w-3" />
              Re-score
            </button>
          </div>
        </div>
      ) : null}
    </Modal>
  );
};
