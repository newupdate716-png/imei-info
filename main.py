from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI(
    title="Premium IMEI Checker API",
    description="Professional API to check IMEI information with high speed.",
    version="1.0.0"
)

# CORS এনাবল করা হয়েছে যাতে অন্য ওয়েবসাইট থেকে আপনার API কল করা যায়
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = "f43f0d0c-27b0-408a-abd0-585fabea6adf"

@app.get("/")
def home():
    return {
        "status": "online",
        "message": "Welcome to Premium IMEI Checker API. Use /check?imei=YOUR_IMEI to use."
    }

@app.get("/check")
def check_imei(imei: str = Query(..., description="Enter the 15-digit IMEI number")):
    # IMEI ভ্যালিডেশন (বেসিক)
    if not imei.isdigit() or len(imei) < 14:
        raise HTTPException(status_code=400, detail="Invalid IMEI format. Must be numeric and valid length.")

    url = f"https://dash.imei.info/api/check/0/?imei={imei}&API_KEY={API_KEY}"
    
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        'Accept': "application/json"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        # প্রিমিয়াম আউটপুট স্ট্রাকচার
        return {
            "success": True,
            "developer": "SB-SAKIB",
            "imei": imei,
            "data": data
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Could not fetch data from provider."
        }