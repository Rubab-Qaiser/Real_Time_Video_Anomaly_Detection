<div align="center">

# 🛡️ QAU Sentinel

**Real-time AI-Powered Video Surveillance & Incident Management System**

A production-style security monitoring platform that fuses an **AI detection engine** (YOLO-Pose, YOLO-Object, and a specialized Fire/Smoke OpenVINO model) with a modern **React dashboard** and **Flask backend** — delivering live camera feeds, real-time alerts, incident tracking, and analytics in one place.

</div>

---

## 📖 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Detection Types](#detection-types)
- [Tech Stack](#tech-stack)
- [Repository Structure](#repository-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [1. Backend](#1-backend)
  - [2. Frontend](#2-frontend)
  - [3. Seed Data](#3-seed-data)
  - [4. Detection Pipeline (optional)](#4-detection-pipeline-optional)
- [Environment Configuration](#environment-configuration)
- [REST API Reference](#rest-api-reference)
- [Real-Time Events (Socket.IO)](#real-time-events-socketio)
- [Frontend Pages & Routes](#frontend-pages--routes)
- [Scripts](#scripts)
- [Security Notes](#security-notes)
- [License](#license)

---

## Overview

**QAU Sentinel** is a complete campus-security monitoring solution. It combines:

- A **real-time Python detection pipeline** (`../system/`) that analyzes camera feeds using multiple YOLO-based models to detect **fires, smoke, crowds, falls, running, fights, and unwanted objects**.
- A **Flask REST + Socket.IO backend** that stores incidents, cameras, and users, authenticates access with JWT tokens, streams live MJPEG video, and serves alert snapshots.
- A **React (Vite) single-page application** that provides a dark, glassmorphism dashboard for operators and administrators to monitor everything in real time.

The detection pipeline pushes live incidents and status updates to the backend, which relays them to the frontend over WebSockets — so a fall, fire, or fight appears on the dashboard within seconds of being detected.

---

## Key Features

- 🔥 **Multi-class anomaly detection** — Fire, Smoke, Crowd, Fall, Running, Fight, and Unwanted Objects.
- 🎥 **Live camera streaming** — MJPEG streams with token-based auth embedded in the URL.
- ⚡ **Real-time updates** — Socket.IO pushes new incidents, camera status, detections, and logs instantly.
- 🛡️ **Role-based access control** — `Admin`, `Operator`, and `Viewer` roles gate pages and API actions.
- 📊 **Rich analytics** — Incident trends, detection distribution, camera performance, dashboards, and CSV/PDF report export.
- 📋 **Incident management** — Full CRUD with search, filtering, severity, status, and pagination.
- 🗂️ **Camera management** — Add, edit, delete, and live-monitor camera feeds.
- 👥 **User management** — Admin-only user CRUD with role assignment.
- 📝 **System logs** — A live, filterable log view derived from incident activity.
- 🚨 **Alert snapshots** — Automatically captured and served images for every detected incident.

---

## Architecture

```
                      ┌───────────────────────────────────────────────┐
                      │              Python Pipeline (system/)        │
                      │                                               │
  Camera ───────────► │  YOLO-Pose      → fall / running / fight      │
  (webcam / video)    │  YOLO-Object    → crowd + banned objects      │
                      │  Fire/Smoke OV  → fire / smoke (bg thread)    │
                      │  MegaAlertManager → alerts + screenshots      │
                      │  DashboardClient  → POST incidents/status     │
                      └────────────────────┬──────────────────────────┘
                                           │  REST / JSON
                                           ▼
                      ┌───────────────────────────────────────────────┐
                      │            Flask Backend (backend/)           │
                      │  REST API  •  JWT Auth  •  SQLite  •  Socket.IO│
                      └────────────────────┬──────────────────────────┘
                                           │  REST + WebSockets
                                           ▼
                      ┌───────────────────────────────────────────────┐
                      │            React Frontend (src/)              │
                      │  Dashboard  •  Cameras  •  Incidents  •  ...  │
                      └───────────────────────────────────────────────┘
```

---

## Detection Types

| Detection Type | Severity | Pipeline Source |
|----------------|----------|-----------------|
| 🔥 Fire | critical | Fire/Smoke OpenVINO model |
| 💨 Smoke | high | Fire/Smoke OpenVINO model |
| 👥 Crowd | medium | YOLO-Object / Haar Cascade head count |
| 🚶 Fall | critical | YOLO-Pose motion heuristics |
| 🏃 Running | high | YOLO-Pose motion heuristics |
| ⚔️ Fight | critical | YOLO-Pose pairwise heuristics |
| 📦 Unwanted Object | high | YOLO-Object banned-class detection |

---

## Tech Stack

**Frontend** (`src/`)
- React 19, React Router 7, Vite 7
- Tailwind CSS 4, Radix UI, Framer Motion, Recharts
- Socket.IO Client, Axios, JWT Decode, React Hook Form, Zod

**Backend** (`backend/`)
- Python 3, Flask 3.1, Flask-CORS, Flask-Login
- Flask-SocketIO (real-time)
- SQLAlchemy 2.0 + SQLite
- PyJWT (access/refresh tokens), OpenCV, Ultralytics

**Detection Pipeline** (`system/`)
- Python 3, OpenCV, NumPy
- Ultralytics YOLO (Pose + Object), OpenVINO runtime
- Flask (MJPEG streaming micro-server), Requests

---

## Repository Structure

```
QAU_SENTINEL/
├── backend/                  # Flask REST + Socket.IO API
│   ├── api/                  # Blueprints: auth, cameras, incidents, detections, analytics, logs, users, health
│   ├── database/             # SQLAlchemy setup + SQLite DB
│   ├── models/               # User, Camera, Incident, RefreshToken
│   ├── services/             # Business logic (camera, incident, analytics, user, stream, yolo)
│   ├── middleware/           # Auth decorators (admin/operator/viewer)
│   ├── utils/                # JWT utilities, detection utils
│   ├── app.py                # App factory, CORS, Socket.IO init
│   ├── config.py             # Configuration (reads env vars)
│   ├── seed_*.py             # Database seed scripts
│   └── requirements.txt
├── src/                      # React frontend
│   ├── api/                  # Axios instance
│   ├── components/           # UI components (cards, charts, cameras, incidents, layouts)
│   ├── config/               # Detection type configuration
│   ├── contexts/             # AuthContext, SocketContext
│   ├── hooks/                # Data-fetching + socket hooks
│   ├── layouts/              # DashboardLayout, AuthLayout
│   ├── pages/                # Dashboard, Cameras, Incidents, Analytics, Logs, Users, Settings, Login
│   ├── routes/               # AppRoutes (routing + guards)
│   ├── services/             # API service modules
│   ├── utils/                # Helpers (token, constants, download)
│   ├── App.jsx
│   └── main.jsx
├── public/                   # Static assets
├── index.html
├── package.json
├── vite.config.js
└── .env.example              # Environment template (safe to commit)
```

> The companion AI detection pipeline lives in the sibling `system/` directory.

---

## Getting Started

### Prerequisites

- **Node.js** 18+ and npm (for the frontend)
- **Python** 3.9+ (for the backend and pipeline)
- A webcam or video file for testing the detection pipeline

### 1. Backend

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt

# Copy the env template and edit if needed
copy .env.example .env        # Windows
# cp .env.example .env        # macOS / Linux

python app.py
```

The backend starts at `http://localhost:5000`. Verify with:

```bash
curl http://localhost:5000/api/health
# {"status":"healthy","message":"AI Surveillance Backend is running","version":"1.0.0"}
```

### 2. Frontend

```bash
npm install
npm run dev
```

The frontend opens at `http://localhost:5173`.

> The frontend reads `VITE_API_BASE_URL` from `.env` to locate the backend. By default it assumes `http://localhost:5000`.

### 3. Seed Data

From the `backend/` directory, populate the database with demo users, cameras, and incidents:

```bash
python seed_users.py          # admin / operator1 / viewer1
python seed_cameras.py        # 4 sample cameras
python seed_new_incidents.py  # sample incidents of all types
# or run everything at once:
python seed_all.py
```

**Default demo accounts** (from `seed_users.py`):

| Role | Email | Password |
|------|-------|----------|
| Viewer | `viewer1@qau.edu.pk` | `viewer123` |

> ⚠️ **Change these default credentials before any real deployment.**

### 4. Detection Pipeline (optional)

The live detection pipeline is a separate Python process in the sibling `system/` directory. It analyzes a camera feed and reports incidents/status to this backend. See [`system/README.md`](../system/README.md) for full setup.

Minimal run:

```bash
cd ../system
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux
pip install -r requirements.txt

# Configure dashboard credentials (see system/README.md)
copy .env.example .env        # fill in DASHBOARD_EMAIL / DASHBOARD_PASSWORD

python master_mega_dashboard.py --source 0 \
    --enable-dashboard --dashboard-ip 127.0.0.1 --dashboard-port 5000 \
    --camera-id 1 --camera-location "Main Entrance"
```

---

## Environment Configuration

Both the frontend and backend read configuration from `.env` files (git-ignored). Templates are provided as `.env.example`.

### Backend `.env` (in `backend/`)

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | `dev-secret-key` | Flask secret key |
| `JWT_SECRET_KEY` | `dev-jwt-secret-key-32-chars-long!!` | JWT signing key |
| `DATABASE_URL` | `sqlite:///.../ai_surveillance.db` | SQLAlchemy connection string |
| `FLASK_DEBUG` | `False` | Enable debug mode (`"true"`) |
| `FLASK_HOST` | `127.0.0.1` | Bind host |
| `FLASK_PORT` | `5000` | Bind port |
| `CORS_ORIGINS` | `http://localhost:5173,...` | Comma-separated allowed origins |
| `YOLO_MODEL` | `yolov8n.pt` | YOLO model path |
| `CAMERA_SOURCE` | `0` | Default camera source |

### Frontend `.env` (in project root)

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_BASE_URL` | *(unset)* | Backend base URL, e.g. `http://localhost:5000` |
| `VITE_APP_NAME` | `QAU Sentinel` | App display name |
| `VITE_APP_VERSION` | `1.0.0` | App version |

### Pipeline `.env` (in `system/`)

| Variable | Default | Description |
|----------|---------|-------------|
| `DASHBOARD_IP` | `127.0.0.1` | Backend host |
| `DASHBOARD_PORT` | `5000` | Backend port |
| `DASHBOARD_EMAIL` | *(required)* | Login email for reporting incidents |
| `DASHBOARD_PASSWORD` | *(required)* | Login password for reporting incidents |

---

## REST API Reference

All endpoints are prefixed with `/api`. Protected endpoints require a `Authorization: Bearer <access_token>` header.

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| `GET` | `/api/health` | Public | Health check |
| `POST` | `/api/auth/login` | Public | Login, returns access + refresh tokens |
| `POST` | `/api/auth/refresh` | Public | Refresh access token |
| `POST` | `/api/auth/logout` | Public | Revoke refresh token |
| `GET` | `/api/auth/me` | Any authenticated | Current user profile |
| `GET` | `/api/cameras/` | Viewer+ | List cameras (search/filter) |
| `GET` | `/api/cameras/<id>` | Viewer+ | Get a camera |
| `POST` | `/api/cameras/` | Operator+ | Create a camera |
| `PUT` | `/api/cameras/<id>` | Operator+ | Update a camera |
| `DELETE` | `/api/cameras/<id>` | Admin | Delete a camera |
| `GET` | `/api/cameras/<id>/live` | Token | Live MJPEG stream |
| `GET` | `/api/incidents/` | Viewer+ | List incidents (filter/paginate) |
| `GET` | `/api/incidents/<id>` | Viewer+ | Get an incident |
| `POST` | `/api/incidents/` | Operator+ | Create an incident |
| `PUT` | `/api/incidents/<id>` | Operator+ | Update an incident |
| `DELETE` | `/api/incidents/<id>` | Operator+ | Delete an incident |
| `GET` | `/api/detections/` | Public | Latest detections (from pipeline cache) |
| `GET` | `/api/detections/latest` | Public | Latest detection summary |
| `POST` | `/api/detections/status` | Public | Push live status from pipeline |
| `GET` | `/api/analytics/dashboard` | Viewer+ | Dashboard stats |
| `GET` | `/api/analytics/distribution` | Viewer+ | Detection distribution |
| `GET` | `/api/analytics/trends` | Viewer+ | Incident trends |
| `GET` | `/api/analytics/camera-performance` | Viewer+ | Camera performance |
| `GET` | `/api/analytics/reports` | Viewer+ | Recent reports |
| `GET` | `/api/analytics/overview` | Viewer+ | Combined analytics |
| `GET` | `/api/analytics/export/csv` | Viewer+ | Export incidents as CSV |
| `GET` | `/api/analytics/export/pdf` | Viewer+ | Export incidents as report |
| `GET` | `/api/logs/` | Viewer+ | Live system logs |
| `GET` | `/api/users/` | Admin | List users |
| `GET` | `/api/users/<id>` | Admin | Get a user |
| `POST` | `/api/users/` | Admin | Create a user |
| `PUT` | `/api/users/<id>` | Admin | Update a user |
| `DELETE` | `/api/users/<id>` | Admin | Delete a user |
| `GET` | `/api/alerts/<filename>` | Public | Serve captured alert snapshots |

---

## Real-Time Events (Socket.IO)

The backend broadcasts the following events over WebSockets:

| Event | Payload | Description |
|-------|---------|-------------|
| `connected` | `{ message }` | Sent on client connect |
| `camera_status` | `{ camera_id, status, camera, timestamp }` | Camera online/offline changes |
| `new_detection` | `{ detection, timestamp }` | New AI detection |
| `new_incident` | `{ incident, timestamp }` | New incident created |
| `incident_update` | `{ incident_id, status, incident, timestamp }` | Incident status changed |
| `new_log` | `{ log, timestamp }` | New system log entry |
| `camera_deleted` | `{ camera_id, timestamp }` | A camera was removed |

---

## Frontend Pages & Routes

| Route | Access | Page |
|-------|--------|------|
| `/login` | Public | Login |
| `/` | Authenticated | Dashboard (Command Center) |
| `/cameras` | Authenticated | Camera management & live feeds |
| `/incidents` | Authenticated | Incident list & management |
| `/analytics` | Authenticated | Analytics & reports |
| `/logs` | Authenticated | Live system logs |
| `/settings` | Authenticated | Settings |
| `/users` | Admin only | User management |

---

## Scripts

**Frontend** (`package.json`):

| Script | Description |
|--------|-------------|
| `npm run dev` | Start Vite dev server |
| `npm run build` | Production build |
| `npm run preview` | Preview production build |
| `npm run lint` | Lint with Oxlint |

**Backend**:

| Script | Description |
|--------|-------------|
| `python app.py` | Run the Flask + Socket.IO server |
| `python seed_users.py` | Seed demo users |
| `python seed_cameras.py` | Seed demo cameras |
| `python seed_new_incidents.py` | Seed demo incidents |
| `python seed_all.py` | Seed everything |

---

## Security Notes

- 🔐 **Never commit `.env` files** — they are git-ignored. Use `.env.example` as a template and keep real secrets out of version control.
- 🔑 **Change default secrets** (`SECRET_KEY`, `JWT_SECRET_KEY`) and demo credentials before deployment.
- 🎫 **JWT access/refresh tokens** — access tokens expire after 7 days; refresh tokens are revocable and stored in the database.
- 🛡️ **Role-based auth** — API actions are gated by `viewer_required`, `operator_required`, and `admin_required` decorators.
- 🖼️ **Streams are token-protected** — live camera URLs require a valid JWT, either as a query param or `Authorization` header.

---

## License

This project is for educational and research purposes. See the repository for any additional license information.
