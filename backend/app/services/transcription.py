def transcribe_media(file_path: str, model_name: str = "base") -> list[dict[str, float | str]]:
    import whisper

    model = whisper.load_model(model_name)
    result = model.transcribe(file_path)
    segments: list[dict[str, float | str]] = []

    for segment in result.get("segments", []):
        segments.append(
            {
                "start": float(segment.get("start", 0.0)),
                "end": float(segment.get("end", 0.0)),
                "text": str(segment.get("text", "")).strip(),
            }
        )

    if not segments:
        segments.append({"start": 0.0, "end": 0.0, "text": ""})

    return segments
