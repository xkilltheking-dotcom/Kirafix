const express = require("express");
const axios = require("axios");
const admin = require("firebase-admin");

const serviceAccount = require("./serviceAccountKey.json");

admin.initializeApp({
    credential: admin.credential.cert(serviceAccount)
});

const db = admin.firestore();

const app = express();
app.use(express.json());

const API_KEY = "YOUR_PAYMOB_API_KEY";
const INTEGRATION_ID_CARD = 123456; // فيزا
const INTEGRATION_ID_WALLET = 654321; // فودافون كاش

let authToken = "";

// 1. get auth token
async function getAuthToken() {
    const res = await axios.post("https://accept.paymob.com/api/auth/tokens", {
        api_key: API_KEY
    });
    authToken = res.data.token;
}

// API endpoint
app.get("/get-payment-url", async (req, res) => {
    const { userId, amount_egp, method } = req.query;

    try {
        await getAuthToken();

        // 2. create order
        const order = await axios.post("https://accept.paymob.com/api/ecommerce/orders", {
            auth_token: authToken,
            delivery_needed: "false",
            amount_cents: amount_egp * 100,
            currency: "EGP",
            items: []
        });

        // 3. payment key
        const paymentKey = await axios.post("https://accept.paymob.com/api/acceptance/payment_keys", {
            auth_token: authToken,
            amount_cents: amount_egp * 100,
            expiration: 3600,
            order_id: order.data.id,
            billing_data: {
                email: "test@test.com",
                first_name: "User",
                last_name: "Test",
                phone_number: "01000000000",
                city: "Cairo",
                country: "EG"
            },
            currency: "EGP",
            integration_id: method === "wallet" ? INTEGRATION_ID_WALLET : INTEGRATION_ID_CARD
        });

        // 4. iframe URL
        const iframeId = "YOUR_IFRAME_ID";
        const url = `https://accept.paymob.com/api/acceptance/iframes/${iframeId}?payment_token=${paymentKey.data.token}`;

        res.json({ url });

    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

app.post("/webhook", async (req, res) => {
    try {
        const data = req.body;

        if (data.type === "TRANSACTION" && data.obj.success === true) {

            const merchantData = data.obj.order.merchant_order_id;

            const [userId, amount] = merchantData.split("_");

            // 🔥 تحويل الفلوس لكوينز (مثال بسيط)
            const coinsMap = {
                "0.99": 100,
                "1.99": 250,
                "3.50": 500,
                "4.99": 700,
                "6.99": 1000,
                "14.99": 2550,
                "24.99": 5000,
                "39.99": 8000,
                "49.99": 10000
            };

            const coins = coinsMap[amount] || 0;

            if (coins > 0) {
                await db.collection("users").doc(userId).update({
                    coins: admin.firestore.FieldValue.increment(coins)
                });

                console.log(`تم إضافة ${coins} كوين للمستخدم ${userId}`);
            }
        }

        res.sendStatus(200);

    } catch (err) {
        console.error(err);
        res.sendStatus(500);
    }
});

app.listen(3000, () => console.log("Server running"));
