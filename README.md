# Real-Time Video Anomaly Detection & Surveillance System

A full-stack intelligent surveillance platform for real-time anomaly detection, camera monitoring, and incident response. The project combines AI-powered video analysis, a Flask backend, and a modern React dashboard to detect suspicious events such as falls, fights, fires, smoke, crowding, and unauthorized objects, then report them instantly for monitoring and review.

## Overview

This repository contains two major parts:

- `system/` — the AI detection engine built in Python for live video processing, anomaly detection, FPS tracking, alert generation, and dashboard reporting.
- `Qau_Sentinel/QAU_SENTINEL/` — the complete monitoring application with a Flask API, WebSocket services, SQLite database, and a React-based frontend dashboard.

Together, they form a real-time surveillance ecosystem for smart security monitoring, incident logging, analytics, and rapid operator response.

## Key Features

- Real-time video anomaly detection from webcam or video streams
- Multi-model AI detection using YOLO object detection, YOLO-Pose, and OpenVINO fire/smoke detection
- Incident generation for falls, fights, running, crowding, smoke, fire, and banned object detection
- Live alert overlays and screenshot capture for detected anomalies
- Flask backend with REST APIs and real-time Socket.IO updates
- Role-based authentication and user management
- Camera management and live stream monitoring
- Incident analytics, dashboard insights, and report generation
- Modern web interface for operators and admins

## Architecture

```text
Camera / Video Source
        |
        v
AI Detection Pipeline (system/)
  - YOLO-Pose: fight / fall / running
  - YOLO-Object: crowd / banned objects
  - Fire/Smoke OpenVINO: fire and smoke detection
  - MegaAlertManager: anomaly alerts and screenshots
        |
        v
Flask Backend (Qau_Sentinel/QAU_SENTINEL/backend)
  - Authentication
  - Camera and user management
  - Incident storage and analytics
  - Socket.IO live events
        |
        v
React Dashboard (Qau_Sentinel/QAU_SENTINEL/src)
  - Live monitoring
  - Incident review
  - Camera controls
  - Analytics and reports
```

## Repository Structure

```text
Real_Time_Video_Anomaly_Detection/
├── README.md
├── system/
│   ├── master_mega_dashboard.py
│   ├── master_detection_functions_modified.py
│   ├── master_mega_alerts.py
│   ├── motion_heuristics_Fall_modified.py
│   ├── dashboard_client.py
│   ├── requirements.txt
│   ├── README.md
│   └── ...
├── Qau_Sentinel/
│   └── QAU_SENTINEL/
│       ├── backend/
│       ├── src/
│       ├── public/
│       ├── package.json
│       ├── vite.config.js
│       ├── README.md
│       └── ...
├── TODO.md
├── analyze_and_fix.py
├── do_fix.py
├── final_fix.py
├── fix_card.py
├── write_card.py
├── write_card2.py
└── ...
```

## Technology Stack

### AI / Detection Layer
- Python
- OpenCV
- OpenVINO
- Ultralytics YOLO
- NumPy

### Backend
- Flask
- Flask-SocketIO
- SQLAlchemy
- SQLite
- JWT authentication

### Frontend
- React
- Vite
- JavaScript / JSX
- Tailwind CSS
- Recharts and UI components

## Getting Started

### 1. AI Detection System

Navigate to the `system/` folder and install dependencies:

```bash
cd system
python -m venv .venv
# Windows
.venv\Scripts\Activate.ps1
# Linux/macOS
source .venv/bin/activate
pip install -r requirements.txt
```

Run the detection pipeline:

```bash
python master_mega_dashboard.py --source 0
```

For full stream and dashboard integration, see the setup guide in [system/README.md](system/README.md).

### 2. Web Application

Open the frontend and backend project:

```bash
cd Qau_Sentinel/QAU_SENTINEL/backend
python -m venv .venv
# Windows
.venv\Scripts\Activate.ps1
# Linux/macOS
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Then run the frontend:

```bash
cd ../
npm install
npm run dev
```

The dashboard should be available in the browser, and the backend will serve API and Socket.IO endpoints for live monitoring.

## Main Use Cases

- Campus or building security monitoring
- Real-time detection of dangerous or abnormal activity
- Automatic incident logging for safety and compliance
- Centralized dashboard for visual surveillance operators
- AI-assisted event detection in smart environments

## Important Notes

- The project is designed as a live monitoring and detection system, so real-world performance depends on hardware, camera quality, and model configuration.
- For production deployment, ensure secure credentials, proper environment configuration, and controlled access to camera feeds and APIs.
- The AI detection pipeline and the web application are intentionally separated so they can be managed and scaled independently.

## Documentation

- [system/README.md](system/README.md)
- [Qau_Sentinel/QAU_SENTINEL/README.md](Qau_Sentinel/QAU_SENTINEL/README.md)

## License

This project is intended for academic, research, and demo use. Please check the project documentation and institutional requirements before public or commercial deployment.

## Project Goal

This project demonstrates how AI-driven computer vision can be integrated with a real-time dashboard to build an intelligent surveillance system capable of identifying suspicious activity, improving situational awareness, and supporting faster incident response.
