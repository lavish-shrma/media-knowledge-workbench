from pathlib import Path


def extract_pdf_text(file_path: str) -> str:
    from pypdf import PdfReader

    reader = PdfReader(file_path)
    pages: list[str] = []

    for page in reader.pages:
        pages.append(page.extract_text() or "")

    extracted = "\n".join(pages).strip()
    if not extracted:
        # Fallback keeps the pipeline deterministic when files contain image-only pages.
        extracted = Path(file_path).name

    return extracted
