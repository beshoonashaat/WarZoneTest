import pandas as pd
import requests
from io import StringIO
from fastapi import FastAPI, Body
import asyncio
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import json  # 👈 مهم جداً لعمليات الـ JSON
from pywebpush import webpush, WebPushException # 👈 المكتبة اللي بتبعت الإشعارات

# 1. تعريف موديل البيانات
class NotificationPayload(BaseModel):
    title: str
    body: str

app = FastAPI()

# 2. إعدادات الـ CORS والـ VAPID
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

VAPID_PUBLIC_KEY = "BNzit0AtKjV98NKB0QTVt8wpzvpEmxpmCq6PGIbxafoJUwjy7oODmFKoMSjNykAu6vp2ZHXhD4xeLunAD5AkIdo"
VAPID_PRIVATE_KEY = "EovBlK04jq_suYT2t2ULH-gmM_d6smFSoTihYi9roPs"
VAPID_CLAIMS = {"sub": "mailto:admin@warzone.com"}

# 3. مخزن المشتركين (لازم يتعرف هنا عشان السيرفر يشوفه)
subscribers = set()

# --- المسارات الجديدة للإشعارات ---

@app.get("/admin")
async def serve_admin():
    return FileResponse("admin.html")

@app.get("/sw.js")
async def serve_sw():
    return FileResponse("sw.js", media_type="application/javascript")

@app.post("/subscribe")
async def subscribe(subscription: dict = Body(...)):
    subscribers.add(json.dumps(subscription))
    print(f"✅ مشترك جديد انضم! إجمالي المشتركين: {len(subscribers)}")
    return {"status": "success"}

@app.post("/send-notification")
async def send_notification(payload: NotificationPayload):
    message_data = json.dumps({"title": payload.title, "body": payload.body})
    inactive_subs = []
    
    print(f"🚀 محاولة إرسال إشعار لـ {len(subscribers)} جهاز...")
    
    for sub_str in subscribers:
        sub_data = json.loads(sub_str)
        try:
            webpush(
                subscription_info=sub_data,
                data=message_data,
                vapid_private_key=VAPID_PRIVATE_KEY,
                vapid_claims=VAPID_CLAIMS
            )
        except WebPushException as ex:
            print(f"❌ خطأ في جهاز: {ex}")
            # لو الجهاز مابقاش موجود (مسح الكوكيز مثلاً) بنشيله من القائمة
            if ex.response and ex.response.status_code in [404, 410]:
                inactive_subs.append(sub_str)
        except Exception as ex:
            print(f"❌ خطأ غير متوقع: {ex}")

    for sub in inactive_subs:
        subscribers.remove(sub)
        
    return {"status": "success", "sent_to": len(subscribers)}

# --- كود مزامنة البيانات القديم بتاعك (بدون تغيير) ---

SHEET_URLS = {
    "Football": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTPGvQX6sgITTWxbUXDqQzLSmQqU6TBxmZJDt0DS9pKOMNnoK7490Bn1TvNQrFlGdJZIH0Z9YPGTYb6/pub?gid=621025358&single=true&output=csv",
    "Dodgeball": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTPGvQX6sgITTWxbUXDqQzLSmQqU6TBxmZJDt0DS9pKOMNnoK7490Bn1TvNQrFlGdJZIH0Z9YPGTYb6/pub?gid=863642824&single=true&output=csv",
    "Volleyball": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTPGvQX6sgITTWxbUXDqQzLSmQqU6TBxmZJDt0DS9pKOMNnoK7490Bn1TvNQrFlGdJZIH0Z9YPGTYb6/pub?gid=1033302345&single=true&output=csv",
    "Ultimate Ball": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTPGvQX6sgITTWxbUXDqQzLSmQqU6TBxmZJDt0DS9pKOMNnoK7490Bn1TvNQrFlGdJZIH0Z9YPGTYb6/pub?gid=2017169226&single=true&output=csv",
    "Football2": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTPGvQX6sgITTWxbUXDqQzLSmQqU6TBxmZJDt0DS9pKOMNnoK7490Bn1TvNQrFlGdJZIH0Z9YPGTYb6/pub?gid=907297379&single=true&output=csv",
    "Dodgeball2": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTPGvQX6sgITTWxbUXDqQzLSmQqU6TBxmZJDt0DS9pKOMNnoK7490Bn1TvNQrFlGdJZIH0Z9YPGTYb6/pub?gid=402610111&single=true&output=csv",
    "Volleyball2": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTPGvQX6sgITTWxbUXDqQzLSmQqU6TBxmZJDt0DS9pKOMNnoK7490Bn1TvNQrFlGdJZIH0Z9YPGTYb6/pub?gid=42182221&single=true&output=csv",
    "Ultimate Ball2": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTPGvQX6sgITTWxbUXDqQzLSmQqU6TBxmZJDt0DS9pKOMNnoK7490Bn1TvNQrFlGdJZIH0Z9YPGTYb6/pub?gid=1116838793&single=true&output=csv"
}

MATCHES_URLS = {
    "Day1": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRqzlySvoK19S0Maw_xLSlUMmGcOPx6eNqiwKJKCtrHwkDxKuO95ZJKbvyNcXns8TxRe1oYnhZRtlNs/pub?gid=1977977902&single=true&output=csv",
    "Day2": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRqzlySvoK19S0Maw_xLSlUMmGcOPx6eNqiwKJKCtrHwkDxKuO95ZJKbvyNcXns8TxRe1oYnhZRtlNs/pub?gid=1547895490&single=true&output=csv",
}

all_sports_data = {k: [] for k in SHEET_URLS.keys()}
all_matches_data = {k: [] for k in MATCHES_URLS.keys()}

async def sync_all_data_loop():
    while True:
        loop = asyncio.get_event_loop()
        for sport, url in SHEET_URLS.items():
            try:
                response = await loop.run_in_executor(None, requests.get, url)
                if response.status_code == 200:
                    response.encoding = 'utf-8'
                    df = pd.read_csv(StringIO(response.text))
                    df.columns = df.columns.str.strip()
                    if 'المجموعة' in df.columns and 'نقاط' in df.columns:
                        df['نقاط'] = pd.to_numeric(df['نقاط'], errors='coerce').fillna(0)
                        df = df.sort_values(by=['المجموعة', 'نقاط'], ascending=[True, False])
                    df = df.fillna("")
                    all_sports_data[sport] = df.to_dict(orient='records')
            except Exception as e: print(f"❌ Error in {sport}: {e}")
        await asyncio.sleep(120)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(sync_all_data_loop())

@app.get("/")
async def serve_home(): return FileResponse("index.html")

@app.get("/standings/{sport_name}")
def get_standings(sport_name: str):
    data = all_sports_data.get(sport_name, [])
    groups = {}
    for entry in data:
        grp = str(entry.get('المجموعة', 'A')) or "A"
        if grp not in groups: groups[grp] = []
        groups[grp].append(entry)
    return groups

@app.get("/matches/{day_name}")
def get_matches(day_name: str):
    return all_matches_data.get(day_name, [])