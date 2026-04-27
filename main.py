from fastapi import FastAPI, Query, HTTPException, Response, Request
from fastapi.middleware.cors import CORSMiddleware
import requests
import json

app = FastAPI(
    title="SB-SAKIB Elite IMEI API",
    description="Professional Secure IMEI Lookup Service",
    version="3.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = "f43f0d0c-27b0-408a-abd0-585fabea6adf"
DEVELOPER = "SB-SAKIB"

# প্রক্সি ইমেজ ফাংশন - এটি অরিজিনাল সোর্স হাইড করবে
@app.get("/proxy/image")
def proxy_image(url: str):
    try:
        res = requests.get(url, stream=True, timeout=15)
        res.raise_for_status()
        return Response(content=res.content, media_type=res.headers.get("Content-Type"))
    except:
        # যদি ইমেজ লোড না হয় তবে একটি ডিফল্ট এরর ইমেজ বা ৪০০ এরর দিবে
        raise HTTPException(status_code=404, detail="Image not available")

def clean_and_mask(data, base_url):
    """এটি ডেটা ক্লিন করবে এবং অরিজিনাল লিঙ্ক হাইড করবে"""
    json_str = json.dumps(data)
    
    # ১. ইমেজ ইউআরএল গুলোকে আপনার প্রক্সি ইউআরএল দিয়ে পরিবর্তন
    # imei.info এর ইমেজ লিঙ্ক সাধারণত imei.info/media/ তে থাকে
    if "imei.info" in json_str:
        # ইমেজ প্রক্সি লিঙ্ক তৈরি
        proxy_prefix = f"{base_url}/proxy/image?url="
        json_str = json_str.replace("https://www.imei.info/media/", f"{proxy_prefix}https://www.imei.info/media/")
        
        # ২. অরিজিনাল লিঙ্কগুলো হাইড করা
        json_str = json_str.replace("https://www.imei.info", "#protected_by_sakib")
        json_str = json_str.replace("https://www.hardreset.info", "#protected_by_sakib")
        json_str = json_str.replace("mailto:info@imei.info", "#protected_by_sakib")

    return json.loads(json_str)

@app.get("/")
def home():
    return {
        "status": "online", 
        "developer": DEVELOPER,
        "endpoint": "/check?imei=YOUR_IMEI"
    }

@app.get("/check")
def check_imei(request: Request, imei: str = Query(..., description="15 Digit IMEI")):
    # বেসিক ভ্যালিডেশন
    if not imei.isdigit() or len(imei) < 14:
        return {"success": False, "message": "Invalid IMEI Format", "dev": DEVELOPER}

    # আপনার প্রোভাইডার এপিআই ইউআরএল
    target_url = f"https://dash.imei.info/api/check/0/?imei={imei}&API_KEY={API_KEY}"
    
    headers = {
        'User-Agent': "okhttp/4.9.2",
        'Accept': "application/json"
    }

    try:
        response = requests.get(target_url, headers=headers, timeout=20)
        
        if response.status_code != 200:
            return {"success": False, "message": "Provider API Error", "status_code": response.status_code}
            
        raw_data = response.json()

        # ডাইনামিক বেস ইউআরএল বের করা (লোকাল বা ভার্সেল অটো কাজ করবে)
        base_url = str(request.base_url).rstrip('/')

        # ডেটা মাস্কিং এবং সিকিউরিটি অ্যাপ্লাই
        final_result = clean_and_mask(raw_data, base_url)

        # প্রিমিয়াম রেসপন্স ফরম্যাট
        return {
            "success": True,
            "developer": DEVELOPER,
            "imei": imei,
            "brand": final_result.get("result", {}).get("header", {}).get("brand", "N/A"),
            "model": final_result.get("result", {}).get("header", {}).get("model", "N/A"),
            "full_details": final_result.get("result", {})
        }

    except Exception as e:
        return {
            "success": False, 
            "error": "System Error", 
            "details": str(e),
            "dev": DEVELOPER
        }
