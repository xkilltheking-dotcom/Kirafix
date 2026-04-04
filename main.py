from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# تصريح العبور (الجسر) عشان المتصفح ميعملش Block
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# الصفحة الرئيسية (عشان تتأكد إن السيرفر شغال)
@app.get("/")
def home():
    return {"status": "Kirafix Server is Online!"}

# "ودن" السيرفر اللي بتسمع الشات
@app.get("/chat")
def chat(query: str):
    # هنا بنقول للسيرفر: خد الكلام ورجعهولي زي ما هو (لحد ما نركب مخ AI)
    return {"response": f"Sended: {query}"}
