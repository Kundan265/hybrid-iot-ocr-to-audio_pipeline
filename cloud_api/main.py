from fastapi import FastAPI, HTTPException, UploadFile, File, Form
import psycopg2
from pymongo import MongoClient
import gridfs  # <--- NEW: The Blob Storage System
import datetime

app = FastAPI()

# --- DATABASE CONNECTIONS ---
# Postgres (Auth)
pg_conn = psycopg2.connect(
    host="127.0.0.1", port="5432",
    database="iot_auth", user="admin", password="********"
)

# Mongo (Data + Files)
mongo_client = MongoClient("mongodb://localhost:27017/")
mongo_db = mongo_client["iot_data_lake"]
mongo_collection = mongo_db["ocr_logs"]

# Initialize GridFS (The "Bucket" for files)
fs = gridfs.GridFS(mongo_db)

@app.post("/upload_data")
async def receive_data(
    device_id: str = Form(...),
    timestamp: str = Form(...),
    raw_text: str = Form(...),
    image_name: str = Form(...),
    audio_file: UploadFile = File(None) 
):
    print(f"\n[Incoming Blob Request] From {device_id}")

    # 1. CHECK AUTH (Postgres)
    cur = pg_conn.cursor()
    cur.execute("SELECT is_active FROM devices WHERE device_id = %s", (device_id,))
    device = cur.fetchone()
    cur.close()

    if not device or not device[0]:
        raise HTTPException(status_code=403, detail="Device Unauthorized")

    # 2. STORE AUDIO BLOB (GridFS)
    audio_id = None
    if audio_file:
        print(f"--- Storing Audio Blob: {audio_file.filename} ---")
        # Read the binary file and save to Mongo GridFS
        file_content = await audio_file.read()
        audio_id = fs.put(file_content, filename=audio_file.filename)
        print(f"Blob stored in GridFS with ID: {audio_id}")

    # 3. STORE METADATA (MongoDB Standard)
    data_dict = {
        "device_id": device_id,
        "timestamp": timestamp,
        "raw_text": raw_text,
        "image_name": image_name,
        "received_at": datetime.datetime.now().isoformat(),
        "audio_blob_id": str(audio_id) if audio_id else None  # Link to the file
    }
    
    result = mongo_collection.insert_one(data_dict)
    
    return {"status": "success", "mongo_id": str(result.inserted_id), "blob_id": str(audio_id)}

@app.get("/view_logs")
def get_logs():
    # Get last 10 logs, newest first
    cursor = mongo_collection.find().sort("received_at", -1).limit(10)
    
    logs = []
    for document in cursor:
        # Fix: Convert MongoDB's weird "ObjectId" to a normal string
        document["_id"] = str(document["_id"])
        logs.append(document)
        
    return logs    
