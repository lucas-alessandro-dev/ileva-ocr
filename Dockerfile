FROM python:3.11-slim

RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
        poppler-utils \
        tesseract-ocr \
        tesseract-ocr-por \
        tesseract-ocr-eng \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /srv/ocr

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ app/

EXPOSE 5500

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5500", "--workers", "2"]
