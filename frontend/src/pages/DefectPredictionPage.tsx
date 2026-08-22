import { useState } from "react";
import { ProjectPicker } from "../components/common/ProjectPicker";
import { runDefectPrediction, listRiskScores } from "../services/api/defectPrediction";
import type { DefectPredictionScanOut, FileRiskScoreOut } from "../services/api/defectPrediction";

const LABEL_COLOR: Record<string, string> = {
  critical: "text-red-600", high: "text-orange-600", medium: "text-amber-600", low: "text-neutral-500",
};

export function DefectPredictionPage() {
  const [projectId, setProjectId] = useState<string | null>(null);
  const [scanning, setScanning] = useState(false);
  const [scanResult, setScanResult] = useState<DefectPredictionScanOut | null>(null);
  const [scores, setScores] = useState<FileRiskScoreOut[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  const loadScores = async (id: string) => setScores(await listRiskScores(id));

  const handleScan = async () => {
    if (!projectId) return;
    setScanning(true);
    setError(null);
    try {
      const result = await runDefectPrediction(projectId);
      setScanResult(result);
      await loadScores(projectId);
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? "Defect prediction scan failed");
    } finally {
      setScanning(false);
    }
  };

  const handleProjectChange = (id: string) => {
    setProjectId(id);
    setScanResult(null);
    loadScores(id);
  };

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-semibold">Defect Prediction</h1>
      <p className="text-sm text-neutral-500">
        Mines real git history: risk = 30% change-frequency + 35% bug-fix-ratio + 20% churn + 15% author-count,
        each normalized across the repo's files.
      </p>

      <div className="flex items-center gap-3">
        <ProjectPicker value={projectId} onChange={handleProjectChange} />
        <button
          onClick={handleScan}
          disabled={!projectId || scanning}
          className="rounded-md bg-brand-600 px-4 py-2 text-sm text-white hover:bg-brand-700 disabled:opacity-50"
        >
          {scanning ? "Scanning…" : "Run Defect Prediction"}
        </button>
      </div>

      {error && <p className="text-sm text-red-600">{error}</p>}
      {scanResult && (
        <div className="rounded-md bg-neutral-50 dark:bg-neutral-900 p-3 text-sm space-y-1">
          <p className="font-medium">{scanResult.files_analyzed} file(s) analyzed — source: {scanResult.source}</p>
          <p className="whitespace-pre-line text-neutral-600 dark:text-neutral-300">{scanResult.narrative}</p>
        </div>
      )}

      {scores && scores.length > 0 && (
        <div className="overflow-x-auto rounded-lg border border-neutral-200 dark:border-neutral-800">
          <table className="w-full text-sm">
            <thead className="bg-neutral-50 dark:bg-neutral-900 text-left text-neutral-500">
              <tr>
                <th className="px-4 py-2 font-medium">File</th>
                <th className="px-4 py-2 font-medium">Risk</th>
                <th className="px-4 py-2 font-medium">Changes</th>
                <th className="px-4 py-2 font-medium">Bug-fix ratio</th>
                <th className="px-4 py-2 font-medium">Churn</th>
                <th className="px-4 py-2 font-medium">Authors</th>
              </tr>
            </thead>
            <tbody>
              {scores.map((s) => (
                <tr key={s.file_path} className="border-t border-neutral-200 dark:border-neutral-800">
                  <td className="px-4 py-2 font-mono text-xs">{s.file_path}</td>
                  <td className={`px-4 py-2 font-medium ${LABEL_COLOR[s.risk_label] ?? ""}`}>
                    {s.risk_label} ({s.risk_score.toFixed(2)})
                  </td>
                  <td className="px-4 py-2 text-neutral-500">{s.change_frequency}</td>
                  <td className="px-4 py-2 text-neutral-500">{(s.bug_fix_ratio * 100).toFixed(0)}%</td>
                  <td className="px-4 py-2 text-neutral-500">{s.churn}</td>
                  <td className="px-4 py-2 text-neutral-500">{s.author_count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
