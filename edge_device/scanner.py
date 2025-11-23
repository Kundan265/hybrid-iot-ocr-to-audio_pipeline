import pytesseract
from PIL import Image
import datetime
import json
import requests
import os
import pyttsx3
import re

API_URL = "http://127.0.0.1:8000/upload_data"

def text_to_tokens(raw_text):
    """Clean text for audio generation"""
    # Remove special chars, keep alphanumeric + punctuation
    clean_text = re.sub(r'[^a-zA-Z0-9\s.,!?]', '', raw_text)
    clean_text = clean_text.replace('\n', ' ')
    return clean_text

def generate_audio_file(text, timestamp_str):
    """
    Saves the text as a .wav file on the disk.
    """
    filename = f"audio_{timestamp_str}.wav"
    print(f"--- [AUDIO GEN] Saving audio to {filename}... ---")
    
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 150) # Speed
        engine.save_to_file(text, filename)
        engine.runAndWait()
        print("Audio file saved successfully.")
        return filename
    except Exception as e:
        print(f"Audio Error: {e}")
        return None

def run_scanner(image_path):
    print(f"--- 1. [SENSOR] Processing {image_path} ---")
    
    if not os.path.exists(image_path):
        print(f"Error: File {image_path} not found.")
        return

    try:
        # --- A. Edge Compute (OCR) ---
        # THIS IS THE PART THAT WAS MISSING
        img = Image.open(image_path)
        extracted_text = pytesseract.image_to_string(img)
        # -----------------------------

        # B. Clean Data
        clean_audio_text = text_to_tokens(extracted_text)
        
        # C. Generate Audio File (Store)
        safe_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        audio_filename = None
        if clean_audio_text.strip():
            audio_filename = generate_audio_file(clean_audio_text, safe_time)
        else:
            print("No text to convert to audio.")

        # D. PREPARE PAYLOAD (Multipart Upload)
        # 1. Text Data (Form Fields)
        data_payload = {
            "device_id": "device_01", 
            "timestamp": datetime.datetime.now().isoformat(),
            "raw_text": extracted_text.strip(),
            "image_name": image_path
        }

        # 2. Binary Data (The File)
        files_payload = {}
        if audio_filename and os.path.exists(audio_filename):
            # We open the file in 'rb' (Read Binary) mode
            files_payload = {
                'audio_file': (audio_filename, open(audio_filename, 'rb'), 'audio/wav')
            }

        print(f"--- 2. [NETWORKING] Uploading Text + Audio Blob... ---")
        
        # NOTE: We use data=... NOT json=... when sending files
        response = requests.post(API_URL, data=data_payload, files=files_payload)
        
        if response.status_code == 200:
            print("[SUCCESS] Cloud Response:", response.json())
        else:
            print(f"[ERROR] Server returned: {response.status_code}")
            print(response.text)

    except requests.exceptions.ConnectionError:
        print("[NETWORK ERROR] Could not connect to Cloud API. Is uvicorn running?")
    except Exception as e:
        print(f"Critical Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Make sure this matches your actual image name!
    run_scanner("sample_img.png")