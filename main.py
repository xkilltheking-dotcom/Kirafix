from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

app = FastAPI()

# قاعدة بيانات وهمية للإعلانات (ممكن تربطها بـ SQL لاحقاً)
ADS_DATABASE = [
    {"id": 1, "title": "مطعم بيتزا نابولي", "content": "أفضل بيتزا إيطالية في المدينة، خصم 20% للطلبات أونلاين.", "link": "#"},
    {"id": 2, "title": "محل آي تك للموبايلات", "content": "أحدث هواتف آيفون وأندرويد بأفضل الأسعار وضمان سنة.", "link": "#"},
    {"id": 3, "title": "برجر كينج ستور", "content": "سندوتشات برجر مشوي على اللهب، جرب عرض العائلة الآن.", "link": "#"},
]

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat")
async def chat(message: str = Form(...)):
    # منطق البحث البسيط (اللي الـ AI بيستخدمه)
    # في النسخ المتقدمة، نرسل الرسالة للـ AI أولاً ليحدد هو الكلمات المفتاحية
    query = message.lower()
    results = []
    
    for ad in ADS_DATABASE:
        if query in ad['content'].lower() or query in ad['title'].lower() or "مطعم" in query:
            if "بيتزا" in query and "بيتزا" in ad['content']:
                results.append(ad)
            elif "برجر" in query and "برجر" in ad['content']:
                results.append(ad)
            elif "موبايل" in query and "موبايل" in ad['content']:
                results.append(ad)

    if not results:
        response_text = "للأسف ملقيتش إعلانات مطابقة لطلبك حالياً، جرب تبحث عن حاجة تانية زي 'بيتزا' أو 'موبايل'."
    else:
        response_text = f"لقيت لك {len(results)} إعلانات مهتمة بطلبك:"
    
    return {"reply": response_text, "ads": results}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
