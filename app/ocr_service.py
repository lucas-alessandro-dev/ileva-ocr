import re
import subprocess
import logging
from pdf2image import convert_from_path
import pytesseract
from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams, LTTextBox
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator

logger = logging.getLogger(__name__)

_MIN_TEXT_CHARS = 20


def _clean(text: str) -> str:
    text = re.sub(r'[ \t]+\n', '\n', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def _count_pages(pdf_path: str) -> int:
    try:
        result = subprocess.run(
            ["pdfinfo", pdf_path],
            capture_output=True, text=True, timeout=10,
        )
        for line in result.stdout.splitlines():
            if line.startswith("Pages:"):
                return int(line.split(":")[1].strip())
    except Exception:
        pass
    with open(pdf_path, "rb") as f:
        count = sum(1 for _ in PDFPage.get_pages(f))
    return count


def _extract_page_text_pdfminer(pdf_path: str, page_number: int) -> str:
    """Extrai texto de uma página específica (0-indexed) via pdfminer."""
    rsrcmgr = PDFResourceManager()
    laparams = LAParams()
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)

    with open(pdf_path, "rb") as f:
        for i, page in enumerate(PDFPage.get_pages(f)):
            if i != page_number:
                continue
            interpreter.process_page(page)
            layout = device.get_result()
            parts = []
            for element in layout:
                if isinstance(element, LTTextBox):
                    parts.append(element.get_text())
            return "".join(parts)
    return ""


def _page_has_text(pdf_path: str, page_number: int) -> bool:
    text = _extract_page_text_pdfminer(pdf_path, page_number)
    return len(text.strip()) >= _MIN_TEXT_CHARS


def _ocr_page(image) -> str:
    return pytesseract.image_to_string(image, lang="por+eng", config="--psm 3")


def extract_text(pdf_path: str) -> str:
    """
    Per-page hybrid extraction pipeline:
      - Pages with native text → pdfminer (fast, accurate)
      - Pages without text (scanned/image) → Tesseract OCR
    Handles mixed PDFs correctly instead of stopping at the first success.
    """
    total_pages = _count_pages(pdf_path)
    logger.info("PDF com %d página(s): %s", total_pages, pdf_path)

    scanned_pages = [
        i for i in range(total_pages)
        if not _page_has_text(pdf_path, i)
    ]

    if not scanned_pages:
        logger.info("Todas as páginas têm texto nativo — extração via pdfminer")
        parts = [_extract_page_text_pdfminer(pdf_path, i) for i in range(total_pages)]
        return _clean("\n\n".join(parts))

    if len(scanned_pages) == total_pages:
        logger.info("PDF 100%% escaneado — OCR em todas as páginas via Tesseract")
        images = convert_from_path(pdf_path, dpi=300)
        parts = []
        for i, img in enumerate(images):
            parts.append(_ocr_page(img))
            logger.info("OCR página %d/%d", i + 1, total_pages)
        return _clean("\n\n".join(parts))

    logger.info(
        "PDF híbrido: %d página(s) escaneada(s) de %d — aplicando OCR seletivo",
        len(scanned_pages), total_pages,
    )
    images = convert_from_path(pdf_path, dpi=300)
    parts = []
    for i in range(total_pages):
        if i in scanned_pages:
            logger.info("Página %d/%d → OCR (Tesseract)", i + 1, total_pages)
            parts.append(_ocr_page(images[i]))
        else:
            logger.info("Página %d/%d → texto nativo (pdfminer)", i + 1, total_pages)
            parts.append(_extract_page_text_pdfminer(pdf_path, i))

    return _clean("\n\n".join(parts))
