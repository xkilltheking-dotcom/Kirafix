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

@app.post("/chat")
async def chat(query: Query):
    # الـ Template ده هو السر عشان يفهم اللهجة المصرية صح
    payload = {
        "model": MODEL_NAME,
        "prompt": f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
أنت Kirafix AI، مساعد ذكي مصري. 
شخصيتك: ابن بلد، دمك خفيف، ذكي ومختصر.
طريقة الكلام: اتكلم مصري عامي زي ما بنتكلم في الشارع (مثلاً: "يا باشا"، "من عينيا"، "أيوة"، "إيه الأخبار").
ممنوع: الكلام باللغة العربية الفصحى أو ترجمة النكت الإنجليزية حرفياً.
لو حد قالك نكتة أو طلب نكتة، قول نكتة مصرية من اللي بنسمعها في القعدة.
<|eot_id|><|start_header_id|>user<|end_header_id|>
{query.prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>""",
        "stream": False,
        "options": {
            "temperature": 0.8, # زودنا الحرارة شوية عشان "الهزار" يبقى أحسن
            "top_p": 0.9,
            "stop": ["<|eot_id|>", "<|start_header_id|>"]
        }
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        data = response.json()
        answer = data.get("response", "").strip()
        
        return {"answer": answer}

    except Exception as e:
        return {"answer": "يا غالي السيرفر مهيس شوية، جرب كمان دقيقة."}
