"""Exact, deterministic access to synthetic admissions records."""
import csv
import re
from .settings import DATA_DIR


def read_csv(filename):
    with (DATA_DIR / filename).open(newline='', encoding='utf-8') as file:
        return list(csv.DictReader(file))


def joined_records():
    colleges = {r['college_id']: r for r in read_csv('colleges.csv')}
    return [{**c, **r} for r in read_csv('cutoffs.csv') if (c := colleges.get(r['college_id']))]


def source_text(rec):
    return (f"SYNTHETIC RECORD [{rec['source_id']}]: "
            f"{rec['college_name']} ({rec['college_id']}), {rec['city']}, {rec['state']}; "
            f"course={rec['course']}; year={rec['year']}; round={rec['round']}; "
            f"quota={rec['quota']}; category={rec['category']}; "
            f"opening_rank={rec['opening_rank']}; closing_rank={rec['closing_rank']}. "
            "Fictional historical example, not admission advice or a guarantee.")


def extract_constraints(question):
    """Only treat unambiguous, explicit filters as exact constraints."""
    q = question.lower()
    result = {}
    years = set(re.findall(r'\b20\d{2}\b', q))
    if len(years) == 1:
        result['year'] = next(iter(years))
    for val in ['GENERAL', 'OBC', 'SC', 'ST']:
        # word boundaries stop SC matching the word 'source'
        if re.search(r'\b' + val.lower() + r'\b', q):
            result['category'] = val
            break
    if re.search(r'\b(?:all.india|aiq)\b', q):
        result['quota'] = 'AIQ'
    elif re.search(r'\bstate quota\b', q):
        result['quota'] = 'STATE'
    if re.search(r'\bmbbs\b', q):
        result['course'] = 'MBBS'
    elif re.search(r'\bbds\b', q):
        result['course'] = 'BDS'
    for state in sorted({r['state'] for r in joined_records()}, key=len, reverse=True):
        if state.lower() in q:
            result['state'] = state
            break
    for r in read_csv('colleges.csv'):
        if r['college_id'].lower() in q or r['college_name'].lower() in q:
            result['college_id'] = r['college_id']
            break
    return result


def matching_records(filters):
    return [r for r in joined_records() if all(str(r.get(k)) == str(v) for k, v in filters.items())]


def exact_rank_answer(question):
    """Answer only fully qualified closing-rank questions without asking the LLM."""
    q = question.lower()
    if 'closing rank' not in q and 'cut-off' not in q and 'cutoff' not in q:
        return None
    filters = extract_constraints(question)
    required = {'college_id', 'year', 'category'}
    if not required.issubset(filters):
        return None
    rows = matching_records(filters)
    # require exactly one record; never silently choose a round/quota
    if len(rows) != 1:
        return {'answer': 'Not in the sources for the specified college/year/category and other filters.', 'sources': [], 'refused': True}
    r = rows[0]
    answer = (f"In the SYNTHETIC dataset, {r['college_name']} ({r['college_id']}) "
              f"had closing rank {r['closing_rank']} for {r['course']}, {r['category']}, "
              f"{r['year']}, {r['round']}, {r['quota']} quota. "
              f"Source: [{r['source_id']}]. This is fictional test data, not a real NEET cut-off.")
    return {'answer': answer, 'sources': [r['source_id']], 'refused': False}
