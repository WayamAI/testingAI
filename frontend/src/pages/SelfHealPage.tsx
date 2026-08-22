import { useEffect, useState } from "react";
import { ProjectPicker } from "../components/common/ProjectPicker";
import { proposeHeal, approveHeal, rejectHeal, listHealAttempts } from "../services/api/selfHeal";
import type { AttemptOut } from "../services/api/selfHeal";

const STATUS_COLOR: Record<string, string> = {
  proposed: "text-amber-600", approved: "text-green-600", rejected: "text-red-600",
};

export function SelfHealPage() {
  const [projectId, setProjectId] = useState<string | null>(null);
  const [url, setUrl] = useState("");
  const [selector, setSelector] = useState("");
  const [failureContext, setFailureContext] = useState("");
  const [targetFile, setTargetFile] = useState("");
  const [targetLine, setTargetLine] = useState("");
  const [proposing, setProposing] = useState(false);
  const [proposeError, setProposeError] = useState<string | null>(null);
  const [attempts, setAttempts] = useState<AttemptOut[] | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);

  useEffect(() => {
    if (projectId) listHealAttempts(projectId).then(setAttempts);
  }, [projectId]);

  const refresh = async () => {
    if (projectId) setAttempts(await listHealAttempts(projectId));
  };

  const handlePropose = async () => {
    if (!projectId || !url || !selector) return;
    setProposing(true);
    setProposeError(null);
    try {
      await proposeHeal(projectId, url, selector, failureContext);
      await refresh();
    } catch (err: any) {
      setProposeError(err?.response?.data?.detail ?? "Propose failed");
    } finally {
      setProposing(false);
    }
  };

  const handleApprove = async (attemptId: string) => {
    if (!projectId) return;
    setActionError(null);
    try {
      await approveHeal(projectId, attemptId, targetFile || null, targetLine ? parseInt(targetLine, 10) : null);
      await refresh();
    } catch (err: any) {
      setActionError(err?.response?.data?.detail ?? "Approve failed");
    }
  };

  const handleReject = async (attemptId: string) => {
    if (!projectId) return;
    await rejectHeal(projectId, attemptId);
    await refresh();
  };

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-semibold">Self-Healing Tests</h1>
      <p className="text-sm text-neutral-500">
        Scoped to selector-not-found failures only. Live-scans the real DOM, the AI picks only an index into
        real candidates (it can't invent a selector), validates live, and requires your explicit approval
        before any write-back.
      </p>

      <ProjectPicker value={projectId} onChange={setProjectId} />

      <div className="space-y-2 rounded-lg border border-neutral-200 dark:border-neutral-800 p-4">
        <label className="block text-sm font-medium" htmlFor="sh-url">Live URL</label>
        <input
          id="sh-url" value={url} onChange={(e) => setUrl(e.target.value)} placeholder="http://localhost:5173/login"
          className="w-full rounded-md border border-neutral-300 dark:border-neutral-700 bg-transparent px-3 py-2 text-sm"
        />
        <label className="block text-sm font-medium" htmlFor="sh-selector">Broken selector</label>
        <input
          id="sh-selector" value={selector} onChange={(e) => setSelector(e.target.value)} placeholder="#submit-payment"
          className="w-full rounded-md border border-neutral-300 dark:border-neutral-700 bg-transparent px-3 py-2 text-sm font-mono"
        />
        <label className="block text-sm font-medium" htmlFor="sh-context">Failure context</label>
        <input
          id="sh-context" value={failureContext} onChange={(e) => setFailureContext(e.target.value)}
          className="w-full rounded-md border border-neutral-300 dark:border-neutral-700 bg-transparent px-3 py-2 text-sm"
        />
        <button
          onClick={handlePropose}
          disabled={!projectId || !url || !selector || proposing}
          className="rounded-md bg-brand-600 px-4 py-2 text-sm text-white hover:bg-brand-700 disabled:opacity-50"
        >
          {proposing ? "Scanning DOM…" : "Propose Fix"}
        </button>
        {proposeError && <p className="text-sm text-red-600">{proposeError}</p>}
      </div>

      {actionError && <p className="text-sm text-red-600">{actionError}</p>}

      {attempts && attempts.length > 0 && (
        <div className="space-y-3">
          <h2 className="font-medium">Attempts ({attempts.length})</h2>
          {attempts.map((a) => (
            <div key={a.id} className="rounded-md border border-neutral-200 dark:border-neutral-800 p-3 text-sm space-y-1">
              <div className="flex items-center justify-between">
                <span className="font-mono">{a.original_selector} → {a.proposed_selector}</span>
                <span className={`font-medium ${STATUS_COLOR[a.status] ?? ""}`}>{a.status}</span>
              </div>
              <p className="text-xs text-neutral-500">
                confidence {(a.ai_confidence * 100).toFixed(0)}% · live validation matched {a.live_validation_count} element(s) · source: {a.source}
              </p>
              <p className="text-xs text-neutral-500">{a.ai_reasoning}</p>
              {a.status === "proposed" && (
                <div className="flex flex-wrap items-center gap-2 pt-1">
                  <input
                    placeholder="target file (optional, e.g. checkout.spec.js)"
                    value={targetFile}
                    onChange={(e) => setTargetFile(e.target.value)}
                    className="rounded-md border border-neutral-300 dark:border-neutral-700 bg-transparent px-2 py-1 text-xs"
                  />
                  <input
                    placeholder="line"
                    value={targetLine}
                    onChange={(e) => setTargetLine(e.target.value)}
                    className="w-16 rounded-md border border-neutral-300 dark:border-neutral-700 bg-transparent px-2 py-1 text-xs"
                  />
                  <button onClick={() => handleApprove(a.id)} className="rounded-md bg-green-600 px-3 py-1 text-xs text-white hover:bg-green-700">
                    Approve
                  </button>
                  <button onClick={() => handleReject(a.id)} className="rounded-md border border-neutral-300 dark:border-neutral-700 px-3 py-1 text-xs">
                    Reject
                  </button>
                </div>
              )}
              {a.applied && <p className="text-xs text-green-600">Applied to {a.target_file}:{a.target_line}</p>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
