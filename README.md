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

## Setup rápido (dev)

Para rodar localmente sem Docker:

```bash
# 1. Dependências de sistema (uma vez só)
sudo apt-get update -y
sudo apt-get install -y poppler-utils tesseract-ocr tesseract-ocr-por tesseract-ocr-eng \
    python3 python3-pip python3-venv

# 2. Ambiente Python (uma vez só)
python3 -m venv venv
./venv/bin/pip install -r requirements.txt

# 3. Subir o servidor (--reload recarrega ao salvar)
./venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 5500 --reload

# 4. Verificar
curl http://localhost:5500/health
# {"status":"ok"}
```

> O `--reload` é só para desenvolvimento. Em produção, troque por `--workers 2` (ver seção PM2 abaixo).

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

## Segurança

### Firewall (isolamento por rede)

O `ileva-ocr` não deve ser exposto à internet. Libere a porta `5500` apenas para os IPs dos serviços autorizados:

```bash
ufw deny 5500
ufw allow from <IP_DO_SERVICO> to any port 5500
```

Para adicionar novos serviços no futuro, basta adicionar mais regras:

```bash
ufw allow from <IP_NOVO_SERVICO> to any port 5500
```

### API Key por serviço

Cada serviço consumidor deve ter sua própria chave. Configure no `ileva-ocr`:

```env
# ileva-ocr — lista de chaves autorizadas separadas por vírgula
OCR_API_KEYS=chave-servico-a,chave-servico-b
```

Todas as requisições ao `POST /ocr` devem incluir o header:

```
X-API-Key: <chave-do-servico>
```

O endpoint `GET /health` é público (usado por healthchecks).

---

## Variáveis de ambiente no sistema consumidor

```env
OCR_SERVICE_URL=http://<ip-da-vps>:5500
OCR_API_KEY=<chave-deste-servico>
```

Exemplo de chamada com a chave (Node.js):

```js
const res = await fetch(`${process.env.OCR_SERVICE_URL}/ocr`, {
  method: 'POST',
  body: form,
  headers: {
    ...form.getHeaders(),
    'X-API-Key': process.env.OCR_API_KEY,
  },
});
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
