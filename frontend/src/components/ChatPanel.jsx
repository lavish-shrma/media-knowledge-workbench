import { useState } from "react";

export default function ChatPanel({
  files,
  selectedFileId,
  messages,
  sources,
  onAsk,
  onStreamAsk,
  onJumpFromSource,
  isAsking,
  isStreaming,
  streamingAnswer,
  error,
}) {
  const [question, setQuestion] = useState("");
  const [selectedMediaKind, setSelectedMediaKind] = useState("all");
  const [minScore, setMinScore] = useState(0);

  async function handleSubmit(event) {
    event.preventDefault();
    if (!question.trim()) {
      return;
    }

    await onAsk(
      question.trim(),
      selectedFileId ? [selectedFileId] : [],
      selectedMediaKind === "all" ? [] : [selectedMediaKind],
      Number(minScore)
    );
    setQuestion("");
  }

  return (
    <section className="panel">
      <h2>Chatbot</h2>
      {files.length === 0 ? <p>Upload and process files to start asking questions.</p> : null}
      <form className="chat-form" onSubmit={handleSubmit}>
        <textarea
          placeholder="Ask a question about uploaded content"
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          rows={3}
        />
        <div className="chat-filters">
          <label>
            Media type
            <select value={selectedMediaKind} onChange={(event) => setSelectedMediaKind(event.target.value)}>
              <option value="all">All</option>
              <option value="document">Document</option>
              <option value="audio">Audio</option>
              <option value="video">Video</option>
            </select>
          </label>
          <label>
            Minimum score
            <input
              type="number"
              min="0"
              max="2"
              step="0.05"
              value={minScore}
              onChange={(event) => setMinScore(event.target.value)}
            />
          </label>
        </div>
        <button type="submit" disabled={isAsking || files.length === 0}>
          {isAsking ? "Asking..." : "Ask"}
        </button>
        <button type="button" disabled={isStreaming || files.length === 0} onClick={() => onStreamAsk(question.trim(), selectedFileId ? [selectedFileId] : [])}>
          {isStreaming ? "Streaming..." : "Stream Ask"}
        </button>
      </form>
      {error ? <p className="status-message error">{error}</p> : null}

      <div className="chat-history">
        {messages.length === 0 ? <p>No conversation yet.</p> : null}
        {messages.map((message, index) => (
          <article key={`${message.created_at}-${index}`} className={`chat-message ${message.role}`}>
            <strong>{message.role === "assistant" ? "Assistant" : "You"}</strong>
            <p>{message.content}</p>
          </article>
        ))}
        {streamingAnswer ? (
          <article className="chat-message assistant">
            <strong>Assistant</strong>
            <p>{streamingAnswer}</p>
          </article>
        ) : null}
      </div>

      {sources.length > 0 ? (
        <div className="sources-list">
          <h3>Sources</h3>
          <ul>
            {sources.map((source, index) => (
              <li key={`${source.chunk_id}-${index}`}>
                <p>{source.source_text}</p>
                <small>
                  file #{source.file_id} | score {source.score.toFixed(3)}
                </small>
                {typeof source.start_seconds === "number" ? (
                  <button
                    type="button"
                    onClick={() => onJumpFromSource(source.file_id, source.start_seconds)}
                  >
                    Play Source Segment
                  </button>
                ) : null}
              </li>
            ))}
          </ul>
        </div>
      ) : null}
    </section>
  );
}
