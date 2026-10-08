from pathlib import Path
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / '.env')

DATA_DIR = BASE_DIR / 'data'
OUTPUT_DIR = BASE_DIR / 'output'
RESUME_DIR = OUTPUT_DIR / 'resumes'
SESSION_DIR = BASE_DIR / 'sessions'
DB_PATH = DATA_DIR / 'jobs.db'

for path in (DATA_DIR, OUTPUT_DIR, RESUME_DIR, SESSION_DIR):
    path.mkdir(exist_ok=True)

TELEGRAM_API_ID = int(os.environ['TELEGRAM_API_ID'])
TELEGRAM_API_HASH = os.environ['TELEGRAM_API_HASH']
TELEGRAM_PHONE = os.getenv('TELEGRAM_PHONE', '')
JOB_GROUP_ID = int(os.environ['JOB_GROUP_ID'])

OLLAMA_URL = os.getenv('OLLAMA_URL', 'http://127.0.0.1:11434')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'qwen3:4b')
MIN_MATCH_SCORE = int(os.getenv('MIN_MATCH_SCORE', '70'))

CANDIDATE_NAME = os.getenv('CANDIDATE_NAME', 'Candidate')
CANDIDATE_EMAIL = os.getenv('CANDIDATE_EMAIL', '')
CANDIDATE_PHONE = os.getenv('CANDIDATE_PHONE', '')
CANDIDATE_LINKEDIN = os.getenv('CANDIDATE_LINKEDIN', '')
CANDIDATE_GITHUB = os.getenv('CANDIDATE_GITHUB', '')
