"""Offline deterministic 16-case evaluation. Run --live for real services (including LM Studio)."""
import argparse, csv, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from fastapi.testclient import TestClient
from backend.main import app
client=TestClient(app)
CASES=json.loads((ROOT/'data'/'evaluation_questions.json').read_text())

def run(live=False):
    if live:
        r=client.post('/ingest');r.raise_for_status()
    rows=[]
    for item in CASES:
        if item['needs_live'] and not live:
            rows.append({'id':item['id'],'status':'SKIP','details':'Needs Qdrant and LM Studio'});continue
        r=client.post(item['endpoint'],json=item['request'])
        got=r.json();ok=r.status_code==200
        if 'expect_refused' in item:ok=ok and got.get('refused') is item['expect_refused']
        if 'expect_source' in item:ok=ok and item['expect_source'] in got.get('sources',[])
        if 'expect_count' in item:ok=ok and len(got.get('options',[]))==item['expect_count']
        rows.append({'id':item['id'],'status':'PASS' if ok else 'FAIL','details':str(got.get('answer',got.get('options','')))[:100]})
    out=ROOT/'evaluation_results.csv'
    with out.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['id','status','details']);w.writeheader();w.writerows(rows)
    from collections import Counter
    summary=Counter(x['status'] for x in rows)
    print('Evaluation:',dict(summary),'saved to',out)
    for row in rows:print(row['id'],row['status'],row['details'])
    return 1 if summary['FAIL'] else 0
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--live',action='store_true');args=parser.parse_args()
    sys.exit(run(args.live))
