# ileva-ocr

Microserviço HTTP de extração de texto em PDF com suporte a PDFs híbridos (texto nativo + páginas escaneadas).

**Porta:** `5500`  
**Stack:** Python 3.11 · FastAPI · Tesseract · pdfminer.six · pdftotext (poppler)

---

## Pipeline de extração (por página)

- Páginas com texto nativo → **pdfminer** (rápido, sem OCR)
- Páginas escaneadas/imagem → **Tesseract** (`por+eng`, 300 DPI)

PDFs puramente digitais, 100% escaneados e híbridos são todos suportados corretamente.

---

## API

| Método | Rota | Descrição |
|--------|------|-----------|
| `GET` | `/health` | Verifica se o serviço está no ar |
| `POST` | `/ocr` | Extrai texto de um PDF |

**POST /ocr**
```
Content-Type: multipart/form-data
Campo: pdf (arquivo .pdf, máx 2 MB)

Resposta 200: { "texto": "..." }
Resposta 400: arquivo inválido ou muito grande
Resposta 422: PDF sem texto extraível
Resposta 500: erro interno
```

---

## Deploy com Docker (recomendado para VPS)

```bash
# 1. Clonar o repositório
git clone <url-do-repo> ileva-ocr
cd ileva-ocr

# 2. Subir o container
docker compose up -d

# 3. Verificar
curl http://localhost:5500/health
# {"status":"ok"}
```

> **VPS com pouca RAM (≤ 1 GB)?**  
> Edite o `Dockerfile` e mude `--workers 2` para `--workers 1`.

---

## Deploy sem Docker (PM2)

```bash
# 1. Instalar dependências do sistema e iniciar com PM2
bash install.sh

# 2. Verificar
curl http://localhost:5500/health
```

---

## Variável de ambiente no sistema consumidor

```env
OCR_SERVICE_URL=http://<ip-da-vps>:5500
```

---

## Comandos úteis

```bash
# Docker
docker compose logs -f
docker compose restart
docker compose down

# PM2
pm2 list
pm2 logs ileva-ocr
pm2 restart ileva-ocr
```
