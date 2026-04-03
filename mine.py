from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests

app = FastAPI()

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

SYSTEM_PROMPT = "أنت Kirafix Ai، رد باللهجة المصرية وباختصار."

@app.post("/chat")
async def chat(query: Query):

payload = {
    "model": MODEL_NAME,
    "prompt": f"""
أنت Kirafix Ai.

اتبع القواعد بدقة:
1- جاوب بمعلومة صحيحة فقط
2- ممنوع تخمين أو إضافة دول غير صحيحة
3- لو مش متأكد قول: "مش متأكد"
4- الرد يكون مختصر جدًا
5- اتكلم باللهجة المصرية البسيطة

السؤال: {query.prompt}

الإجابة:
""",
    "stream": False
}

    try:
        response = requests.post(OLLAMA_URL, json=payload)
        data = response.json()

        print("OLLAMA RESPONSE:", data)

        return {
            "answer": data.get("response") or data.get("message") or str(data)
        }

    except Exception as e:
        return {
            "answer": f"خطأ في السيرفر: {str(e)}"
        }
