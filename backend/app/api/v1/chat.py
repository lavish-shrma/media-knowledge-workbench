from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import json
from typing import Iterable

from app.core.config import get_settings
from app.db.session import get_db
from app.models.chat_conversation import ChatConversation
from app.models.chat_message import ChatMessage
from app.models.chat_source import ChatSource
from app.models.user import User
from app.schemas.chat import ChatAnswerResponse
from app.schemas.chat import ChatQueryRequest
from app.schemas.chat import ChatSourceResponse
from app.schemas.chat import ConversationHistoryResponse
from app.services.auth import get_current_user
from app.services.chatbot import answer_question
from app.services.retrieval import retrieve_chunks
from app.services.redis_store import cache_get_json
from app.services.redis_store import cache_key
from app.services.redis_store import cache_set_json
from app.services.redis_store import increment_rate_limit
from app.services.redis_store import rate_limit_key

router = APIRouter(prefix="/chat", tags=["chat"])


def _chat_signature(question: str, file_ids: list[int] | None, media_kinds: list[str] | None, min_score: float, limit: int) -> str:
    payload = {
        "question": question.strip().lower(),
        "file_ids": sorted(file_ids or []),
        "media_kinds": sorted(media_kinds or []),
        "min_score": min_score,
        "limit": limit,
    }
    return json.dumps(payload, sort_keys=True)


def _persist_chat_turn(
    db: Session,
    conversation: ChatConversation,
    question: str,
    answer: str,
    retrieved,
) -> tuple[ChatConversation, list[ChatSourceResponse]]:
    user_message = ChatMessage(conversation_id=conversation.id, role="user", content=question)
    db.add(user_message)
    db.commit()

    assistant_message = ChatMessage(conversation_id=conversation.id, role="assistant", content=answer)
    db.add(assistant_message)
    db.commit()
    db.refresh(assistant_message)

    sources: list[ChatSourceResponse] = []
    for item in retrieved:
        source = ChatSource(
            message_id=assistant_message.id,
            file_id=item.chunk.file_id,
            chunk_id=item.chunk.id,
            source_text=item.chunk.text,
            score=item.score,
            start_seconds=item.chunk.start_seconds,
            end_seconds=item.chunk.end_seconds,
        )
        db.add(source)
        sources.append(
            ChatSourceResponse(
                file_id=item.chunk.file_id,
                chunk_id=item.chunk.id,
                source_text=item.chunk.text,
                score=item.score,
                start_seconds=item.chunk.start_seconds,
                end_seconds=item.chunk.end_seconds,
            )
        )

    db.commit()
    return conversation, sources


@router.post("/query", response_model=ChatAnswerResponse)
def query_chat(
    payload: ChatQueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ChatAnswerResponse:
    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    settings = get_settings()
    if increment_rate_limit(rate_limit_key("chat", current_user.email)) > settings.rate_limit_per_minute:
        raise HTTPException(status_code=429, detail="Chat rate limit exceeded")

    signature = _chat_signature(question, payload.file_ids, payload.media_kinds, payload.min_score, payload.limit)
    cached = cache_get_json(cache_key("chat", signature))

    if payload.conversation_id:
        conversation = db.query(ChatConversation).filter(ChatConversation.id == payload.conversation_id).first()
        if conversation is None:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        conversation = ChatConversation()
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    if cached is not None and payload.conversation_id is None:
        retrieved = retrieve_chunks(
            db,
            question,
            payload.file_ids,
            payload.media_kinds,
            payload.min_score,
            payload.limit,
        )
        conversation, sources = _persist_chat_turn(db, conversation, question, cached["answer"], retrieved)
        return ChatAnswerResponse(
            conversation_id=conversation.id,
            answer=cached["answer"],
            model_name=cached["model_name"],
            sources=[ChatSourceResponse(**source) for source in cached["sources"]],
        )

    retrieved = retrieve_chunks(
        db,
        question,
        payload.file_ids,
        payload.media_kinds,
        payload.min_score,
        payload.limit,
    )
    answer, model_name = answer_question(question, retrieved)

    conversation, sources = _persist_chat_turn(db, conversation, question, answer, retrieved)
    cache_set_json(
        cache_key("chat", signature),
        {
            "answer": answer,
            "model_name": model_name,
            "sources": [source.model_dump() for source in sources],
        },
        settings.chat_cache_ttl_seconds,
    )

    return ChatAnswerResponse(
        conversation_id=conversation.id,
        answer=answer,
        model_name=model_name,
        sources=sources,
    )


@router.get("/conversations/{conversation_id}", response_model=ConversationHistoryResponse)
def get_conversation(conversation_id: int, db: Session = Depends(get_db)) -> ConversationHistoryResponse:
    conversation = db.query(ChatConversation).filter(ChatConversation.id == conversation_id).first()
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.conversation_id == conversation_id)
        .order_by(ChatMessage.created_at.asc(), ChatMessage.id.asc())
        .all()
    )

    return ConversationHistoryResponse(conversation_id=conversation_id, messages=messages)


