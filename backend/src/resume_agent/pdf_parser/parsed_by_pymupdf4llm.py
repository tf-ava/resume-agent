import asyncio

import pymupdf
import pymupdf4llm
from fastapi import UploadFile, HTTPException, status

from src.resume_agent.schemas import ParsedResumePdf


MAX_PDF_SIZE = 10 * 1024 * 1024  # 10 MB


async def parse_pdf_to_markdown(
    pdf_bytes: bytes,
    content_type: str | None = None,
) -> ParsedResumePdf:
    """
    Parse a FastAPI UploadFile PDF into Markdown using PyMuPDF4LLM.

    CPU 密集型解析逻辑放到线程中，避免阻塞事件循环。
    """

    if content_type not in {"application/pdf", "application/x-pdf"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported.",
        )

    if not pdf_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded PDF is empty.",
        )

    if len(pdf_bytes) > MAX_PDF_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="PDF file is too large.",
        )

    try:
        markdown = await asyncio.to_thread(_parse_pdf_bytes_sync, pdf_bytes)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to parse PDF: {exc}",
        ) from exc

    return ParsedResumePdf(
        markdown_text=markdown
    )


def _parse_pdf_bytes_sync(pdf_bytes: bytes) -> str:
    """
    PyMuPDF / PyMuPDF4LLM 是同步、偏 CPU 密集型操作。
    所以这个函数保持同步，并由外层 asyncio.to_thread 调用。
    """

    doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")

    try:
        return pymupdf4llm.to_markdown(
            doc,
            header=False,
            footer=False,
        )
    finally:
        doc.close()