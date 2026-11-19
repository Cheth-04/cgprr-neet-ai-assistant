# Final CGPRR submission checklist

1. Confirm LM Studio loaded model ID and quantization; update README/design note if different.
2. Reinstall Python packages after updated dependency pin: `python -m pip install -r requirements.txt`.
3. Verify Qdrant: `docker compose up -d qdrant`; check server version and API accessibility.
4. Run `python -m pytest tests/ -v`.
5. Run `python scripts/smoke_test.py` with live FastAPI, LM Studio and Qdrant.
6. Run `python scripts/evaluate.py --live`, inspect failures, verify `docs/EVALUATION_RESULTS.md`, commit the report.
7. Optional Docker deployment: stop native API, then `docker compose up --build -d`; inspect `docker compose logs api`; repeat smoke test. Docker mode is NOT claimed tested until you complete this check.
8. Reduce design note to about two pages in PDF form and verify the model, privacy and cost statements.
9. Record a 3–5 minute demo showing cited answer and refusal, plus actual evaluation.
10. Add video link to README and send GitHub repository, design note, and demo link by deadline.
11. Review repository visibility, credentials, and AI coding assistant disclosure.
