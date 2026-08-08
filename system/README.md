# Sentinel — Mega Dashboard (Phase 5.3 / 5.4)

Real-time hybrid anomaly detection pipeline: YOLO-Pose (fall / fight / running),
YOLO-Object (crowd + banned-object anomalies), a fire/smoke OpenVINO model, and
a flashing-alert overlay — with live MJPEG streaming and incident reporting to
the QAU Sentinel Flask backend.

> This folder is the AI detection engine for the **QAU Sentinel** project. It feeds
> incidents and live status into the web dashboard in the sibling
> `Qau_Sentinel/QAU_SENTINEL/` directory (Flask backend + React frontend).

## Pipeline

```
Camera → OpenCV capture
       → YOLO-Pose (every frame)        → PersonTrack state machines → fall / running / fight
       → YOLO-Object (every Nth frame)  → crowd count + banned-object anomalies
       → Fire/Smoke OpenVINO (bg thread, throttled)
       → MegaAlertManager               → flashing overlay, screenshot log, on_alert callback
       → FrameBroadcaster (optional)    → MJPEG stream  → React dashboard video panel
       → DashboardClient (optional)     → POST /api/incidents → Sentinel Flask backend
```

## Files

| File | Role |
|---|---|
| `master_mega_dashboard.py` | Entry point — the real-time detection loop |
| `master_detection_functions_modified.py` | Fire/smoke detector, crowd counter, HUD overlay, MJPEG broadcaster |
| `master_mega_alerts.py` | `MegaAlertManager` — flashing boxes, screenshot logging, `on_alert` hook |
| `motion_heuristics_Fall_modified.py` | `PersonTrack`, `check_fight` — fall/running/fight state machines |
| `dashboard_client.py` | Pushes incidents to the Sentinel Flask backend asynchronously |
| `.env.example` | Template for dashboard connection credentials (safe to commit) |
| `requirements.txt` | Python dependencies |

## Setup

### 1. Create and activate a virtual environment

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Windows (cmd.exe):**
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

You'll know it worked when your shell prompt is prefixed with `(.venv)`.

### 2. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

> **GPU note:** `ultralytics` pulls in `torch` automatically. If your machine
> has an NVIDIA GPU and you want CUDA acceleration, install the matching
> `torch`/`torchvision` build from https://pytorch.org/get-started/locally/
> **before** running `pip install -r requirements.txt` — otherwise you'll get
> the CPU-only wheel by default.

### 3. Prepare the environment file

Copy the template and fill in your dashboard credentials if you plan to report
incidents to the QAU Sentinel backend:

```bash
copy .env.example .env    # Windows
# cp .env.example .env    # macOS / Linux
```

See the [dashboard connection credentials](#dashboard-connection-credentials)
section for the variables it contains.

### 4. Get the models in place

`master_mega_dashboard.py` expects three exported model folders, passed via
CLI flags (defaults shown):

- `--pose-model` → `yolov8n-pose_openvino_model`
- `--object-model` → `yolo11n_openvino_model_320`
- `--fire-smoke-model` → path to your exported fire/smoke `*_openvino_model` folder

Each is an OpenVINO IR export (a folder containing `model.xml` / `model.bin`),
produced via `model.export(format="openvino")` from the corresponding `.pt`
weights — not the raw `.pt` file itself.

## Running

Minimal (local display only, no dashboard/stream):
```bash
python master_mega_dashboard.py --source 0
```

Full pipeline, with the live stream and dashboard reporting enabled:
```bash
python master_mega_dashboard.py --source 0 \
    --enable-stream --stream-port 8080 \
    --enable-dashboard --dashboard-ip 192.168.1.50 --dashboard-port 5000 \
    --camera-id 1 --camera-location "Main Entrance"
```

- `--source`: `0` = integrated webcam, `1` = Iriun webcam, `2` = USB camera, or a path to a video file. Omit it and you'll be prompted interactively.
- `--enable-stream`: serves the annotated feed at `http://<this-machine-ip>:<stream-port>/stream` — point an `<img>`/`<video>` tag on the React dashboard at that URL.
- `--enable-dashboard`: POSTs each new (de-duplicated) incident to the Flask backend's `/api/incidents` endpoint.
- Press `q` in the video window to quit; both background threads (fire/smoke detector, dashboard client) shut down cleanly.

Run `python master_mega_dashboard.py --help` for the full flag list (thresholds, alert cooldowns, panel side, etc.).

### Dashboard connection credentials

`dashboard_client.py` authenticates to the QAU Sentinel backend using **environment variables** — no credentials are hardcoded. Set them in a local `.env` file (git-ignored):

```bash
# system/.env  (copy from .env.example)
DASHBOARD_IP=127.0.0.1
DASHBOARD_PORT=5000
DASHBOARD_EMAIL=admin@qau.edu.pk
DASHBOARD_PASSWORD=admin123
```

> Use the credentials of any active user on the QAU Sentinel backend (see the `backend/seed_users.py` file for the seeded demo accounts). Change these before any real deployment. The connection values can also be overridden via the `DashboardClient(...)` constructor or its environment variables.

## Output

- `Alerts/` — screenshots of every logged incident, named `<type>_<timestamp>.png`
- Console logs from `MegaAlertManager`, `FireSmokeDetector`, `DashboardClient`, and `FrameBroadcaster`

## Troubleshooting

- **"Could not open video source"** — another process (or the streaming server, if you're running an older version that opens its own capture) is holding the camera. Close other apps using the webcam and retry.
- **Dashboard login fails / incidents not appearing** — confirm the Flask backend is running and reachable. Check that `DASHBOARD_EMAIL` / `DASHBOARD_PASSWORD` in your `.env` match an active user on the backend (`/api/auth/login`), and that the user has permission to create incidents (Operator or Admin).
- **Low FPS** — increase `--frame-skip` (object model runs less often) or `--fire-smoke-interval-frames` (fire/smoke thread polls less often); both trade detection latency for speed.
- **`ModuleNotFoundError: flask` / `requests`** — these are only required if you use `--enable-stream` / `--enable-dashboard`; otherwise the core detection loop runs without them, but `pip install -r requirements.txt` installs both regardless.
