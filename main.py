from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI(
    title="SB-SAKIB Elite IMEI API",
    description="Secured Data-Only IMEI Lookup Service",
    version="4.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = "f43f0d0c-27b0-408a-abd0-585fabea6adf"
DEVELOPER = "SB-SAKIB"

def filter_premium_data(raw_data):
    """এটি ইমেজ এবং লিঙ্কগুলোকে পুরোপুরি রিমুভ করে শুধু তথ্যগুলো রাখবে"""
    if "result" not in raw_data:
        return {}

    original_items = raw_data.get("result", {}).get("items", [])
    header_info = raw_data.get("result", {}).get("header", {})
    
    clean_items = []
    
    for item in original_items:
        # শুধুমাত্র টেক্সট ডাটাগুলো নেওয়া হচ্ছে, বাটন বা লিঙ্ক বাদ দেওয়া হয়েছে
        if item.get("role") in ["header", "item"]:
            # কন্টেন্ট যদি কোনো লিঙ্ক বা ইমেইল হয় তবে সেটি বাদ দেওয়া হবে
            content = str(item.get("content", ""))
            if "http" not in content and "mailto" not in content:
                clean_items.append({
                    "title": item.get("title"),
                    "value": content if content != "None" else "N/A"
                })

    return {
        "brand": header_info.get("brand", "N/A"),
        "model": header_info.get("model", "N/A"),
        "specifications": clean_items
    }

@app.get("/")
def home():
    return {
        "status": "online", 
        "developer": DEVELOPER,
        "mode": "Ultra Secure (No Tracking)"
    }

@app.get("/check")
def check_imei(imei: str = Query(..., description="15 Digit IMEI")):
    # বেসিক ভ্যালিডেশন
    if not imei.isdigit() or len(imei) < 14:
        return {"success": False, "message": "Invalid IMEI Format", "dev": DEVELOPER}

    target_url = f"https://dash.imei.info/api/check/0/?imei={imei}&API_KEY={API_KEY}"
    
    headers = {
        'User-Agent': "okhttp/4.9.2",
        'Accept': "application/json"
    }

    try:
        response = requests.get(target_url, headers=headers, timeout=20)
        
        if response.status_code != 200:
            return {"success": False, "message": "Service Busy", "dev": DEVELOPER}
            
        raw_data = response.json()

        # ডেটা ফিল্টারিং (ইমেজ এবং ইউআরএল বাদ দেওয়া)
        final_details = filter_premium_data(raw_data)

        if not final_details:
            return {"success": False, "message": "No data found for this IMEI", "dev": DEVELOPER}

        # প্রিমিয়াম আউটপুট
        return {
            "success": True,
            "developer": DEVELOPER,
            "imei": imei,
            "device": {
                "brand": final_details["brand"],
                "model": final_details["model"]
            },
            "details": final_details["specifications"]
        }

    except Exception:
        return {
            "success": False, 
            "message": "Internal Server Error", 
            "dev": DEVELOPER
        }
