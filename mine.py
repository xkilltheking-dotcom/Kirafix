import firebase_admin
from firebase_admin import credentials, firestore
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
from datetime import datetime

# إعداد Firebase
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

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
    user_id: str
    prompt: str

SYSTEM_PROMPT = """
أنت "Kirafix Ai"، مساعد ذكي احترافي. 
تتحدث باللغة العربية الفصحى دائماً.
أسلوبك جاد، دقيق، ومختصر.
"""

# 📌 دالة تجيب آخر محادثات (History)
def get_history(user_id):
    chats = db.collection("chats")\
        .where("user_id", "==", user_id)\
        .order_by("timestamp", direction=firestore.Query.DESCENDING)\
        .limit(5)\
        .stream()

    history = ""
    for chat in chats:
        data = chat.to_dict()
        history += f"المستخدم: {data['question']}\nالرد: {data['answer']}\n"

    return history


@app.post("/chat")
async def chat(query: Query):

    # 🧠 1. هات البيانات من Firebase
    docs = db.collection('info').stream()
    context_data = ""

    for doc in docs:
        context_data += f"{doc.to_dict()}\n"

    # 🧠 2. هات History
    history = get_history(query.user_id)

    # 🧠 3. بناء البرومبت
    full_prompt = f"""
{SYSTEM_PROMPT}

سجل المحادثة:
{history}

بيانات القاعدة:
{context_data}

المستخدم: {query.prompt}
"""

    payload = {
        "model": MODEL_NAME,
        "prompt": full_prompt,
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload)
        answer = response.json().get("response")

        # 💾 4. حفظ المحادثة
        db.collection("chats").add({
            "user_id": query.user_id,
            "question": query.prompt,
            "answer": answer,
            "timestamp": datetime.utcnow()
        })

        return {"answer": answer}

    except:
        return {"answer": "خطأ في الاتصال. تأكد من تشغيل Ollama."}
