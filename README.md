# Assistive Communication System for ALS Patients (GEMMA4)

This repository contains the codebase for an assistive communication system designed for ALS patients, powered by **GEMMA4**.

---

## 🏗️ Repository Structure

### 1. Server (Flask Manager)
- **Location:** `src/server.py`
- Acts as the central manager of the system
- Handles communication between frontend and backend services
- Coordinates data flow across all modules

---

### 2. Frontend
- Connected directly to the Flask server
- Provides the user interface for interaction
- Sends user inputs and receives processed outputs

---

### 3. Gaze Tracking Module
- **Location:** `src/new_detect.py`
- Tracks user eye movements
- Converts gaze data into actionable input signals

---

### 4. GEMMA Service (VM Hosted)
- **Location:** `src/gemma_service`
- Hosted on a separate virtual machine
- Runs GEMMA4 for AI-driven processing
- Generates communication outputs based on inputs

---

## 🔌 Communication Protocol

- Uses **WebSockets** for real-time, bidirectional communication
- Enables low-latency interaction between:
  - Frontend
  - Flask Server
  - Gaze Tracking Module
  - GEMMA Service

---

## 🔄 System Workflow

1. User interacts via the **Frontend**
2. Input is sent to the **Flask Server**
3. Server communicates with:
   - **Gaze Tracking Module** (for input interpretation)
   - **GEMMA Service** (for AI processing)
4. Processed output is sent back to the **Frontend**
5. Results are displayed to the user

---

## 🚀 Key Features

- Real-time assistive communication
- Eye-gaze-based input system
- AI-powered response generation (GEMMA4)
- Modular architecture with scalable services
- WebSocket-based low-latency communication

---

## 📌 Notes

- Ensure the GEMMA service VM is running before starting the server
- WebSocket connections must be properly configured across all services
- Gaze tracking module requires camera access and proper calibration

---


