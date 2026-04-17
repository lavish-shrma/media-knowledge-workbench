import { useCallback, useEffect, useState } from "react";
import AppLayout from "../components/AppLayout";
import AuthPanel from "../components/AuthPanel";
import ChatPanel from "../components/ChatPanel";
import FileStatusList from "../components/FileStatusList";
import MediaPlayerPanel from "../components/MediaPlayerPanel";
import SummaryPanel from "../components/SummaryPanel";
import TimestampPanel from "../components/TimestampPanel";
import UploadPanel from "../components/UploadPanel";
import { askChat, extractTimestamps, getConversation, getSummary, listFiles, loginUser, processFile, registerUser, refreshToken, streamChat } from "../services/apiClient";

export default function WorkspacePage() {
  void [
    AppLayout,
    AuthPanel,
    ChatPanel,
    FileStatusList,
    MediaPlayerPanel,
    SummaryPanel,
    TimestampPanel,
    UploadPanel,
  ];

  const [files, setFiles] = useState([]);
  const [error, setError] = useState("");
  const [selectedFileId, setSelectedFileId] = useState(null);
  const [summary, setSummary] = useState(null);
  const [summaryError, setSummaryError] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const [conversationId, setConversationId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [chatSources, setChatSources] = useState([]);
  const [chatError, setChatError] = useState("");
  const [isAsking, setIsAsking] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamingAnswer, setStreamingAnswer] = useState("");
  const [selectedMediaId, setSelectedMediaId] = useState(null);
  const [timestampMatches, setTimestampMatches] = useState([]);
  const [timestampError, setTimestampError] = useState("");
  const [isExtractingTimestamps, setIsExtractingTimestamps] = useState(false);
  const [playbackSeconds, setPlaybackSeconds] = useState(null);
  const [authEmail, setAuthEmail] = useState(window.localStorage.getItem("auth_email") || "");
  const [authStatus, setAuthStatus] = useState("");

  const loadFiles = useCallback(async () => {
    try {
      const payload = await listFiles();
      setFiles(payload);
      if (!selectedFileId && payload.length > 0) {
        setSelectedFileId(payload[0].id);
      }
      if (!selectedMediaId) {
        const firstMedia = payload.find((item) => item.media_kind === "audio" || item.media_kind === "video");
        if (firstMedia) {
          setSelectedMediaId(firstMedia.id);
        }
      }
      setError("");
    } catch (requestError) {
      setError(requestError.message);
    }
  }, [selectedFileId, selectedMediaId]);

  async function handleGenerateSummary() {
    if (!selectedFileId) {
      return;
    }

    setIsProcessing(true);
    setSummaryError("");

    try {
      await processFile(selectedFileId);
      const payload = await getSummary(selectedFileId);
      setSummary(payload);
      await loadFiles();
    } catch (requestError) {
      setSummaryError(requestError.message);
      setSummary(null);
    } finally {
      setIsProcessing(false);
    }
  }

  async function handleSelectFile(fileId) {
    setSelectedFileId(fileId);
    setSummary(null);
    setSummaryError("");

    try {
      const payload = await getSummary(fileId);
      setSummary(payload);
    } catch {
      setSummary(null);
    }
  }

  async function handleAsk(question, fileIds, mediaKinds = [], minScore = 0) {
    setIsAsking(true);
    setChatError("");

    try {
      const result = await askChat(question, conversationId, fileIds, mediaKinds, minScore);
      setConversationId(result.conversation_id);
      setChatSources(result.sources || []);
      const history = await getConversation(result.conversation_id);
      setMessages(history.messages || []);
    } catch (requestError) {
      setChatError(requestError.message);
    } finally {
      setIsAsking(false);
    }
  }

  async function handleStreamAsk(question, fileIds, mediaKinds = [], minScore = 0) {
    if (!question.trim()) {
      return;
    }

    setIsStreaming(true);
    setChatError("");
    setStreamingAnswer("");

    try {
      await streamChat(
        question.trim(),
        conversationId,
        fileIds,
        mediaKinds,
        minScore,
        4,
        (token) => {
          setStreamingAnswer((current) => `${current}${current ? " " : ""}${token}`);
        },
        async (payload) => {
          setConversationId(payload.conversation_id);
          setChatSources(payload.sources || []);
          const history = await getConversation(payload.conversation_id);
          setMessages(history.messages || []);
          setStreamingAnswer("");
          setIsStreaming(false);
        }
      );
    } catch (requestError) {
      setChatError(requestError.message);
      setIsStreaming(false);
    }
  }

  async function handleRegister(email, password) {
    const payload = await registerUser(email, password);
    setAuthEmail(payload.email);
    window.localStorage.setItem("auth_email", payload.email);
    setAuthStatus("Registered successfully. Please log in.");
  }

  async function handleLogin(email, password) {
    const payload = await loginUser(email, password);
    window.localStorage.setItem("access_token", payload.access_token);
    window.localStorage.setItem("refresh_token", payload.refresh_token);
    window.localStorage.setItem("auth_email", email);
    setAuthEmail(email);
    setAuthStatus("Logged in.");
    await loadFiles();
  }

  async function handleLogout() {
    window.localStorage.removeItem("access_token");
    window.localStorage.removeItem("refresh_token");
    setAuthStatus("Logged out.");
  }

  async function handleRefresh() {
    const refresh = window.localStorage.getItem("refresh_token");
    if (!refresh) {
      setAuthStatus("No refresh token available.");
      return;
    }
    const payload = await refreshToken(refresh);
    window.localStorage.setItem("access_token", payload.access_token);
    window.localStorage.setItem("refresh_token", payload.refresh_token);
    setAuthStatus("Token refreshed.");
  }

  async function handleExtractTimestamps(fileId, topic) {
    setIsExtractingTimestamps(true);
    setTimestampError("");

    try {
      const payload = await extractTimestamps(fileId, topic, 5);
      setTimestampMatches(payload.matches || []);
    } catch (requestError) {
      setTimestampError(requestError.message);
      setTimestampMatches([]);
    } finally {
      setIsExtractingTimestamps(false);
    }
  }

  function handleJumpTo(seconds) {
    setPlaybackSeconds(seconds);
  }

  function handleJumpFromSource(fileId, seconds) {
    setSelectedMediaId(fileId);
    setPlaybackSeconds(seconds);
  }

  const selectedMedia = files.find((item) => item.id === selectedMediaId) || null;

  useEffect(() => {
    loadFiles();
  }, [loadFiles]);

  return (
    <AppLayout>
      <h1>AI Document and Multimedia Q&A</h1>
      <p>Phase 3 processing and summary pipeline is ready.</p>
      <AuthPanel onLogin={handleLogin} onRegister={handleRegister} onLogout={handleLogout} email={authEmail} />
      <button type="button" onClick={handleRefresh}>Refresh Token</button>
      {authStatus ? <p className="status-message">{authStatus}</p> : null}
      <UploadPanel onUploaded={loadFiles} />
      {error ? <p className="status-message error">{error}</p> : null}
      <FileStatusList files={files} />
      <SummaryPanel
        files={files}
        selectedFileId={selectedFileId}
        onSelectFile={handleSelectFile}
        onGenerateSummary={handleGenerateSummary}
        summary={summary}
        summaryError={summaryError}
        isProcessing={isProcessing}
      />
      <ChatPanel
        files={files}
        selectedFileId={selectedFileId}
        messages={messages}
        sources={chatSources}
        onAsk={handleAsk}
        onStreamAsk={handleStreamAsk}
        onJumpFromSource={handleJumpFromSource}
        isAsking={isAsking}
        isStreaming={isStreaming}
        streamingAnswer={streamingAnswer}
        error={chatError}
      />
      <TimestampPanel
        files={files}
        selectedMediaId={selectedMediaId}
        onSelectMedia={setSelectedMediaId}
        onExtract={handleExtractTimestamps}
        matches={timestampMatches}
        error={timestampError}
        isLoading={isExtractingTimestamps}
        onJumpTo={handleJumpTo}
      />
      <MediaPlayerPanel selectedMedia={selectedMedia} jumpToSeconds={playbackSeconds} />
    </AppLayout>
  );
}
