import os
import tempfile
import logging
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from app.ocr_service import extract_text

MAX_SIZE = 2 * 1024 * 1024  # 2 MB

app = FastAPI(title="OCR Service", version="1.0.0")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ocr")
async def ocr_endpoint(pdf: UploadFile = File(...)):
    if not pdf.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="O arquivo deve ser um PDF.")

    content = await pdf.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="O arquivo não pode ultrapassar 2 MB.")

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        texto = extract_text(tmp_path)
    except Exception:
        logger.exception("Erro ao processar PDF: %s", pdf.filename)
        raise HTTPException(status_code=500, detail="Erro interno ao processar o PDF.")
    finally:
        os.unlink(tmp_path)

    if not texto.strip():
        raise HTTPException(
            status_code=422,
            detail="Não foi possível extrair texto do PDF. Verifique se o arquivo é legível.",
        )

    return JSONResponse(content={"texto": texto})
