import threading
import time

from flask import Blueprint, jsonify, request

detection_bp = Blueprint(
    "detections",
    __name__,
)

# ── In-memory cache for live detection status pushed by the detection pipeline ──
_live_status_cache = {
    "fire": False,
    "smoke": False,
    "crowd": False,
    "detections": [],
    "count": 0,
    "timestamp": 0.0,
    "camera_id": 0,
    "area_m2": None,
    "density_people_per_m2": None,
    "zone_densities": [],
    "head_positions_world": [],
    "events": [],
}
_cache_lock = threading.Lock()
_CACHE_TTL_SEC = 120.0  # Treat cache as stale after 120s without an update (external pipeline pushes every ~1s)


def _cache_is_fresh() -> bool:
    """Return True if the cache has been updated within TTL."""
    with _cache_lock:
        return (time.time() - _live_status_cache["timestamp"]) < _CACHE_TTL_SEC


def _get_cached_data():
    """Return the current cached data with a copy to avoid race conditions."""
    with _cache_lock:
        return {
            "fire": _live_status_cache["fire"],
            "smoke": _live_status_cache["smoke"],
            "crowd": _live_status_cache["crowd"],
            "detections": list(_live_status_cache["detections"]),
            "count": _live_status_cache["count"],
            "camera_id": _live_status_cache["camera_id"],
            "area_m2": _live_status_cache["area_m2"],
            "density_people_per_m2": _live_status_cache["density_people_per_m2"],
            "zone_densities": list(_live_status_cache["zone_densities"]),
            "head_positions_world": list(_live_status_cache["head_positions_world"]),
            "events": list(_live_status_cache["events"]),
            "source": "live_pipeline",
            "stale": False,
        }


@detection_bp.get("/")
def get_detections():
    """
    Return detections — from live cache if fresh.
    NO camera fallback to avoid competing with the external detection pipeline.
    """
    if _cache_is_fresh():
        with _cache_lock:
            return jsonify(
                {
                    "count": len(_live_status_cache["detections"]),
                    "detections": _live_status_cache["detections"],
                    "source": "live_pipeline",
                }
            )

    # Return empty detections (last known state) instead of trying to open camera
    with _cache_lock:
        return jsonify(
            {
                "count": _live_status_cache["count"],
                "detections": _live_status_cache["detections"],
                "source": "live_pipeline",
                "stale": True,
            }
        )


@detection_bp.get("/latest")
def latest_detection():
    """
    Return the latest detection summary — from live cache if fresh.
    NO camera fallback to avoid competing with the external detection pipeline.
    """
    if _cache_is_fresh():
        with _cache_lock:
            return jsonify(
                {
                    "fire": _live_status_cache["fire"],
                    "smoke": _live_status_cache["smoke"],
                    "crowd": _live_status_cache["crowd"],
                    "detections": _live_status_cache["detections"],
                    "area_m2": _live_status_cache["area_m2"],
                    "density_people_per_m2": _live_status_cache["density_people_per_m2"],
                    "zone_densities": _live_status_cache["zone_densities"],
                    "head_positions_world": _live_status_cache["head_positions_world"],
                    "events": _live_status_cache["events"],
                    "source": "live_pipeline",
                }
            )

    # Return last known status (stale) instead of trying to open camera
    with _cache_lock:
        return jsonify(
            {
                "fire": _live_status_cache["fire"],
                "smoke": _live_status_cache["smoke"],
                "crowd": _live_status_cache["crowd"],
                "detections": _live_status_cache["detections"],
                "area_m2": _live_status_cache["area_m2"],
                "density_people_per_m2": _live_status_cache["density_people_per_m2"],
                "zone_densities": _live_status_cache["zone_densities"],
                "head_positions_world": _live_status_cache["head_positions_world"],
                "events": _live_status_cache["events"],
                "source": "live_pipeline",
                "stale": True,
            }
        )


# ── POST endpoint — called by the detection pipeline to push live status ──

@detection_bp.post("/status")
def push_detection_status():
    """
    Accept a live detection status snapshot pushed by the external
    detection pipeline (master_mega_dashboard.py via DashboardClient).

    Body (JSON):
    {
        "fire": bool,
        "smoke": bool,
        "crowd": bool,
        "detections": list,
        "camera_id": int,
        "area_m2": float,
        "density_people_per_m2": float,
        "zone_densities": list,
        "head_positions_world": list,
        "events": list
    }
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON body"}), 400

    with _cache_lock:
        _live_status_cache["fire"] = bool(data.get("fire", False))
        _live_status_cache["smoke"] = bool(data.get("smoke", False))
        _live_status_cache["crowd"] = bool(data.get("crowd", False))
        _live_status_cache["detections"] = data.get("detections", [])
        _live_status_cache["count"] = len(_live_status_cache["detections"])
        _live_status_cache["camera_id"] = int(data.get("camera_id", 1))
        _live_status_cache["area_m2"] = data.get("area_m2")
        _live_status_cache["density_people_per_m2"] = data.get("density_people_per_m2")
        _live_status_cache["zone_densities"] = data.get("zone_densities", [])
        _live_status_cache["head_positions_world"] = data.get("head_positions_world", [])
        _live_status_cache["events"] = data.get("events", [])
        _live_status_cache["timestamp"] = time.time()

    return jsonify({"status": "ok", "message": "Detection status updated"}), 200
