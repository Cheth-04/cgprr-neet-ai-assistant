"""Deterministic illustrative filtering of purely fictional admissions rows."""
from .data import matching_records

def predict(rank: int, state: str, category: str, course: str='MBBS', year: int=2025, quota: str='STATE'):
    filters = {'year': str(year), 'state': state, 'category': category,
               'course': course, 'quota': quota}
    records = matching_records(filters)
    options = []
    for r in records:
        closing = int(r['closing_rank'])
        if rank <= closing:
            options.append({'college_id': r['college_id'], 'college_name': r['college_name'],
              'state': r['state'], 'city': r['city'], 'course': r['course'], 'year': int(r['year']),
              'quota': r['quota'], 'round': r['round'], 'category': r['category'],
              'closing_rank': closing, 'source_id': r['source_id'],
              'reason': f'Your input rank {rank:,} is at or below this fictional historical closing rank {closing:,}.'})
    options.sort(key=lambda r:(r['closing_rank'],r['college_id']))
    return {'data':'SYNTHETIC', 'disclaimer':'Fictional illustrative records only. No prediction of actual eligibility, admission or allocation.',
            'filters':{'rank':rank, **filters}, 'matching_records':len(records), 'options': options}
