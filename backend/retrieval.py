"""Local CPU embeddings, Qdrant vector search, and stable source IDs."""
from functools import lru_cache
from . import settings
from .data import joined_records, source_text


@lru_cache(maxsize=1)
def embedder():
    from fastembed import TextEmbedding
    return TextEmbedding(model_name=settings.EMBED_MODEL)


@lru_cache(maxsize=1)
def qdrant():
    from qdrant_client import QdrantClient
    return QdrantClient(url=settings.QDRANT_URL, timeout=15)


def embed(texts):
    return [list(v) for v in embedder().embed(texts)]


def ingest():
    records = joined_records()
    vectors = embed([source_text(r) for r in records])
    if not vectors:
        raise RuntimeError('Dataset is empty')
    from qdrant_client import models
    client = qdrant()
    if not client.collection_exists(settings.QDRANT_COLLECTION):
        client.create_collection(collection_name=settings.QDRANT_COLLECTION,
            vectors_config=models.VectorParams(size=len(vectors[0]), distance=models.Distance.COSINE))
    else:
        info = client.get_collection(settings.QDRANT_COLLECTION)
        # Recreate only if the vector configuration changed.
        current = info.config.params.vectors
        if getattr(current, 'size', None) != len(vectors[0]):
            client.delete_collection(settings.QDRANT_COLLECTION)
            client.create_collection(collection_name=settings.QDRANT_COLLECTION,
                vectors_config=models.VectorParams(size=len(vectors[0]), distance=models.Distance.COSINE))
    points = [models.PointStruct(id=i + 1, vector=vec,
              payload={**rec, 'text': source_text(rec)}) for i, (rec, vec) in enumerate(zip(records, vectors))]
    client.upsert(collection_name=settings.QDRANT_COLLECTION, points=points, wait=True)
    return {'indexed': len(points), 'collection': settings.QDRANT_COLLECTION, 'embedding_model': settings.EMBED_MODEL}


def search(question, limit=5, filters=None):
    from qdrant_client import models
    query_vec = embed([question])[0]
    clauses = [models.FieldCondition(key=k, match=models.MatchValue(value=v)) for k, v in (filters or {}).items()]
    query_filter = models.Filter(must=clauses) if clauses else None
    result = qdrant().query_points(collection_name=settings.QDRANT_COLLECTION,
            query=query_vec, query_filter=query_filter, limit=limit,
            score_threshold=settings.SCORE_THRESHOLD, with_payload=True)
    return [{'source_id': p.payload['source_id'], 'score': round(p.score, 3),
             'text': p.payload['text']} for p in result.points]
