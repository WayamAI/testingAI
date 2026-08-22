import { useState } from "react";
import { ProjectPicker } from "../components/common/ProjectPicker";
import { uploadDocument } from "../services/api/docDriven";
import type { DocDrivenResultOut } from "../services/api/docDriven";

export function DocDrivenPage() {
  const [projectId, setProjectId] = useState<string | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<DocDrivenResultOut | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [expanded, setExpanded] = useState<number | null>(null);

  const handleUpload = async () => {
    if (!projectId || !file) return;
    setUploading(true);
    setError(null);
    setResult(null);
    try {
      const res = await uploadDocument(projectId, file);
      setResult(res);
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? "Upload failed");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-semibold">Doc-Driven Tests</h1>
      <p className="text-sm text-neutral-500">
        Upload a PRD/spec/API-def (PDF, DOCX, TXT, or Markdown) — real text is extracted, AI identifies
        testable scenarios, and Playwright tests are generated from them.
      </p>

      <div className="flex flex-wrap items-center gap-3">
        <ProjectPicker value={projectId} onChange={setProjectId} />
        <input
          type="file"
          accept=".pdf,.docx,.txt,.md"
          aria-label="Document"
          onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          className="text-sm"
        />
        <button
          onClick={handleUpload}
          disabled={!projectId || !file || uploading}
          className="rounded-md bg-brand-600 px-4 py-2 text-sm text-white hover:bg-brand-700 disabled:opacity-50"
        >
          {uploading ? "Processing…" : "Upload & Generate"}
        </button>
      </div>

      {error && <p className="text-sm text-red-600">{error}</p>}
      {result && (
        <div className="space-y-3">
          <div className="rounded-md bg-neutral-50 dark:bg-neutral-900 p-3 text-sm">
            {result.message ? (
              <p>{result.message}</p>
            ) : (
              <p>
                Extracted {result.scenarios_extracted} scenario(s) ({result.scenario_source}), generated{" "}
                {result.tests_generated} test(s) ({result.rejected_invalid_syntax} rejected) — source: {result.source}
              </p>
            )}
          </div>
          {result.tests.map((t, i) => (
            <div key={t.id} className="rounded-md border border-neutral-200 dark:border-neutral-800 p-3">
              <button
                onClick={() => setExpanded(expanded === i ? null : i)}
                className="flex w-full items-center justify-between text-left"
              >
                <span className="font-medium">{t.title}</span>
                <span className="text-xs text-neutral-500">{t.category}</span>
              </button>
              {expanded === i && (
                <pre className="mt-2 overflow-x-auto rounded bg-neutral-100 dark:bg-neutral-950 p-2 text-xs">{t.code}</pre>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
