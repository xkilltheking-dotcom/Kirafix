from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# تصريح العبور (الجسر) - ده اللي هيحل "تعذر الاتصال"
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "Online"}

@app.get("/chat")
def chat(query: str):
    # جرب نغير "response" لـ "text" لأن أغلب الواجهات بتدور على الاسم ده
    return {"text": f"Kirafix Ai: {query}"}
