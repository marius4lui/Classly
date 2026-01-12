from fastapi import APIRouter, Response, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import os
import secrets
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from app.database import get_db, SessionLocal
from sqlalchemy import text
from app.core.monitoring import update_db_metrics, ENABLE_PROMETHEUS_METRICS, METRICS_ENDPOINT_AUTH

router = APIRouter()
security = HTTPBasic(auto_error=False)
HEALTH_CHECK_ENABLED = os.getenv("HEALTH_CHECK_ENABLED", "true").lower() == "true"

def check_metrics_auth(credentials: HTTPBasicCredentials = Depends(security)):
    if not METRICS_ENDPOINT_AUTH:
        return True

    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Basic"},
        )

    correct_username = os.getenv("PROMETHEUS_USERNAME", "metrics")
    correct_password = os.getenv("PROMETHEUS_PASSWORD", "secret")

    current_username_bytes = credentials.username.encode("utf8")
    correct_username_bytes = correct_username.encode("utf8")
    is_correct_username = secrets.compare_digest(
        current_username_bytes, correct_username_bytes
    )

    current_password_bytes = credentials.password.encode("utf8")
    correct_password_bytes = correct_password.encode("utf8")
    is_correct_password = secrets.compare_digest(
        current_password_bytes, correct_password_bytes
    )

    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return True

# Note: The /api/metrics endpoint is now handled by prometheus-fastapi-instrumentator in setup_prometheus
# BUT, we need to inject the auth check. Instrumentator doesn't support auth easily out of the box unless we wrap the app or middleware.
# Actually, Instrumentator.expose() adds a route.
# "The exposed endpoint can be secured by using the standard FastAPI dependencies." - No, wait, expose just adds a route.
# If I use Instrumentator().expose(app), I can't easily add dependencies to that specific route unless I look at how expose works.
# expose() returns the app.
# The `expose` method has `dependencies` argument in newer versions? Let's check docs or source if possible.
# Assuming standard usage, I might need to NOT use expose() and define the route myself if I want auth, using `generate_latest`.
# So I will keep my route definition here, and `instrumentator.instrument(app)` will just collect metrics.
# I will NOT call `expose(app)` in `monitoring.py` if I define the route manually here.

@router.get("/api/metrics")
def metrics(auth: bool = Depends(check_metrics_auth)):
    if not ENABLE_PROMETHEUS_METRICS:
        return Response(content="Prometheus metrics are disabled", status_code=404)

    # Update our custom DB metrics
    update_db_metrics()

    # generate_latest() will collect all metrics including those from Instrumentator (which uses the default registry)
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

if HEALTH_CHECK_ENABLED:
    @router.get("/api/health")
    def health(db = Depends(get_db)):
        try:
            # Check DB connection
            db.execute(text("SELECT 1"))
            return JSONResponse(status_code=200, content={"status": "ok", "database": "connected"})
        except Exception as e:
            return JSONResponse(status_code=503, content={"status": "error", "database": str(e)})
