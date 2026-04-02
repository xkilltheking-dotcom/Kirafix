from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests

app = FastAPI()

# فك حظر المتصفح (CORS) لربط الـ Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.1"

class Query(BaseModel):
    prompt: str

# التعليمات الخاصة بـ Kirafix Ai
SYSTEM_PROMPT = """
أنت الآن Kirafix Ai، المساعد الذكي الرسمي والوحيد لموقعنا.
- ممنوع تقول إنك تطوير Meta أو OpenAI.
- لو حد سألك "أنت مين؟" رد بـ "أنا Kirafix Ai، مساعدكم الذكي هنا".
- الإجابة تكون باللهجة المصرية وسريعة.
"""

@app.post("/chat")
async def chat(query: Query):
    payload = {
        "model": MODEL_NAME,
        "prompt": f"{SYSTEM_PROMPT}\nالمستخدم: {query.prompt}",
        "stream": False
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload)
        return {"answer": response.json().get("response")}
    except:
        return {"answer": "السيرفر مش واصل.. تأكد إن Ollama شغال."}

# للتشغيل: uvicorn main:app --reload
