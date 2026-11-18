from fastapi.testclient import TestClient
from backend.main import app
c=TestClient(app)
def test_predict_expected_two():
 r=c.post('/predict',json={'rank':25000,'state':'Tamil Nadu','category':'GENERAL','course':'MBBS','year':2025}).json()
 assert not r['refused']
 assert [x['college_id'] for x in r['options']] == ['FC002','FC003']
 assert all(o['source_id'].startswith('cutoffs.csv#') for o in r['options'])
def test_predict_unsupported_year():
 r=c.post('/predict',json={'rank':1,'state':'Tamil Nadu','category':'GENERAL','year':2026}).json()
 assert r['refused'] and not r['options']
def test_predict_rank_above_cutoff():
 r=c.post('/predict',json={'rank':2000000,'state':'Tamil Nadu','category':'GENERAL'}).json()
 assert not r['options']
def test_frontend():
 assert c.get('/').status_code==200
