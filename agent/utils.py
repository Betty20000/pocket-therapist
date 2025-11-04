import os
import re
from dotenv import load_dotenv
import google.generativeai as genai
import logging
logger = logging.getLogger(__name__)

# --- Load environment variables ---
load_dotenv()

# Get Gemini key
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_KEY:
    print("⚠️ Warning: GEMINI_API_KEY not set. Gemini calls will fail.")

# Configure Gemini API
genai.configure(api_key=GEMINI_KEY)

# --- Auto-select a working Gemini 2.5 model ---
def get_gemini_model():
    try:
        available = [
            m.name for m in genai.list_models()
            if "gemini-2.5" in m.name and "flash" in m.name
        ]
        model_name = available[0] if available else "gemini-flash-latest"
    except Exception:
        model_name = "gemini-flash-latest"
        print("⚠️ Could not list models, using default gemini-flash-latest")
    print(f"✅ Using model: {model_name}")
    return genai.GenerativeModel(model_name)


model = get_gemini_model()

# --- Simple keyword-based risk detection ---
NEGATIVE_KEYWORDS = [
    "kill myself", "suicide", "i want to die", "end my life", "worthless",
    "i can't go on", "hurt myself", "i'm done"
]

def detect_risk(text: str) -> bool:
    txt = text.lower()
    return any(re.search(r"\b" + re.escape(kw) + r"\b", txt) for kw in NEGATIVE_KEYWORDS)


# --- Lightweight sentiment analysis ---
def detect_sentiment(text: str) -> str:
    txt = text.lower()
    negative = ["sad", "tired", "stressed", "anxious", "angry", "depressed"]
    positive = ["happy", "good", "great", "relieved", "better", "okay"]

    if any(w in txt for w in negative):
        return "negative"
    if any(w in txt for w in positive):
        return "positive"
    return "neutral"


# --- Gemini-powered cognitive reframe ---
def gemini_reframe(thought: str) -> str:
    """Use Gemini to reframe a user's negative thought empathetically."""
    system_prompt = (
        "You are PocketTherapist, a compassionate, concise, non-judgmental "
        "assistant helping users reframe negative thoughts. Keep replies short."
    )

    user_prompt = (
        f"User negative thought: \"{thought}\"\n\n"
        "Respond with:\n"
        "1) A brief empathic reflection (1 sentence).\n"
        "2) Identify possible cognitive distortion(s) (comma separated).\n"
        "3) Offer 2 concise reframes (each a short sentence).\n"
        "4) One small actionable step the user can take now.\n\n"
        "If you detect suicidal intent, instead respond with a crisis-safety message "
        "encouraging immediate help and providing resources."
    )

    try:
        response = model.generate_content(f"{system_prompt}\n\n{user_prompt}")
        return response.text.strip()

    except Exception as e:
        print(f"❌ Gemini Error: {e}")
        return "Sorry — I'm having trouble generating a reframe right now. Please try again later."
