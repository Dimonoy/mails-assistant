import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT_PATH = Path(__file__).parent.parent.absolute()
load_dotenv(PROJECT_ROOT_PATH / '.env')

DEBUG=bool(os.environ['DEBUG'])

DATA_PATH=Path(os.environ['DATA_PATH'])

GOOGLE_CREDENTIALS_FILE=Path(os.environ['GOOGLE_CREDENTIALS_FILE'])
GOOGLE_TOKENS_DIR=Path(os.environ['GOOGLE_TOKENS_DIR'])
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

OPENAI_API_KEY = os.environ['OPENAI_API_KEY']

with open(DATA_PATH / os.environ['LLM_INSTRUCTIONS_FILE'], 'r') as f:
    LLM_INSTRUCTIONS = f.read().strip()
