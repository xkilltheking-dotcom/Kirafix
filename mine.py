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

@app.post("/chat")
async def chat(query: Query):

    user_text = query.prompt.lower()

    # 🧠 1. تحديد هل ده بحث ولا سؤال عام
    keywords = ["سعر", "كام", "شراء", "منتج", "عايز", "عندك"]
    is_search = any(word in user_text for word in keywords)

    found_products = []

    # 🧠 2. بحث في المنتجات
    if is_search:
        docs = db.collection('products').stream()

        for doc in docs:
            item = doc.to_dict()
            name = item.get("name", "").lower()

            # 🔥 مقارنة ذكية (مش لازم تطابق كامل)
            if any(word in name for word in user_text.split()):
                found_products.append(item)

    # 🧠 3. تجهيز البيانات
    if found_products:
        context = "المنتجات المتاحة:\n"
        for p in found_products[:5]:  # نحدد 5 بس
            context += f"- {p['name']} | السعر: {p['price']} | {p['description']}\n"
    else:
        # fallback للذكاء
        history = get_history(query.user_id)
        context = f"""
لا توجد نتائج مباشرة.

سجل المحادثة:
{history}
"""

    # 🧠 4. بناء البرومبت
    full_prompt = f"""
{SYSTEM_PROMPT}

تعليمات:
- لو فيه منتجات: رشح الأفضل
- لو مفيش: جاوب بشكل عام

{context}

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

        # 💾 حفظ الشات
        db.collection("chats").add({
            "user_id": query.user_id,
            "question": query.prompt,
            "answer": answer
        })

        return {"answer": answer}

    except:
        return {"answer": "حصل خطأ في السيرفر"}
