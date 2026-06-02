"""Quick Mistral AI connectivity check — run independently of the app."""
import os
import sys
from pathlib import Path

# Load .env manually so this script works without the app running
env_file = Path(__file__).parent.parent / ".env"
if env_file.exists():
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

api_key = os.getenv("MISTRAL_API_KEY", "")
if not api_key or api_key == "your_mistral_api_key_here":
    print("ERROR: MISTRAL_API_KEY not set in backend/.env")
    sys.exit(1)

print(f"Key loaded: {api_key[:8]}...{api_key[-4:]}")

try:
    from mistralai.client import Mistral
except ImportError:
    print("ERROR: mistralai not installed — run: pip install mistralai")
    sys.exit(1)

client = Mistral(api_key=api_key)

prompt = (
    'What are the calories in 1 cup of white rice? '
    'Return ONLY valid JSON, no markdown, no explanation: '
    '{"calories": 0, "protein_g": 0.0, "carbs_g": 0.0, "fat_g": 0.0, "serving_size": "", "confidence": 0.0}'
)

print("Sending request to mistral-small-latest...")
try:
    response = client.chat.complete(
        model="mistral-small-latest",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=256,
    )
    print("SUCCESS:")
    print(response.choices[0].message.content)
except Exception as e:
    print(f"FAILED: {e}")
    sys.exit(1)
