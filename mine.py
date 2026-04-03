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

# 📌 History
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

    # 🔍 البحث في Firebase عن منتج قريب من رسالة المستخدم
    products_ref = db.collection('products')

    docs = products_ref.stream()

    found_info = ""

    for doc in docs:
        item = doc.to_dict()

        # لو اسم المنتج موجود في رسالة المستخدم
        if item.get('name', '').lower() in query.prompt.lower():
            found_info += f"المنتج: {item['name']}, السعر: {item['price']}, الوصف: {item['description']}\n"

    # ❗ لو مفيش نتائج
    if not found_info:
        found_info = "لم أجد معلومات محددة عن هذا المنتج في القاعدة حالياً."

    # 🧠 تجهيز البرومبت للـ AI
    full_prompt = f"""
{SYSTEM_PROMPT}

بيانات المنتجات المتوفرة:
{found_info}

سؤال المستخدم: {query.prompt}
"""

    payload = {
        "model": MODEL_NAME,
        "prompt": full_prompt,
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload)
        answer = response.json().get("response")

        return {"answer": answer}

    except:
        return {"answer": "خطأ في الاتصال بالسيرفر"}
