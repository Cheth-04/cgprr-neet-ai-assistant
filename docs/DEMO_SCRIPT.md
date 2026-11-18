# 3–5 minute demo recording plan

0:00–0:40: Explain clearly that the dataset is synthetic, the Qwen model is hosted locally by LM Studio, and Qdrant is local.
0:40–1:20: Show README quick start, LM Studio server loaded, `/health` and `/ingest`.
1:20–2:05: UI Q&A: "What was the 2025 GENERAL closing rank for FC001?" Display citation `cutoffs.csv#CR0005` and the matching CSV row.
2:05–2:40: UI Q&A: "What was the 2026 GENERAL closing rank for FC001?" Show refusal.
2:40–3:30: Show rank 25000, Tamil Nadu, GENERAL, MBBS, 2025 giving FC002 and FC003. Explain comparison with fictional historical closing ranks, not guaranteed admissions.
3:30–4:10: Run `python scripts/evaluate.py --live`, show `evaluation_results.csv` and actual scores.
4:10–4:40: Discuss limitations (synthetic data, local-only, approximate GPU estimate, no deployed authentication) and show design note.

Record only results you actually observed. Do not claim a GPU benchmark or zero failures unless tested.
