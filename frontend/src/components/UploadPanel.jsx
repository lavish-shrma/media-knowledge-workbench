import { useState } from "react";
import { uploadAsset } from "../services/apiClient";

const ACCEPTED_TYPES = ".pdf,.mp3,.wav,.m4a,.aac,.ogg,.mp4,.mov,.avi,.mkv,.webm";

export default function UploadPanel({ onUploaded }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [message, setMessage] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();
    if (!selectedFile) {
      setMessage("Select a PDF, audio, or video file first.");
      return;
    }

    setIsUploading(true);
    setMessage("");

    try {
      await uploadAsset(selectedFile);
      setMessage("Upload successful. Status set to queued.");
      setSelectedFile(null);
      onUploaded();
    } catch (error) {
      setMessage(error.message);
    } finally {
      setIsUploading(false);
    }
  }

  return (
    <section className="panel">
      <h2>Upload Files</h2>
      <form className="upload-form" onSubmit={handleSubmit}>
        <input
          type="file"
          accept={ACCEPTED_TYPES}
          onChange={(event) => setSelectedFile(event.target.files?.[0] || null)}
        />
        <button type="submit" disabled={isUploading}>
          {isUploading ? "Uploading..." : "Upload"}
        </button>
      </form>
      {message ? <p className="status-message">{message}</p> : null}
    </section>
  );
}
