# AI Surveillance Backend

Flask backend for the AI Surveillance System.

> This directory is part of the **QAU Sentinel** project — a real-time AI-powered
> video surveillance & incident management platform. It exposes the REST + Socket.IO
> API consumed by the React frontend in `src/`, and receives incidents pushed from
> the AI detection pipeline in the sibling `system/` directory. See the project
> root `README.md` for the full picture.

---

## Tech Stack

- Flask
- Flask-CORS
- OpenCV
- Ultralytics YOLOv8
- SQLite
- SQLAlchemy

---

## Folder Structure

```text
backend/
│
├── api/
├── database/
├── models/
├── services/
├── utils/
│
├── app.py
├── config.py
├── requirements.txt
├── .env.example
└── README.md
```

---

## Installation

### 1. Create a virtual environment

Windows:

```bash
python -m venv venv
```

Activate it:

```bash
venv\Scripts\activate
```

---

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 3. Create your environment file

Copy:

```text
.env.example
```

to

```text
.env
```

and update any values if necessary.

---

### 4. Run the backend

```bash
python app.py
```

The backend will start at:

```text
http://localhost:5000
```

---

## Health Check

Open:

```text
http://localhost:5000/api/health
```

Expected response:

```json
{
    "status": "healthy",
    "message": "AI Surveillance Backend is running",
    "version": "1.0.0"
}
```

---

## Upcoming Features

- SQLite database
- Camera streaming
- YOLOv8 object detection
- Incident management
- Analytics API
- Report generation
- React integration