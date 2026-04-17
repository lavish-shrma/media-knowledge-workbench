const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

function authHeaders() {
  const token = window.localStorage.getItem("access_token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function parseJsonResponse(response, fallbackMessage) {
  if (!response.ok) {
    const payload = await response.json();
    throw new Error(payload.detail || fallbackMessage);
  }
  return response.json();
}

export async function getHealth() {
  const response = await fetch(`${API_BASE_URL}/api/v1/health`);
  if (!response.ok) {
    throw new Error("Failed to fetch health status");
  }
  return response.json();
}

export async function uploadAsset(file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/api/v1/files/upload`, {
    method: "POST",
    headers: authHeaders(),
    body: formData,
  });

  return parseJsonResponse(response, "Upload failed");
}

export async function listFiles() {
  const response = await fetch(`${API_BASE_URL}/api/v1/files`, { headers: authHeaders() });
  return parseJsonResponse(response, "Failed to load uploaded files");
}

export async function processFile(fileId) {
  const response = await fetch(`${API_BASE_URL}/api/v1/files/${fileId}/process`, {
    method: "POST",
    headers: authHeaders(),
  });

  return parseJsonResponse(response, "Failed to process file");
}

export async function getSummary(fileId) {
  const response = await fetch(`${API_BASE_URL}/api/v1/files/${fileId}/summary`, { headers: authHeaders() });
  return parseJsonResponse(response, "Failed to load summary");
}

export async function askChat(question, conversationId, fileIds, mediaKinds = [], minScore = 0, limit = 4) {
  const response = await fetch(`${API_BASE_URL}/api/v1/chat/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify({
      question,
      conversation_id: conversationId,
      file_ids: fileIds,
      media_kinds: mediaKinds,
      min_score: minScore,
      limit,
    }),
  });

  return parseJsonResponse(response, "Chat request failed");
}

export async function getConversation(conversationId) {
  const response = await fetch(`${API_BASE_URL}/api/v1/chat/conversations/${conversationId}`, { headers: authHeaders() });
  return parseJsonResponse(response, "Failed to load conversation");
}

export async function extractTimestamps(fileId, topic, limit = 5) {
  const response = await fetch(`${API_BASE_URL}/api/v1/timestamps/extract`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify({ file_id: fileId, topic, limit }),
  });

  return parseJsonResponse(response, "Failed to extract timestamps");
}

export function mediaStreamUrl(fileId) {
  return `${API_BASE_URL}/api/v1/media/${fileId}/stream`;
}

export async function streamChat(question, conversationId, fileIds, mediaKinds = [], minScore = 0, limit = 4, onChunk, onDone) {
  const params = new URLSearchParams();
  params.set("question", question);
  if (conversationId) params.set("conversation_id", String(conversationId));
  if (fileIds?.length) params.set("file_ids", fileIds.join(","));
  if (mediaKinds?.length) params.set("media_kinds", mediaKinds.join(","));
  params.set("min_score", String(minScore));
  params.set("limit", String(limit));

  const response = await fetch(`${API_BASE_URL}/api/v1/chat/stream?${params.toString()}`, {
    headers: authHeaders(),
  });

  if (!response.ok || !response.body) {
    const payload = await response.json();
    throw new Error(payload.detail || "Streaming chat failed");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) {
      break;
    }

    buffer += decoder.decode(value, { stream: true });
    const events = buffer.split("\n\n");
    buffer = events.pop() || "";

    for (const eventBlock of events) {
      const lines = eventBlock.split("\n");
      const eventLine = lines.find((line) => line.startsWith("event: ")) || "";
      const dataLine = lines.find((line) => line.startsWith("data: ")) || "";
      const eventName = eventLine.replace("event: ", "").trim();
      const data = JSON.parse(dataLine.replace("data: ", ""));

      if (eventName === "chunk" && onChunk) {
        onChunk(data.token);
      }
      if (eventName === "done" && onDone) {
        onDone(data);
      }
    }
  }
}

export async function registerUser(email, password) {
  const response = await fetch(`${API_BASE_URL}/api/v1/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  return parseJsonResponse(response, "Registration failed");
}

export async function loginUser(email, password) {
  const response = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  return parseJsonResponse(response, "Login failed");
}

export async function refreshToken(refreshToken) {
  const response = await fetch(`${API_BASE_URL}/api/v1/auth/refresh`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token: refreshToken }),
  });
  return parseJsonResponse(response, "Token refresh failed");
}
