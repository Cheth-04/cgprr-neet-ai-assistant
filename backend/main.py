from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from .predictor import predict
from pydantic import BaseModel, Field
from . import settings
from .data import exact_rank_answer, extract_constraints, matching_records, joined_records
from .retrieval import ingest, search
from .llm import generate

app = FastAPI(title='CGPRR Synthetic NEET RAG', version='0.3.0',
    description='LOCAL ONLY. All college and rank data is fictional.')


class ChatRequest(BaseModel):
    question: str = Field(min_length=3, max_length=1000)


@app.get('/health')
def health():
    return {'status': 'ok', 'dataset_records': len(joined_records()),
            'llm_model': settings.LLM_MODEL or 'NOT_CONFIGURED', 'data': 'SYNTHETIC'}


@app.post('/ingest')
def build_index():
    try:
        return ingest()
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f'Ingestion unavailable: {exc}') from exc


@app.post('/chat')
def chat(request: ChatRequest):
    q = request.question
    filters = extract_constraints(q)
    # Do not allow a 2026 question to match a different year.
    if filters and not matching_records(filters):
        return {'answer': 'Not in the sources for the specified filters.',
                'sources': [], 'refused': True, 'data': 'SYNTHETIC'}
    # An exact rank claim requires a unique college, year and category.
    if any(term in q.lower() for term in ('closing rank', 'cut-off', 'cutoff')):
        if not {'college_id', 'year', 'category'}.issubset(filters):
            return {'answer': 'Please specify a known college ID, year and category; no rank will be guessed.',
                    'sources': [], 'refused': True, 'data': 'SYNTHETIC'}
    exact = exact_rank_answer(q)
    if exact is not None:
        return {**exact, 'data': 'SYNTHETIC'}
    # Retrieval only sees records consistent with the stated constraints.
    try:
        records = search(q, filters=filters)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f'Retrieval unavailable; run /ingest first: {exc}') from exc
    if not records:
        return {'answer': 'Not in the sources.', 'sources': [], 'refused': True, 'data': 'SYNTHETIC'}
    try:
        answer = generate(q, records)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f'Local LLM unavailable: {exc}') from exc
    # Only return source IDs actually supplied to the LLM and cited in its answer.
    cited = [r['source_id'] for r in records if f"[{r['source_id']}]" in answer]
    if answer.lower().startswith('not in the sources') or not cited:
        return {'answer': 'Not in the sources.', 'sources': [], 'refused': True, 'data': 'SYNTHETIC'}
    return {'answer': answer, 'sources': cited, 'refused': False, 'data': 'SYNTHETIC'}


class PredictRequest(BaseModel):
    rank: int = Field(ge=1, le=2000000)
    state: str
    category: str
    course: str = 'MBBS'
    year: int = 2025
    quota: str = 'STATE'


@app.post('/predict')
def college_predict(request: PredictRequest):
    # Reject unknown combinations rather than fabricate options.
    if request.state not in ('Tamil Nadu', 'Karnataka') or request.category not in ('GENERAL','OBC','SC','ST') or request.course not in ('MBBS','BDS') or request.quota != 'STATE' or request.year not in (2024,2025):
        return {'data':'SYNTHETIC','refused':True,'options':[], 'answer':'Not in the sources for the selected filters.'}
    return {**predict(**request.model_dump()), 'refused':False}


@app.get('/')
def home():
    return FileResponse(settings.ROOT / 'frontend' / 'index.html')

app.mount('/static', StaticFiles(directory=str(settings.ROOT / 'frontend')), name='static')
