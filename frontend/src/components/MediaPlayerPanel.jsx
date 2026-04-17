import { useEffect } from "react";
import { useRef } from "react";
import { mediaStreamUrl } from "../services/apiClient";

export default function MediaPlayerPanel({ selectedMedia, jumpToSeconds }) {
  const playerRef = useRef(null);

  useEffect(() => {
    if (playerRef.current) {
      playerRef.current.load();
    }
  }, [selectedMedia?.id]);

  useEffect(() => {
    if (playerRef.current && typeof jumpToSeconds === "number") {
      playerRef.current.currentTime = jumpToSeconds;
      playerRef.current.play().catch(() => {});
    }
  }, [jumpToSeconds]);

  if (!selectedMedia) {
    return (
      <section className="panel">
        <h2>Media Player</h2>
        <p>Select an audio/video file to preview playback.</p>
      </section>
    );
  }

  const source = mediaStreamUrl(selectedMedia.id);
  const isVideo = selectedMedia.media_kind === "video";

  return (
    <section className="panel">
      <h2>Media Player</h2>
      {isVideo ? (
        <video ref={playerRef} controls className="media-player">
          <source src={source} type={selectedMedia.mime_type} />
        </video>
      ) : (
        <audio ref={playerRef} controls className="media-player">
          <source src={source} type={selectedMedia.mime_type} />
        </audio>
      )}
    </section>
  );
}
