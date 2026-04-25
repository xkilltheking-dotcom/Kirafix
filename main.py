from fastapi import FastAPI, Request
import httpx
import firebase_admin
from firebase_admin import credentials, firestore

app = FastAPI()

# --- إعداداتك السحرية ---
PAYMOB_SECRET_KEY = "حط_هنا_الـ_Secret_Key_بتاع_بيموب"
INTEGRATION_ID_WALLET = "123456" # الـ ID بتاع المحفظة
INTEGRATION_ID_CARD = "789012"   # الـ ID بتاع الفيزا (لو عملته)

# إعداد Firebase
# تأكد من وضع ملف الخدمة (serviceAccountKey.json) بجانب الملف
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

@app.get("/get-payment-url")
async def get_url(userId: str, amount_egp: int, method: str):
    # 1. الحصول على Token
    async with httpx.AsyncClient() as client:
        auth_res = await client.post("https://accept.paymob.com/api/auth/tokens", 
                                     json={"api_key": PAYMOB_SECRET_KEY})
        token = auth_res.json()['token']

        # 2. تسجيل الطلب
        order_res = await client.post("https://accept.paymob.com/api/ecommerce/orders", 
                                      json={"auth_token": token, "amount_cents": str(amount_egp * 100), "currency": "EGP", "items": []})
        order_id = order_res.json()['id']

        # 3. الحصول على مفتاح الدفع
        integration_id = INTEGRATION_ID_WALLET if method == "wallet" else INTEGRATION_ID_CARD
        payment_res = await client.post("https://accept.paymob.com/api/accept/payment_keys", 
                                        json={
                                            "auth_token": token, "amount_cents": str(amount_egp * 100), "order_id": order_id,
                                            "billing_data": {"first_name": "Ahmed", "last_name": "Aymen", "email": "test@test.com", "phone_number": "01000000000"},
                                            "currency": "EGP", "integration_id": integration_id,
                                            "extra_description": userId # 👈 بنخزن الـ ID هنا
                                        })
        
        return {"url": f"https://accept.paymob.com/api/accept/payments/pay/{payment_res.json()['token']}"}

# الـ Webhook اللي بيموب هيكلمه أوتوماتيك
@app.post("/paymob-webhook")
async def webhook(request: Request):
    data = await request.json()
    if data['obj']['success'] is True:
        user_id = data['obj']['order']['shipping_details']['extra_description']
        amount_cents = data['obj']['amount_cents']
        
        # حسبة الكوينز (عدلها حسب رغبتك)
        coins = 700 if amount_cents == 49900 else 100 # مثال
        
        # تحديث الفايربيز
        user_ref = db.collection('users').document(user_id)
        user_ref.update({"coins": firestore.Increment(coins)})
        
        return {"status": "success"}
    return {"status": "failed"}
