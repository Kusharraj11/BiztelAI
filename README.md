# BiztelAI Document Copilot

A local FastAPI + React app for questions over the company PDFs. Answers use Ollama and show source documents, revisions and pages. Missing facts receive an explicit not-found response.

```text
BiztelAI/
├── backend/
│   ├── app/
│   │   ├── main.py           # API, PDF serving, production UI
│   │   └── rag.py            # ingestion, embeddings, retrieval, generation
│   ├── data/
│   │   ├── pdfs/             # four source PDFs
│   │   ├── index.json        # generated embedding cache (ignored)
│   │   └── logs/             # local logs (ignored)
│   ├── tests/test_rag.py
│   ├── evaluate.py           # ten real-model questions
│   ├── requirements.txt
│   └── requirements-dev.txt
├── frontend/
│   ├── index.html
│   ├── src/main.jsx
│   ├── src/style.css
│   ├── package.json
│   └── vite.config.js
├── start.ps1
├── THINKING.md
└── README.md
```

## Run on this Windows computer

From the project directory:

```powershell
.\start.ps1
```

Then visit **http://127.0.0.1:8000**. Keep the terminal open; Ctrl+C stops FastAPI. Ollama stays available in the background. The first request may take longer while loading the model.

## Fresh setup

Requires Python 3.14 (the installed/tested version), Node 24, and [Ollama for Windows](https://docs.ollama.com/windows). These downloads require internet; normal inference uses local APIs only.

```powershell
python -m venv backend/.venv
backend/.venv/Scripts/python -m pip install -r backend/requirements-dev.txt
ollama pull qwen3:4b
ollama pull nomic-embed-text
cd frontend
npm.cmd ci
npm.cmd run build
cd ..
.\start.ps1
```

This machine also has a project-local Ollama installation in `backend/tools/ollama`. Large binaries/models, Python environment, cache and frontend build dependencies are ignored by Git.

## Development

```powershell
# Terminal 1 (Ollama must be running)
cd backend
.venv/Scripts/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
# Terminal 2
cd frontend
npm.cmd run dev
```

Open http://127.0.0.1:5173. Vite proxies API and PDF requests. API documentation: http://127.0.0.1:8000/docs.

Optional environment variables: `OLLAMA_URL` (default `http://127.0.0.1:11434`), `OLLAMA_MODEL` (`qwen3:4b`), `EMBED_MODEL` (`nomic-embed-text`), `PDF_DIR` (default `backend/data/pdfs`). Restart after changing them. Models must already be pulled. Replacing PDFs rebuilds embeddings on the next startup. `Sample_Questions.pdf` is excluded from ingestion.

## Checks and evaluation

```powershell
cd backend
.venv/Scripts/python -m pytest -q
# With the app running:
.venv/Scripts/python evaluate.py
```

The evaluation writes `backend/evaluation-results.json` with the actual ten responses, timings and sources. Keyword checks are a regression aid, not a factuality score; review source support manually. The first five questions come from the supplied sample sheet; the other five test sampling thresholds, missing MTC, current quarantine/escalation, revision comparison and a missing bearing-replacement interval.

The revision-aware workflow, rationale, model tradeoffs and limitations are explained in [THINKING.md](THINKING.md). This is a local assessment app, without multi-user authentication or public hosting. Current means latest among supplied PDFs; verify controlled procedures in QMS.

## Troubleshooting

- Startup connection error: start Ollama and check `ollama list` contains both models.
- Missing model: run the matching `ollama pull` command.
- Source PDFs changed: restart the backend; the content hash triggers reindexing.
- Model weights changed behind the same model tag: remove `backend/data/index.json` and restart.
- Port 8000 already in use: reuse the running app or stop its terminal before restarting.
- No text extracted: the current ingest supports text PDFs; scanned pages need OCR first.

## Five additional questions and actual app answers

Recorded outputs from 12 November 2026. Bracketed numbers identify source cards for that individual request.

### 1. For a lot of 600 pieces with two minor defects and no other defects, how many samples are required and is it accepted?

**Actual app answer:** For a lot of 600 pieces, 32 samples are required. The lot is rejected because there are 2 minor defects, which exceeds the acceptable limit of 1 or fewer minor defects [1].

Sources: QC-SOP-014_Rev04_Incoming_Material_Inspection.pdf, page 1

### 2. Can we inspect or accept a lot when the supplier MTC is missing?

**Actual app answer:** No, the lot must be put on HOLD and must not be inspected or accepted until the MTC is received [1].

Sources: QC-SOP-014_Rev04_Incoming_Material_Inspection.pdf, page 2

### 3. Where should rejected material go, who holds the key, and how soon must SQE be informed?

**Actual app answer:** Rejected material is tagged with a RED tag and moved to Quarantine Cage Q1, Stores Bay 3. The key is held by the Shift QC Supervisor. The Shift QC Supervisor must inform the SQE within 4 hours of rejection [1].

Sources: QC-SOP-014_Rev04_Incoming_Material_Inspection.pdf, page 2

### 4. Compare Rev 03 and Rev 04: what changed in incoming inspection record forms and retention?

Mode: include superseded revisions for this comparison.

**Actual app answer:** In Rev 03, the incoming inspection report was paper-based and retained for 2 years [4]. In Rev 04, the report is digital (QF-07A) and retained for 5 years [3].

Sources: QC-SOP-014_Rev03_Incoming_Material_Inspection.pdf, page 1, QC-SOP-014_Rev04_Incoming_Material_Inspection.pdf, page 2, QC-SOP-014_Rev04_Incoming_Material_Inspection.pdf, page 2

### 5. What is the recommended spindle bearing replacement interval in hours for the TX-200?

**Actual app answer:** I couldn't find an answer in the provided documents.

Sources: None; the requested specification is absent from the supplied documents.

## Use from a phone on the same Wi-Fi

Run `.\start.ps1 -Lan` from the project directory, then open `http://<laptop-private-IP>:8000` on the phone. Find the Wi-Fi IPv4 address with `ipconfig`. Both devices must be on the same network. The UI and API share port 8000, so no frontend URL or CORS change is needed. Ollama stays on laptop loopback.


