from app.core.config import get_settings


def summarize_text(content: str) -> tuple[str, str]:
    cleaned = " ".join(content.split())
    if not cleaned:
        return "No extractable content found.", "fallback:empty"

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
                "Summarize the following content in 5 concise bullet points. "
                "Preserve important facts and technical context.\n\n"
                f"{cleaned}"
            )
            response = llm.invoke([HumanMessage(content=prompt)])
            return response.content.strip(), f"openai:{settings.openai_model}"
        except Exception:
            pass

    truncated = cleaned[:500]
    return f"Summary: {truncated}", "fallback:extractive"
