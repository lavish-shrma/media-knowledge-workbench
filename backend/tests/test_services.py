import sys
import types

from app.services.pdf_extractor import extract_pdf_text
from app.services.summarizer import summarize_text
from app.services.transcription import transcribe_media
from app.services.chatbot import answer_question
from app.services.retrieval import RetrievedChunk


class _DummyPage:
    def __init__(self, text: str) -> None:
        self._text = text

    def extract_text(self) -> str:
        return self._text


class _DummyPdfReader:
    def __init__(self, _path: str) -> None:
        self.pages = [_DummyPage("first page"), _DummyPage("second page")]


class _DummyWhisperModel:
    def transcribe(self, _path: str) -> dict:
        return {
            "segments": [
                {"start": 0, "end": 1.5, "text": "hello"},
                {"start": 2, "end": 3.0, "text": "world"},
            ]
        }


def test_extract_pdf_text_uses_reader(monkeypatch) -> None:
    monkeypatch.setitem(sys.modules, "pypdf", types.SimpleNamespace(PdfReader=_DummyPdfReader))

    output = extract_pdf_text("dummy.pdf")

    assert output == "first page\nsecond page"


def test_transcribe_media_maps_segments(monkeypatch) -> None:
    whisper_module = types.SimpleNamespace(load_model=lambda _name: _DummyWhisperModel())
    monkeypatch.setitem(sys.modules, "whisper", whisper_module)

    output = transcribe_media("clip.mp3", "base")

    assert len(output) == 2
    assert output[0]["text"] == "hello"


def test_summarize_text_fallback_when_no_api_key(monkeypatch) -> None:
    class _Settings:
        openai_api_key = ""
        openai_model = "gpt-4o-mini"

    monkeypatch.setattr("app.services.summarizer.get_settings", lambda: _Settings())

    summary, model_name = summarize_text("This is content to summarize.")

    assert summary.startswith("Summary:")
    assert model_name == "fallback:extractive"


def test_summarize_text_openai_branch(monkeypatch) -> None:
    class _Settings:
        openai_api_key = "secret"
        openai_model = "gpt-4o-mini"

    class _Message:
        def __init__(self, content: str) -> None:
            self.content = content

    class _ChatModel:
        def __init__(self, **_kwargs) -> None:
            pass

        def invoke(self, _messages):
            return types.SimpleNamespace(content="bullet summary")

    monkeypatch.setattr("app.services.summarizer.get_settings", lambda: _Settings())
    monkeypatch.setitem(sys.modules, "langchain_openai", types.SimpleNamespace(ChatOpenAI=_ChatModel))
    monkeypatch.setitem(sys.modules, "langchain_core.messages", types.SimpleNamespace(HumanMessage=_Message))

    summary, model_name = summarize_text("Important content")

    assert summary == "bullet summary"
    assert model_name == "openai:gpt-4o-mini"


def test_summarize_text_empty_content(monkeypatch) -> None:
    class _Settings:
        openai_api_key = ""
        openai_model = "gpt-4o-mini"

    monkeypatch.setattr("app.services.summarizer.get_settings", lambda: _Settings())

    summary, model_name = summarize_text("   ")

    assert summary == "No extractable content found."
    assert model_name == "fallback:empty"


def test_answer_question_fallback_without_context(monkeypatch) -> None:
    class _Settings:
        openai_api_key = ""
        openai_model = "gpt-4o-mini"

    monkeypatch.setattr("app.services.chatbot.get_settings", lambda: _Settings())

    answer, model_name = answer_question("question", [])

    assert "could not find relevant context" in answer
    assert model_name == "fallback:rule-based"


def test_answer_question_openai_branch(monkeypatch) -> None:
    class _Settings:
        openai_api_key = "secret"
        openai_model = "gpt-4o-mini"

    class _Message:
        def __init__(self, content: str) -> None:
            self.content = content

    class _ChatModel:
        def __init__(self, **_kwargs) -> None:
            pass

        def invoke(self, _messages):
            return types.SimpleNamespace(content="assistant response")

    chunk = types.SimpleNamespace(text="context block")
    retrieved = [RetrievedChunk(chunk=chunk, score=0.9)]

    monkeypatch.setattr("app.services.chatbot.get_settings", lambda: _Settings())
    monkeypatch.setitem(sys.modules, "langchain_openai", types.SimpleNamespace(ChatOpenAI=_ChatModel))
    monkeypatch.setitem(sys.modules, "langchain_core.messages", types.SimpleNamespace(HumanMessage=_Message))

    answer, model_name = answer_question("What?", retrieved)

    assert answer == "assistant response"
    assert model_name == "openai:gpt-4o-mini"
