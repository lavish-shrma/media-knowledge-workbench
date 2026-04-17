import { useMemo } from "react";

export default function SummaryPanel({
  files,
  selectedFileId,
  onSelectFile,
  onGenerateSummary,
  summary,
  summaryError,
  isProcessing,
}) {
  const selectedFile = useMemo(
    () => files.find((item) => item.id === selectedFileId) || null,
    [files, selectedFileId]
  );

  return (
    <section className="panel">
      <h2>Summary</h2>
      {files.length === 0 ? <p>Upload a file to generate a summary.</p> : null}
      {files.length > 0 ? (
        <div className="summary-controls">
          <label htmlFor="file-select">Choose file</label>
          <select
            id="file-select"
            value={selectedFileId || ""}
            onChange={(event) => onSelectFile(Number(event.target.value))}
          >
            <option value="" disabled>
              Select a file
            </option>
            {files.map((item) => (
              <option key={item.id} value={item.id}>
                {item.original_name}
              </option>
            ))}
          </select>
          <button
            type="button"
            onClick={onGenerateSummary}
            disabled={!selectedFileId || isProcessing}
          >
            {isProcessing ? "Processing..." : "Generate or Refresh Summary"}
          </button>
        </div>
      ) : null}
      {selectedFile ? <p>Selected: {selectedFile.original_name}</p> : null}
      {summaryError ? <p className="status-message error">{summaryError}</p> : null}
      {summary ? (
        <article className="summary-card">
          <p>{summary.summary_text}</p>
          <small>Model: {summary.model_name}</small>
        </article>
      ) : null}
    </section>
  );
}
