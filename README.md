# Assistive Communication System for ALS Patients (GEMMA4)

This repository contains the codebase for an assistive communication system designed for ALS patients, powered by **GEMMA4**.

---

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
  
## 📌 Notes

- Ensure the GEMMA service VM is running before starting the server
- WebSocket connections must be properly configured across all services
- Gaze tracking module requires camera access and proper calibration
