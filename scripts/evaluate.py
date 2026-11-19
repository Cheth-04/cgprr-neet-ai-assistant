"""Offline/live evaluation with actual rank assertions and an auditable Markdown report."""
import argparse
import csv
import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from fastapi.testclient import TestClient
from backend.main import app
from backend import settings

CASES = json.loads((ROOT / 'data/evaluation_questions.json').read_text())
client = TestClient(app)


def check_case(case, response):
    actual = response.json()
    failures = []
    if response.status_code != 200:
        failures.append(f'HTTP {response.status_code}')
        return actual, failures
    if 'expect_refused' in case and actual.get('refused') is not case['expect_refused']:
        failures.append(f'refused expected {case["expect_refused"]}, got {actual.get("refused")}')
    if 'expect_source' in case and case['expect_source'] not in actual.get('sources', []):
        failures.append('expected source missing')
    if 'expect_source' in case and f'[{case["expect_source"]}]' not in actual.get('answer',''):
        failures.append('citation not in answer text')
    if 'expect_count' in case and len(actual.get('options', [])) != case['expect_count']:
        failures.append(f'expected {case["expect_count"]} options, got {len(actual.get("options", []))}')
    if 'expect_closing_rank' in case:
        # Match a complete numeric rank, not a substring (e.g. 1 vs 16000).
        matches = re.findall(r'closing rank\s*[:=]?\s*([\d,]+)', actual.get('answer',''), re.I)
        ranks = [int(m.replace(',', '')) for m in matches]
        if not ranks or any(rank != case['expect_closing_rank'] for rank in ranks):
            failures.append(f'expected closing rank {case["expect_closing_rank"]}, found {ranks}')
    return actual, failures


def run(live=False):
    if live:
        response=client.post('/ingest')
        response.raise_for_status()
    results=[]
    for case in CASES:
        if case['needs_live'] and not live:
            results.append({'id':case['id'], 'status':'SKIP', 'details':'Needs live Qdrant and LM Studio'})
            continue
        try:
            resp=client.post(case['endpoint'],json=case['request'])
            actual,issues=check_case(case,resp)
            details='; '.join(issues) if issues else str(actual.get('answer', actual.get('options','')))[:140]
            results.append({'id':case['id'],'status':'FAIL' if issues else 'PASS','details':details})
        except Exception as exc:
            results.append({'id':case['id'],'status':'FAIL','details':f'{type(exc).__name__}: {exc}'[:200]})
    csv_path=ROOT/'evaluation_results.csv'
    with csv_path.open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=['id','status','details'])
        writer.writeheader();writer.writerows(results)
    counts=Counter(r['status'] for r in results)
    print('Evaluation:',dict(counts),'saved to',csv_path)
    for record in results:print(record['id'],record['status'],record['details'])
    if live:
        report=ROOT/'docs'/'EVALUATION_RESULTS.md'
        timestamp=datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
        lines=[
            '# CGPRR — Actual live evaluation results','',
            f'- Run at: {timestamp}',
            f'- Model ID reported by configuration: `{settings.LLM_MODEL}`',
            f'- Embedding model: `{settings.EMBED_MODEL}`',
            f'- Collection: `{settings.QDRANT_COLLECTION}`',
            '- Run mode: live (`python scripts/evaluate.py --live`)',
            f'- Results: **{counts["PASS"]} passed, {counts["FAIL"]} failed, {counts["SKIP"]} skipped** / {len(results)} cases','',
            '| Case | Result | Details |','|---|---|---|',
        ]
        for record in results:
            escaped=record['details'].replace('|', r'\|').replace('\n',' ')[:160]
            lines.append(f'| {record["id"]} | {record["status"]} | {escaped} |')
        lines += ['', '## Interpretation and limitations','',
                  'This report records the actual run, not an assumed perfect score. Tests verify expected refusal, source IDs, exact closing ranks for structured cases, and option counts. Live RAG tests check citations and response status; they do not independently prove the semantic truth of every sentence.',
                  'All data is fictional. No RTX 6000 performance or private-data security assessment was performed. Numerical grounding is a conservative check, not full entailment verification.']
        report.write_text('\n'.join(lines)+'\n',encoding='utf-8')
        print('Actual live report saved to:',report)
    return 1 if counts['FAIL'] else 0

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--live',action='store_true')
    args=parser.parse_args()
    sys.exit(run(args.live))
