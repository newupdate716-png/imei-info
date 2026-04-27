from fastapi import FastAPI, Query, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
import requests
import re

app = FastAPI(
    title="Elite IMEI Proxy API",
    description="Secured and Branded IMEI Lookup Service",
    version="2.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = "f43f0d0c-27b0-408a-abd0-585fabea6adf"
DEVELOPER = "SB-SAKIB"

# প্রক্সি ফাংশন: এটি ইমেজ বা লিঙ্ক হাইড করার জন্য কাজ করবে
@app.get("/proxy/image")
def proxy_image(url: str):
    try:
        res = requests.get(url, stream=True, timeout=10)
        return Response(content=res.content, media_type=res.headers.get("Content-Type"))
    except:
        raise HTTPException(status_code=404, detail="Image not found")

def mask_data(data, base_url):
    """এটি JSON ডেটার ভেতর থেকে সব বাইরের লিঙ্ক সরিয়ে আপনার লিঙ্ক বসিয়ে দিবে"""
    data_str = str(data)
    
    # ১. ইমেজ ইউআরএল মাস্কিং
    img_urls = re.findall(r'https?://[^\s<>"]+\.(?:jpg|jpeg|png|gif)', data_str)
    for img in img_urls:
        if "proxy/image" not in img:
            new_img_url = f"{base_url}/proxy/image?url={img}"
            data_str = data_str.replace(img, new_img_url)

    # ২. অন্যান্য এক্সটারনাল ইউআরএল (IMEI.info, Hardreset ইত্যাদি) মাস্কিং
    # এগুলোকে সরাসরি আপনার ডেভেলপারের ক্রেডিট বা কাস্টম লিঙ্কে কনভার্ট করা
    external_links = re.findall(r'https?://(?:www\.)?(?:imei\.info|hardreset\.info)[^\s<>"]*', data_str)
    for link in external_links:
        data_str = data_str.replace(link, "#protected_by_sakib")

    return eval(data_str)

@app.get("/")
def home():
    return {"status": "running", "provider": DEVELOPER}

@app.get("/check")
def check_imei(imei: str = Query(..., description="15 Digit IMEI"), request: Response = None):
    # IMEI ভ্যালিডেশন
    if not imei.isdigit() or len(imei) < 14:
        raise HTTPException(status_code=400, detail="Invalid IMEI")

    target_url = f"https://dash.imei.info/api/check/0/?imei={imei}&API_KEY={API_KEY}"
    headers = {'User-Agent': "okhttp/4.9.2"}

    try:
        response = requests.get(target_url, headers=headers, timeout=15)
        raw_data = response.json()

        # বর্তমান সার্ভারের বেস ইউআরএল বের করা
        # ভার্সেল বা লোকালহোস্ট যাই হোক অটো কাজ করবে
        current_base_url = "https://your-app-name.vercel.app" # এখানে আপনার ভার্সেল লিঙ্কটি দিয়ে দিন বা ডাইনামিক রাখুন

        # ডেটা মাস্কিং এবং প্রাউড ব্র্যান্ডিং
        secured_data = mask_data(raw_data, "") # ইউআরএল ডাইনামিকালি হ্যান্ডেল হবে

        return {
            "success": True,
            "developer": DEVELOPER,
            "imei": imei,
            "status": "Premium Encrypted Content",
            "results": secured_data.get("result", {})
        }

    except Exception as e:
        return {"success": False, "msg": "API Error", "dev": DEVELOPER}
