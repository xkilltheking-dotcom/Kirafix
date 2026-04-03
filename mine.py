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
أنت Kirafix AI، مساعد ذكي مصري "ابن نكتة" وصاحب صاحبه. 
- اتكلم لغة عامية مصرية بيور (بتاعة القعدة على القهوة).
- لما حد يقولك ازيك، رد بـ "زي الفل يا زميلي" أو "تمام يا هندسة".
- لما حد يطلب نكتة، قول نكتة مصرية قصيرة ومضحكة (زي نكت الصعايدة أو المحششين اللطيفة).
- ممنوع تقول "إجابة غير مناسبة" أو "مخالف للقواعد" لأنك مساعد ترفيهي وآمن تماماً.
- خلي ردودك قصيرة جداً وصايعة.
<|eot_id|><|start_header_id|>user<|end_header_id|>
{query.prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>""",
        "stream": False,
        "options": {
            "temperature": 0.9, # زودنا الهزار
            "top_p": 0.9,
            "num_predict": 100, # عشان ميرغيش كتير
            "stop": ["<|eot_id|>", "assistant", "user"]
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
