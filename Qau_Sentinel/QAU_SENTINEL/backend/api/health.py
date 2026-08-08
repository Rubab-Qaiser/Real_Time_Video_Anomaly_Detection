from flask import Blueprint, jsonify

health_bp = Blueprint(
    "health",
    __name__,
)


@health_bp.get("/health")
def health_check():
    """
    Health check endpoint.

    Used to verify that the backend server is
    running and reachable.
    """

    return (
        jsonify(
            {
                "status": "healthy",
                "message": "AI Surveillance Backend is running",
                "version": "1.0.0",
            }
        ),
        200,
    )