from app.core.config import get_settings
from app.services.retrieval import RetrievedChunk


def answer_question(question: str, contexts: list[RetrievedChunk]) -> tuple[str, str]:
    combined_context = "\n\n".join(item.chunk.text for item in contexts)
    settings = get_settings()

    if settings.openai_api_key:
        try:
            from langchain_openai import ChatOpenAI
            from langchain_core.messages import HumanMessage

            llm = ChatOpenAI(
                model=settings.openai_model,
                api_key=settings.openai_api_key,
                temperature=0,
            )
            prompt = (
                "You are a grounded assistant. Answer only from the provided context. "
                "If context is missing, say it clearly.\n\n"
                f"Question: {question}\n\nContext:\n{combined_context}"
            )
            response = llm.invoke([HumanMessage(content=prompt)])
            return response.content.strip(), f"openai:{settings.openai_model}"
        except Exception:
            pass

    if not contexts:
        return "I could not find relevant context in uploaded files.", "fallback:rule-based"

    top = contexts[0].chunk.text.strip()
    concise = top[:280]
    return f"Based on uploaded content: {concise}", "fallback:rule-based"
