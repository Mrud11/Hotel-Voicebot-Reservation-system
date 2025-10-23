import os
import tempfile
import numpy as np
import requests
import pandas as pd
from dotenv import load_dotenv
from gtts import gTTS
import whisper
import sounddevice as sd
import wavio

load_dotenv()

SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")

BOOKINGS_FILE = "bookings.xlsx"
whisper_model = whisper.load_model("small")

def record_and_transcribe(duration=5):
    fs = 16000
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype="float32")
    sd.wait()
    audio_np = np.squeeze(recording)

    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "audio.wav")
        wavio.write(path, audio_np, fs, sampwidth=2)
        result = whisper_model.transcribe(path)

    return result["text"].strip()

def text_to_speech_bytes(text):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tmp_path = tmp.name
    tmp.close()
    try:
        tts = gTTS(text=text, lang="en", slow=False)
        tts.save(tmp_path)
        audio_bytes = open(tmp_path, "rb").read()
    finally:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except:
                pass
    return audio_bytes

def search_hotels(city, check_in, check_out, adults=2):
    params = {
        "engine": "google_hotels",
        "q": city,
        "gl": "in",
        "hl": "en",
        "check_in_date": check_in,
        "check_out_date": check_out,
        "adults": adults,
        "api_key": SERPAPI_API_KEY,
        "currency": "INR",
    }
    response = requests.get("https://serpapi.com/search", params=params)
    if response.status_code != 200:
        print(f"SerpApi error: {response.text}")
        return []
    try:
        hotels = response.json().get("properties", [])
        filtered = []
        for h in hotels:
            if ("hotel" in h.get("type", "").lower() and
                h.get("rate_per_night") and
                h["rate_per_night"].get("extracted_lowest")):
                filtered.append(h)
        return filtered
    except Exception as e:
        print(f"JSON parsing error: {e}")
        return []

def prepare_comparison(hotels):
    data = []
    for h in hotels:
        try:
            base_price = float(h.get("rate_per_night", {}).get("extracted_lowest", 0))
            if base_price <= 0:
                continue
        except (ValueError, TypeError):
            continue
        rating = h.get("overall_rating") or 0
        name = h.get("name", "Unknown")
        address = h.get("address", "No address")
        prices = {
            "Booking.com": round(base_price, 2),
            "Agoda": round(base_price * 1.05, 2),
            "MakeMyTrip": round(base_price * 0.98, 2),
            "Trivago": round(base_price * 1.02, 2),
        }
        min_price = min(prices.values())
        data.append({
            "Name": name,
            "Address": address,
            "Rating": rating,
            "Min Price (₹)": min_price,
            **prices
        })
    df = pd.DataFrame(data)
    if df.empty or "Min Price (₹)" not in df.columns or "Rating" not in df.columns:
        return pd.DataFrame()
    return df.sort_values(by=["Min Price (₹)", "Rating"], ascending=[True, False]).head(10)

def ask_llm(question):
    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "sonar",  # Explicitly specify model here
        "messages": [
            {"role": "system", "content": "You are a helpful hotel booking assistant."},
            {"role": "user", "content": question},
        ],
        "max_tokens": 800,
        "temperature": 0.5,
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        try:
            data = response.json()
            choices = data.get("choices", [])
            if choices:
                message = choices[0].get("message", {})
                return message.get("content", "No answer available.")
            return "No answer available."
        except Exception as e:
            return f"LLM response parse error: {e}"
    else:
        return f"LLM API error: {response.status_code} - {response.text}"

def save_booking(details):
    df = pd.DataFrame([details])
    if os.path.exists(BOOKINGS_FILE):
        old = pd.read_excel(BOOKINGS_FILE)
        df = pd.concat([old, df], ignore_index=True)
    df.to_excel(BOOKINGS_FILE, index=False)

def generate_receipt(details):
    receipt_text = f"""
HOTEL BOOKING RECEIPT
--------------------------
Name: {details['Name']}
Hotel: {details['Hotel']}
Address: {details['Address']}
Check-in: {details['Check-in']}
Check-out: {details['Check-out']}
Price: ₹{details['Price']}
Rating: {details['Rating']}
Booking Date: {details['Booking Date']}
--------------------------
Thank you for booking!
"""
    path = "receipt.txt"
    with open(path, "w", encoding="utf-8") as f:
        f.write(receipt_text)
    return path
