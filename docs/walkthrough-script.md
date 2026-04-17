# Walkthrough Video Script

## Opening
1. Introduce the application as a full-stack AI-powered document and multimedia Q&A system.
2. State the supported file types: PDF, audio, and video.
3. Mention the main capabilities: upload, summarize, ask questions, extract timestamps, and jump playback.

## Step 1: Upload Files
1. Show the upload panel in the frontend.
2. Upload a PDF and show the queued status.
3. Upload an audio file and a video file.
4. Point out that uploaded files appear in the file list.

## Step 2: Summaries
1. Select a processed file.
2. Trigger summary generation.
3. Show the summary card and the persisted summary status.

## Step 3: Chatbot Questions
1. Ask a question about uploaded content.
2. Show the assistant response grounded in uploaded sources.
3. Highlight the source citation list and conversation history.

## Step 4: Timestamp Extraction
1. Choose an audio or video file.
2. Enter a topic and extract timestamps.
3. Show the ranked timestamp matches.

## Step 5: Playback Jump
1. Click a timestamp result or source playback button.
2. Show media playback jumping to the indicated time.
3. Demonstrate that audio/video can be resumed from the relevant segment.

## Step 6: Backend and Ops
1. Mention FastAPI backend, PostgreSQL with pgvector, and Redis.
2. Show the Docker Compose setup instructions from the README.
3. Mention the GitHub Actions pipeline and coverage gate.

## Closing
1. Summarize the requirement coverage.
2. Mention that the bonus features are pending or planned after core approval.
3. End with the repository and local run instructions.
