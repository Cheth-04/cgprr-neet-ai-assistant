# CGPRR — Local NEET AI assistant (Track A)

**Fully fictional data. Never use this program for real NEET counselling.** This submission-ready *prototype* combines local RAG and a deterministic synthetic college predictor. All model inference is local through **LM Studio**, not Ollama. The package includes a frontend, backend, dataset, 16-case evaluation, design note, and demo guide. Live test evidence should be generated and reviewed on the candidate's machine.

## Prerequisites (macOS Apple Silicon, 8 GB RAM intended development target)
- macOS with Python 3.11 or 3.12, Docker Desktop, and LM Studio installed. Terminal commands below assume `python3` works. Docker Desktop must be running.
- LM Studio: load an open-weight local text-capable model. The model used in the candidate's first successful live smoke test was **`qwen/qwen3-vl-4b`** (exact quantization not yet recorded). Qwen2.5 3B Instruct Q4 is an alternative, not the demonstrated model., load it, open **Developer** and start the local server on port **1234**. Use the exact model ID the server returns.
- Internet access required for first-time pip installation and the initial downloads of Qwen and local `BAAI/bge-small-en-v1.5` embeddings.
- This setup has been tested with automated local code tests in the packaging environment; **live LM Studio and Docker services must be tested on your Mac**.

## Option A: simplest — Python locally + Qdrant Docker + LM Studio locally (recommended)

1. Extract ZIP, open Terminal, enter the extracted `cgprr-neet-ai` directory:
   ```bash
   cd ~/Downloads/cgprr-neet-ai   # adjust path to where you extracted it
   bash scripts/setup_mac.sh
   ```
2. Confirm LM Studio is running and get the **exact loaded model ID**:
   ```bash
   curl http://localhost:1234/v1/models
   ```
   Edit `.env` (e.g. `nano .env`) and change `LLM_MODEL=REPLACE_WITH_YOUR_LOADED_MODEL_ID` to that ID, leaving the rest as supplied. `Ctrl+O`, Enter, `Ctrl+X` to exit nano.
3. Start the Qdrant container (do not start a second Qdrant container if port 6333 is occupied):
   ```bash
   docker compose up -d qdrant
   ```
   If you previously ran `cgprr-qdrant` on port 6333, stop it first with `docker stop cgprr-qdrant` (your old container and data remain intact).
4. Start the API:
   ```bash
   source .venv/bin/activate
   python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
   ```
5. Open second Terminal window, change to project directory, then build the Qdrant index and test:
   ```bash
   curl http://127.0.0.1:8000/health
   curl -X POST http://127.0.0.1:8000/ingest
   python3 scripts/smoke_test.py
   ```
   First ingestion takes longer as it downloads the embedding model. If /ingest reports a model download error, verify internet and retry.
6. Open **http://127.0.0.1:8000/** for the interface and **http://127.0.0.1:8000/docs** for Swagger API docs.

## Option B: Docker for API + Qdrant, LM Studio still on Mac

Use the same `.env` model ID and local LM Studio server. Enable **Serve on Local Network** in LM Studio so Docker can reach it via host.docker.internal, and restrict access to trusted devices. Be aware LM Studio network server may become reachable from your LAN. Then:
```bash
docker compose up --build -d
curl http://127.0.0.1:8000/health
curl -X POST http://127.0.0.1:8000/ingest
python3 scripts/smoke_test.py
```
Important: with Docker Compose API, Qdrant is at `http://qdrant:6333` and LM Studio at `http://host.docker.internal:1234/v1`. Containers should not use localhost to contact services on the Mac host. For the simplest reliable setup use Option A.

## Main API endpoints
- `GET /health` — dataset and configuration status
- `POST /ingest` — embed 64 synthetic rows, upsert to Qdrant
- `POST /chat` — `{"question":"What was the 2025 GENERAL closing rank for FC001?"}`
- `POST /predict` — `{"rank":25000,"state":"Tamil Nadu","category":"GENERAL","course":"MBBS","year":2025,"quota":"STATE"}`

Expected deterministic examples: FC001 GENERAL 2025 closing rank `16000`, source `cutoffs.csv#CR0005`; unsupported FC001 GENERAL 2026 must refuse; predictor with rank 25,000 + Tamil Nadu + GENERAL + MBBS + 2025 matches fictional FC002, FC003.

## Tests and evaluation
```bash
source .venv/bin/activate
python -m pytest tests/ -v
python scripts/evaluate.py         # offline deterministic tests; 2 cases SKIPPED
python scripts/evaluate.py --live  # requires live Qdrant and LM Studio; includes summary generation
```
The result CSV is generated as `evaluation_results.csv`. A **live** evaluation also generates `docs/EVALUATION_RESULTS.md`; review and commit that report if accurate. The CSV remains ignored. **Do not report offline unit-test passing as proof of live model behavior.** Read `docs/DESIGN_NOTE.md` for GPU/VRAM, privacy, cost and limitations. Read `docs/DEMO_SCRIPT.md` before recording your 3–5 minute demo.

## Troubleshooting
- `curl .../v1/models` fails: start LM Studio's Developer server; ensure correct port 1234.
- `LLM_MODEL` not configured: edit `.env` with exact model ID and restart API.
- Port 6333 allocated: stop old `cgprr-qdrant`, or choose only one Qdrant container.
- Port 8000 busy: stop prior FastAPI process with Ctrl+C; don't run native and containerized API simultaneously.
- Qdrant connection refused: check `docker compose ps`, `docker compose logs qdrant` and `curl http://localhost:6333/collections`.
- `Retrieval unavailable`: run `/ingest` before asking free-form questions.
- No answer for broad free-form question: retrieval threshold may filter out sources; inspect synthetic dataset and tune `SCORE_THRESHOLD` carefully. Never remove citation/refusal protections to fake a pass.
- Docker API cannot connect to LM Studio: run Option A, or enable local network serving and confirm `host.docker.internal:1234` is reachable.
- Mac out of memory: close other applications, use a compatible smaller Q4 model and a smaller context window, and native Python backend Option A.

## Data privacy and honest limitations
All 8 colleges and 64 cutoff records are **invented**; no student or internal business data is included. The API is bound to localhost in prescribed setup, has no authentication and is **not production-ready**. Model downloads contact external repositories initially; inference stays local. Citation ID checks reduce made-up sources but do not guarantee factual correctness in every generated sentence. No actual RTX 6000 benchmark has been run. Multi-company separation, production audit logging and authentication are design proposals rather than implemented claims.

## Disclosure
ChatGPT (AI coding assistant) was used to draft code and documentation. The candidate must test and understand the implementation and disclose any other tools used before submitting. Python and English used as required in the brief.

## Verification record and important caveats
- Candidate-reported live smoke test: **PASS**, using LM Studio model ID `qwen/qwen3-vl-4b` on an Apple MacBook Air M1 with 8 GB unified memory. Exact quantization should be confirmed using LM Studio before final submission.
- Docker end-to-end mode has not been independently confirmed; native macOS FastAPI + Qdrant Docker + LM Studio is the demonstrated workflow.
- Qdrant server is pinned to `v1.15.5`, and the Python client is constrained to the compatible `1.15–1.16` range. Reinstall requirements in the virtual environment and rebuild the API Docker image before testing it.
- The numeric grounding check rejects numerals absent from retrieved evidence, but it is not a semantic verifier. It can reject benign numbers and cannot prove factual correctness of non-numeric claims.
- Before sharing this repository, confirm the assignment recipient is permitted to access it; this take-home may be better kept private.
