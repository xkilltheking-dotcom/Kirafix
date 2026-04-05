import ollama  # تأكد إنك محمل مكتبة ollama ومفعل موديل مثل llama3
from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse

app = FastAPI()

# قاعدة بياناتك (كمثال)
ADS_DATABASE = [
    {"title": "بيتزا السلطان", "content": "أقوى عرض بيتزا في المنصورة، اطلب 2 والثالثة هدية."},
    {"title": "محل تيك زون", "content": "تصليح جميع أنواع الموبايلات في أسرع وقت."},
]

@app.post("/chat")
async def chat(message: str = Form(...)):
    # 1. بنسأل الـ AI الأول: هل المستخدم بيسأل عن خدمة/منتج؟ ولا ده مجرد سلام؟
    system_prompt = f"""
    أنت مساعد ذكي لموقع إعلانات. 
    قاعدة البيانات المتاحة عندك حالياً هي: {ADS_DATABASE}
    إذا سألك المستخدم عن منتج، ابحث في القاعدة وأعطه التفاصيل.
    إذا سلم عليك (مثل: ازيك، سلام، مرحبا)، رد عليه بلباقة وأخبره كيف يمكنك مساعدته.
    اجعل ردك دائماً باللهجة المصرية الودودة.
    """
    
    try:
        response = ollama.chat(model='llama3', messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': message},
        ])
        
        reply = response['message']['content']
        return {"reply": reply, "ads": []} # الـ AI هنا هيدمج النتائج جوه الرد نفسه
    except Exception as e:
        return {"reply": "حصلت مشكلة صغيرة في التفكير، جرب تاني كمان شوية!"}
