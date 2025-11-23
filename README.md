# Hybrid Edge-Cloud IoT Pipeline for OCR Analytics

A distributed IoT architecture simulating a smart camera system. It performs **Edge_Computing** (OCR & Audio Generation) to reduce bandwidth and utilizes a **Hybrid Database** strategy (SQL + NoSQL) 
for scalable data management.

---

## Project Overview

**The Problem:** In remote IoT environments (e.g., oil rigs, rural warehouses), bandwidth is expensive and unstable. Sending high-resolution video streams to the cloud for processing is an inefficient approach.

**The Solution:** A "Smart Edge" approach. The device processes images locally, extracts text, converts it to audio for accessibility, and transmits only the lightweight structured data (and binary blobs) to the cloud.

**Key Capabilities:**
* **Edge Intelligence:** Uses Tesseract OCR and offline Text-to-Speech (TTS) to process data without internet.
* **Hybrid Storage:** Uses **PostgreSQL** for strict device authentication (IAM) and **MongoDB GridFS** for storing unstructured logs and audio blobs.
* **Containerization:** Fully Dockerized backend for reproducible deployment.

---

## Architecture

**1. The Edge Node (Python Client)**
* Simulates a smart camera.
* **Pre-processing:** Image capture & cleaning.
* **Compute:** Runs `pytesseract` (OCR) and `pyttsx3` (Audio Synthesis) locally.
* **Network:** Uploads data via `multipart/form-data` POST request.

**2. The Cloud API (FastAPI)**
* **The Gatekeeper:** Validates `device_id` against PostgreSQL.
* **The Router:** Routes metadata to MongoDB and binary files to GridFS.

**3. The Data Layer (Docker)**
* **PostgreSQL:** Relational DB for strictly structured data (Device Registry).
* **MongoDB:** NoSQL Data Lake for flexible JSON logs and Binary Objects (BLOBs).

---

## Tech Stack

| Component | Technology | Role |
| :--- | :--- | :--- |
| **Language** | Python 3.9+ | Core logic for Edge and API |
| **Framework** | FastAPI | High-performance REST API |
| **Edge AI** | Tesseract v5 | Optical Character Recognition (OCR) |
| **Audio** | pyttsx3 | Offline Text-to-Speech engine |
| **Databases** | PostgreSQL, MongoDB | Polyglot Persistence |
| **DevOps** | Docker, Docker Compose | Container orchestration |

---

## Getting Started

### Prerequisites
* Docker Desktop installed & running.
* Python 3.x installed.
* **Tesseract Engine** installed on your OS:
    * *Mac:* `brew install tesseract`
    * *Windows:* [Download Installer](https://github.com/UB-Mannheim/tesseract/wiki) (Add to PATH)
    * *Linux:* 'sudo apt install tesseract-ocr'
