import { useMemo } from "react";
import { useState } from "react";

export default function TimestampPanel({
  files,
  selectedMediaId,
  onSelectMedia,
  onExtract,
  matches,
  error,
  isLoading,
  onJumpTo,
}) {
  const [topic, setTopic] = useState("");
  const mediaFiles = useMemo(
    () => files.filter((item) => item.media_kind === "audio" || item.media_kind === "video"),
    [files]
  );

  async function handleSubmit(event) {
    event.preventDefault();
    if (!selectedMediaId || !topic.trim()) {
      return;
    }

    await onExtract(selectedMediaId, topic.trim());
  }

  return (
    <section className="panel">
      <h2>Timestamps and Playback</h2>
      {mediaFiles.length === 0 ? <p>Upload audio/video and process it to extract timestamps.</p> : null}
      {mediaFiles.length > 0 ? (
        <form className="timestamp-form" onSubmit={handleSubmit}>
          <label htmlFor="media-select">Media file</label>
          <select
            id="media-select"
            value={selectedMediaId || ""}
            onChange={(event) => onSelectMedia(Number(event.target.value))}
          >
            <option value="" disabled>
              Select media file
            </option>
            {mediaFiles.map((item) => (
              <option key={item.id} value={item.id}>
                {item.original_name}
              </option>
            ))}
          </select>

          <label htmlFor="topic-input">Topic</label>
          <input
            id="topic-input"
            type="text"
            placeholder="e.g. machine learning"
            value={topic}
            onChange={(event) => setTopic(event.target.value)}
          />

          <button type="submit" disabled={isLoading || !selectedMediaId}>
            {isLoading ? "Extracting..." : "Extract Timestamps"}
          </button>
        </form>
      ) : null}

      {error ? <p className="status-message error">{error}</p> : null}

      {matches.length > 0 ? (
        <ul className="timestamp-list">
          {matches.map((item, index) => (
            <li key={`${item.start_seconds}-${item.end_seconds}-${index}`}>
              <p>{item.text}</p>
              <small>
                {item.start_seconds.toFixed(2)}s - {item.end_seconds.toFixed(2)}s | score {item.score.toFixed(2)}
              </small>
              <button type="button" onClick={() => onJumpTo(item.start_seconds)}>
                Play From Here
              </button>
            </li>
          ))}
        </ul>
      ) : null}
    </section>
  );
}