@router.get("/stream")
def stream_chat(
    question: str,
    conversation_id: int | None = None,
    file_ids: str | None = None,
    media_kinds: str | None = None,
    min_score: float = 0.0,
    limit: int = 4,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StreamingResponse:
    question = question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    settings = get_settings()
    if increment_rate_limit(rate_limit_key("chat", current_user.email)) > settings.rate_limit_per_minute:
        raise HTTPException(status_code=429, detail="Chat rate limit exceeded")

    parsed_file_ids = [int(item) for item in file_ids.split(",") if item] if file_ids else None
    parsed_media_kinds = [item for item in media_kinds.split(",") if item] if media_kinds else None
    signature = _chat_signature(question, parsed_file_ids, parsed_media_kinds, min_score, limit)
    cached = cache_get_json(cache_key("chat", signature))

    if conversation_id:
        conversation = db.query(ChatConversation).filter(ChatConversation.id == conversation_id).first()
        if conversation is None:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        conversation = ChatConversation()
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    if cached is not None and conversation_id is None:
        answer = cached["answer"]
        model_name = cached["model_name"]
        retrieved = []
    else:
        user_message = ChatMessage(conversation_id=conversation.id, role="user", content=question)
        db.add(user_message)
        db.commit()

        retrieved = retrieve_chunks(db, question, parsed_file_ids, parsed_media_kinds, min_score, limit)
        answer, model_name = answer_question(question, retrieved)

    def event_stream() -> Iterable[str]:
        accumulated = []
        for token in answer.split():
            accumulated.append(token)
            yield f"event: chunk\ndata: {json.dumps({'token': token})}\n\n"

        if cached is None:
            assistant_message = ChatMessage(conversation_id=conversation.id, role="assistant", content=answer)
            db.add(assistant_message)
            db.commit()
            db.refresh(assistant_message)

            sources = []
            for item in retrieved:
                source = ChatSource(
                    message_id=assistant_message.id,
                    file_id=item.chunk.file_id,
                    chunk_id=item.chunk.id,
                    source_text=item.chunk.text,
                    score=item.score,
                    start_seconds=item.chunk.start_seconds,
                    end_seconds=item.chunk.end_seconds,
                )
                db.add(source)
                sources.append(
                    {
                        "file_id": item.chunk.file_id,
                        "chunk_id": item.chunk.id,
                        "source_text": item.chunk.text,
                        "score": item.score,
                        "start_seconds": item.chunk.start_seconds,
                        "end_seconds": item.chunk.end_seconds,
                    }
                )

            db.commit()
            cache_set_json(
                cache_key("chat", signature),
                {"answer": answer, "model_name": model_name, "sources": sources},
                settings.chat_cache_ttl_seconds,
            )
        else:
            sources = cached["sources"]
        yield f"event: done\ndata: {json.dumps({'conversation_id': conversation.id, 'answer': answer, 'model_name': model_name, 'sources': sources})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
