import firebase_admin
from firebase_admin import credentials, firestore
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx # أفضل من requests في FastAPI
from datetime import datetime

# إعداد Firebase
cred = credentials.Certificate("serviceAccountKey.json")
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
db = firestore.client()

app = FastAPI()
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # بيفتح الباب للواجهة تكلم السيرفر
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.1" # تأكد من تحميله في ollama

class Query(BaseModel):
    user_id: str
    prompt: str

SYSTEM_PROMPT = """
أنت "Kirafix Ai"، مساعد ذكي لموقع إعلانات.
- مهمتك هي مساعدة المستخدمين في العثور على المنتجات والمطاعم من البيانات المقدمة لك.
- إذا وجدت إعلانات مناسبة، اذكر اسم المنتج وسعره ورابطه (إن وجد).
- تحدث بالعربية دائماً بأسلوب ودود ومختصر.
"""

# 📌 دالة لجلب سجل المحادثة
async def get_history(user_id):
    chats = db.collection("chats")\
        .where("user_id", "==", user_id)\
        .order_by("timestamp", direction=firestore.Query.DESCENDING)\
        .limit(3).stream()
    
    history = ""
    for chat in chats:
        data = chat.to_dict()
        history += f"المستخدم: {data['question']}\nالرد: {data['answer']}\n"
    return history

@app.post("/chat")
async def chat(query: Query):
    # 1. جلب الإعلانات من قاعدة البيانات (هنا بنجيب كل المنتجات، والأفضل مستقبلاً استخدام Vector DB)
    docs = db.collection('products').stream()
    all_ads = ""
    for doc in docs:
        p = doc.to_dict()
        all_ads += f"- المنتج: {p.get('name')} | السعر: {p.get('price')} | الوصف: {p.get('description')}\n"

    # 2. جلب التاريخ
    history = await get_history(query.user_id)

    # 3. بناء البرومبت النهائي (الـ Context)
    full_prompt = f"""
{SYSTEM_PROMPT}

سجل المحادثة السابق:
{history}

الإعلانات المتوفرة في الموقع حالياً:
{all_ads}

سؤال المستخدم الآن: {query.prompt}
(ملاحظة: إذا سأل عن شيء غير موجود في الإعلانات، اعتذر بلباقة وأخبره أنك لم تجد طلباً مطابقاً حالياً).
"""

    payload = {
        "model": MODEL_NAME,
        "prompt": full_prompt,
        "stream": False
    }

    try:
        # استخدام httpx لعدم تعطيل السيرفر
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(OLLAMA_URL, json=payload)
            response_data = response.json()
            answer = response_data.get("response", "عذراً، لم أستطع معالجة الرد.")

        # 💾 حفظ المحادثة في Firebase
        db.collection("chats").add({
            "user_id": query.user_id,
            "question": query.prompt,
            "answer": answer,
            "timestamp": datetime.utcnow()
        })

        return {"answer": answer}

    except Exception as e:
        print(f"Error: {e}")
        return {"answer": "حدث خطأ في الاتصال بمحرك الذكاء الاصطناعي."}
