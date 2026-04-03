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
    # الـ Prompt ده بيجبر الموديل يتقمص الشخصية صح ويبعد عن الترجمة الحرفية
    payload = {
        "model": MODEL_NAME,
        "prompt": f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
أنت Kirafix AI، مساعد ذكي مصري دمك خفيف وبترد بلهجة مصرية عامية "نفس طريقة كلام الشباب في القاهرة".
قواعدك:
1. الرد يكون مصري خالص (زي: "يا باشا"، "من عينيا"، "أيوة"، "مش عارف").
2. لو سألك عن معلومة، جاوب بدقة وبسرعة.
3. ممنوع الهبد، لو مش عارف قول "والله ما عندي فكرة".
4. خليك مختصر ومفيد.
<|eot_id|><|start_header_id|>user<|end_header_id|>
{query.prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>""",
        "stream": False,
        "options": {
            "temperature": 0.7,  # عشان ميكررش الكلام
            "top_p": 0.9
        }
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
