# ileva-ocr — Contexto de Integração

Microserviço HTTP de extração de texto em PDF. Roda na porta `5500`.

---

## Variável de ambiente

```env
OCR_SERVICE_URL=http://localhost:5500
```

> Em produção, substitua `localhost` pelo IP ou hostname da VPS.

---

## Endpoints

### `GET /health`

Verifica se o serviço está no ar.

```
200 → { "status": "ok" }
```

---

### `POST /ocr`

Extrai texto de um arquivo PDF.

**Request:**
```
Content-Type: multipart/form-data
Campo: pdf — arquivo .pdf (máx 2 MB)
```

**Respostas:**

| Status | Situação | Body |
|--------|----------|------|
| `200` | Sucesso | `{ "texto": "..." }` |
| `400` | Arquivo não é PDF ou ultrapassa 2 MB | `{ "detail": "..." }` |
| `422` | PDF sem texto extraível | `{ "detail": "..." }` |
| `500` | Erro interno | `{ "detail": "..." }` |

---

## Exemplos de integração

### Node.js (fetch + form-data)

```js
import FormData from 'form-data';
import fetch from 'node-fetch';
import fs from 'fs';

async function extrairTexto(caminhoPdf) {
  const form = new FormData();
  form.append('pdf', fs.createReadStream(caminhoPdf), 'documento.pdf');

  const res = await fetch(`${process.env.OCR_SERVICE_URL}/ocr`, {
    method: 'POST',
    body: form,
    headers: form.getHeaders(),
  });

  if (!res.ok) {
    const err = await res.json();
    throw new Error(`OCR error ${res.status}: ${err.detail}`);
  }

  const { texto } = await res.json();
  return texto;
}
```

### Node.js (Buffer em memória)

```js
import FormData from 'form-data';
import fetch from 'node-fetch';

async function extrairTextoDobuffer(buffer, filename = 'documento.pdf') {
  const form = new FormData();
  form.append('pdf', buffer, { filename, contentType: 'application/pdf' });

  const res = await fetch(`${process.env.OCR_SERVICE_URL}/ocr`, {
    method: 'POST',
    body: form,
    headers: form.getHeaders(),
  });

  if (!res.ok) {
    const err = await res.json();
    throw new Error(`OCR error ${res.status}: ${err.detail}`);
  }

  const { texto } = await res.json();
  return texto;
}
```

### cURL

```bash
curl -X POST http://localhost:5500/ocr \
  -F "pdf=@/caminho/para/arquivo.pdf"
```

---

## Comportamento interno (pipeline por página)

O serviço processa cada página individualmente:

- **Texto nativo** → extração via `pdfminer` (rápido, sem OCR)
- **Página escaneada/imagem** → OCR via `Tesseract` (`por+eng`, 300 DPI)

Suporta PDFs puramente digitais, 100% escaneados e **híbridos** (mistura de páginas digitais e escaneadas).

---

## Limites e restrições

- Tamanho máximo: **2 MB** por arquivo
- Apenas arquivos `.pdf` são aceitos
- PDFs protegidos por senha ou corrompidos retornam `500`
- PDFs com imagens sem texto legível retornam `422`
