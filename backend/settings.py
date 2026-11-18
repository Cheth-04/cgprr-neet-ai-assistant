import os
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / '.env')
DATA_DIR = ROOT / 'data'
LMSTUDIO_BASE_URL = os.getenv('LMSTUDIO_BASE_URL', 'http://localhost:1234/v1').rstrip('/')
LLM_MODEL = os.getenv('LLM_MODEL', '').strip()
QDRANT_URL = os.getenv('QDRANT_URL', 'http://localhost:6333')
QDRANT_COLLECTION = os.getenv('QDRANT_COLLECTION', 'neet_knowledge')
EMBED_MODEL = os.getenv('EMBED_MODEL', 'BAAI/bge-small-en-v1.5')
SCORE_THRESHOLD = float(os.getenv('SCORE_THRESHOLD', '0.48'))
