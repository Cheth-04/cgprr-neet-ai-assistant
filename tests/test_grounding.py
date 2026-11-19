from backend.grounding import numbers_in, numerical_claims_supported

EVIDENCE = [{'source_id': 'cutoffs.csv#CR0005',
    'text': 'SYNTHETIC [cutoffs.csv#CR0005] FC001, year=2025, opening_rank=9920, closing_rank=16000.'}]

def test_known_numbers_accepted():
    assert numerical_claims_supported('In 2025 closing rank 16,000 [cutoffs.csv#CR0005]', EVIDENCE)

def test_injected_false_rank_rejected():
    assert not numerical_claims_supported('Closing rank 1 [cutoffs.csv#CR0005]', EVIDENCE)

def test_unsupported_extra_number_rejected():
    assert not numerical_claims_supported('Closing rank 16000, 99 seats [cutoffs.csv#CR0005]', EVIDENCE)

def test_ids_not_treated_as_numbers():
    assert 1 not in numbers_in('FC001 [cutoffs.csv#CR0005]')

def test_rejected_valid_citation_wrong_number_in_endpoint(monkeypatch):
    import backend.main as main
    from fastapi.testclient import TestClient
    monkeypatch.setattr(main, 'search', lambda q, filters: EVIDENCE)
    monkeypatch.setattr(main, 'generate', lambda q, records: 'Closing rank 1 [cutoffs.csv#CR0005].')
    result=TestClient(main.app).post('/chat',json={'question':'Summarize FC001 for 2025 GENERAL.'}).json()
    assert result['refused'] is True and result['sources']==[]
