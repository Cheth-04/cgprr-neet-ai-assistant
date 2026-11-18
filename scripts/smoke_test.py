"""Live smoke checks. Needs running FastAPI, Qdrant and LM Studio."""
import json, os, sys, urllib.request
BASE=os.getenv('API_URL','http://127.0.0.1:8000')
def call(path,body=None):
    data=None if body is None else json.dumps(body).encode()
    req=urllib.request.Request(BASE+path,data=data,headers={'Content-Type':'application/json'} if data else {},method='POST' if data else 'GET')
    with urllib.request.urlopen(req,timeout=180) as r: return json.loads(r.read())
try:
    print('HEALTH:',call('/health'))
    print('INGEST:',call('/ingest', {}))
    good=call('/chat',{'question':'What was the 2025 GENERAL closing rank for FC001?'})
    print('SUPPORTED:',good);assert not good['refused'] and good['sources']
    refusal=call('/chat',{'question':'What was the 2026 GENERAL closing rank for FC001?'})
    print('REFUSAL:',refusal);assert refusal['refused']
    options=call('/predict',{'rank':25000,'state':'Tamil Nadu','category':'GENERAL','course':'MBBS','year':2025,'quota':'STATE'})
    print('PREDICT:',[(o['college_id'],o['source_id']) for o in options['options']]);assert len(options['options'])==2
    summary=call('/chat',{'question':'Summarize FC001 for 2025 GENERAL.'})
    print('LOCAL LLM:',summary)
    assert not summary['refused'], 'Local LLM summary refused; inspect LM Studio response and retrieval threshold'
    print('LIVE SMOKE PASSED')
except Exception as e:
    print('LIVE SMOKE FAILED:',repr(e),file=sys.stderr);sys.exit(1)
