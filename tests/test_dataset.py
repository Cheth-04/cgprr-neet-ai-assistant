import csv
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / 'data'

def load(name):
    with (DATA/name).open(newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def test_dataset_integrity():
    colleges, cutoffs = load('colleges.csv'), load('cutoffs.csv')
    ids = [x['college_id'] for x in colleges]
    record_ids = [x['record_id'] for x in cutoffs]
    assert len(colleges) == 8 and len(cutoffs) == 64
    assert len(ids) == len(set(ids))
    assert len(record_ids) == len(set(record_ids))
    assert all(r['college_id'] in ids for r in cutoffs)
    assert all(r['data_type'] == 'SYNTHETIC' for r in cutoffs)
    assert all(r['source_id'] == f"cutoffs.csv#{r['record_id']}" for r in cutoffs)
    assert all(0 < int(r['opening_rank']) <= int(r['closing_rank']) for r in cutoffs)
    assert {r['year'] for r in cutoffs} == {'2024','2025'}
    assert {r['category'] for r in cutoffs} == {'GENERAL','OBC','SC','ST'}
    assert {r['quota'] for r in cutoffs} == {'STATE'}


def test_example_prediction():
    colleges = {x['college_id']: x for x in load('colleges.csv')}
    matching = [r for r in load('cutoffs.csv') if r['year'] == '2025' and r['category'] == 'GENERAL' and r['quota'] == 'STATE' and colleges[r['college_id']]['state'] == 'Tamil Nadu' and colleges[r['college_id']]['course'] == 'MBBS' and 25000 <= int(r['closing_rank'])]
    assert {r['college_id'] for r in matching} == {'FC002', 'FC003'}
