# services/openai_client.py
import os
from openai import OpenAI
from dotenv import load_dotenv


load_dotenv()


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("Missing OPENAI_API_KEY in environment/.env")

client = OpenAI(api_key=OPENAI_API_KEY)