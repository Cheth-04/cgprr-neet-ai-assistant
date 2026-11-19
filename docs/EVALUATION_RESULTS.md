# CGPRR — Actual live evaluation results

- Run at: 2026-11-19 04:55 UTC
- Model ID reported by configuration: `qwen/qwen3-vl-4b`
- Embedding model: `BAAI/bge-small-en-v1.5`
- Collection: `neet_knowledge`
- Run mode: live (`python scripts/evaluate.py --live`)
- Results: **16 passed, 0 failed, 0 skipped** / 16 cases

| Case | Result | Details |
|---|---|---|
| E01 | PASS | In the SYNTHETIC dataset, Sample Riverbend Medical Institute (FC001) had closing rank 16000 for MBBS, GENERAL, 2025, R1, STATE quota. Source |
| E02 | PASS | In the SYNTHETIC dataset, Sample Riverbend Medical Institute (FC001) had closing rank 14800 for MBBS, GENERAL, 2024, R1, STATE quota. Source |
| E03 | PASS | In the SYNTHETIC dataset, Sample Riverbend Medical Institute (FC001) had closing rank 22400 for MBBS, OBC, 2025, R1, STATE quota. Source: [c |
| E04 | PASS | In the SYNTHETIC dataset, Sample Lotus Medical Academy (FC002) had closing rank 42035 for MBBS, GENERAL, 2025, R1, STATE quota. Source: [cut |
| E05 | PASS | In the SYNTHETIC dataset, Sample Marina Dental Academy (FC004) had closing rank 115105 for BDS, GENERAL, 2025, R1, STATE quota. Source: [cut |
| E06 | PASS | Not in the sources for the specified filters. |
| E07 | PASS | Not in the sources for the specified filters. |
| E08 | PASS | Please specify a known college ID, year and category; no rank will be guessed. |
| E09 | PASS | Not in the sources for the specified filters. |
| E10 | PASS | In the SYNTHETIC dataset, Sample Riverbend Medical Institute (FC001) had closing rank 16000 for MBBS, GENERAL, 2025, R1, STATE quota. Source |
| E11 | PASS | Sample Riverbend Medical Institute (FC001), Chennai, Tamil Nadu, offers the MBBS course for 2025 under the GENERAL category with STATE quota |
| E12 | PASS | Sample Lotus Medical Academy (FC002), Coimbatore, Tamil Nadu, offers MBBS in 2025 under the STATE quota for OBC category. The opening rank f |
| E13 | PASS | [{'college_id': 'FC002', 'college_name': 'Sample Lotus Medical Academy', 'state': 'Tamil Nadu', 'city': 'Coimbatore', 'course': 'MBBS', 'yea |
| E14 | PASS | [] |
| E15 | PASS | [{'college_id': 'FC005', 'college_name': 'Sample Sapphire Medical Institute', 'state': 'Karnataka', 'city': 'Bengaluru', 'course': 'MBBS', ' |
| E16 | PASS | In the SYNTHETIC dataset, Sample Riverbend Medical Institute (FC001) had closing rank 16000 for MBBS, GENERAL, 2025, R1, STATE quota. Source |

## Interpretation and limitations

This report records the actual run, not an assumed perfect score. Tests verify expected refusal, source IDs, exact closing ranks for structured cases, and option counts. Live RAG tests check citations and response status; they do not independently prove the semantic truth of every sentence.
All data is fictional. No RTX 6000 performance or private-data security assessment was performed. Numerical grounding is a conservative check, not full entailment verification.
