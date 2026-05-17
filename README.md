# Assistive Communication System for ALS Patients (GEMMA4)
This repository contains the codebase for an assistive communication system designed for ALS patients, powered by **GEMMA4**.
<img width="957" height="462" alt="Application Home Screen" src="https://github.com/user-attachments/assets/4c534190-1029-43dc-99a1-21096f6a00f6" />
<img width="959" height="458" alt="Medical Intent Screen" src="https://github.com/user-attachments/assets/ad5c332a-ddfb-49c9-b90e-b42313d7b8ef" />

## 🏗️ Repository Structure

### 1. Server (Flask Manager)
- **Location:** `src/server.py`
### 2. Gaze Tracking Module
- **Location:** `src/new_detect.py`
- Tracks user eye movements
- Converts gaze data into actionable input signals
### 3. GEMMA Service (VM Hosted)
- **Location:** `src/gemma_service`
- Hosted on a separate virtual machine
- Runs GEMMA4 for AI-driven processing

---
# 🚀 PRESENCE: Multi-modal AI System for ALS Assistive Care

## 🖥️ Local Machine Setup

### 1. Clone the Repository
```bash
git clone https://github.com/chandanreddy10/presence-als-assist
cd presence-als-assist
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Navigate to Source Directory
```bash
cd src
```

### 4. Run Services (Open Two Terminals)

**Terminal 1**
```bash
python server.py
```

**Terminal 2**
```bash
python new_detect.py
```

---

## ☁️ Remote Machine (Server / VM Setup)

### 1. Clone the Repository
```bash
git clone https://github.com/chandanreddy10/presence-als-assist
cd presence-als-assist
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Navigate to Source Directory
```bash
cd src
```

### 4. Run Services (Open Two Terminals)

**Terminal 1 – Gemma Service**
```bash
uvicorn gemma_service:app --host 0.0.0.0 --port 8001
```

**Terminal 2 – Main Server**
```bash
uvicorn gemma_server:app --host 0.0.0.0 --port 8000
```

---

## 🔧 Configuration

Edit the file:

```bash
src/ws.py
```

Update the WebSocket URL:

```python
VM_WS_URL = "ws://<REMOTE_MACHINE_IP>:8000"
```

Replace `<REMOTE_MACHINE_IP>` with your remote server/VM IP address.

---

## ✅ Notes

- Ensure ports **8000** and **8001** are open  
- Both machines must be network-accessible  
- Using a virtual environment is recommended
- Ensure the GEMMA service VM is running before starting the server
- WebSocket connections must be properly configured across all services
- Gaze tracking module requires camera access and proper calibration
