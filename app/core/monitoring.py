import os
import time
import logging
import logging.config
import sys
from fastapi import Request, Response, FastAPI
import sentry_sdk
from prometheus_client import Gauge
from prometheus_fastapi_instrumentator import Instrumentator
from app.database import SessionLocal
from app import models
from sqlalchemy import text

# Environment Variables
SENTRY_DSN = os.getenv("SENTRY_DSN")
SENTRY_ENVIRONMENT = os.getenv("SENTRY_ENVIRONMENT", "production")
SENTRY_TRACES_SAMPLE_RATE = float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1"))
SENTRY_ENABLED = os.getenv("SENTRY_ENABLED", "false").lower() == "true"

ENABLE_PROMETHEUS_METRICS = os.getenv("ENABLE_PROMETHEUS_METRICS", "false").lower() == "true"
METRICS_ENDPOINT_AUTH = os.getenv("METRICS_ENDPOINT_AUTH", "false").lower() == "true"

LOG_FORMAT = os.getenv("LOG_FORMAT", "json")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_TO_FILE = os.getenv("LOG_TO_FILE", "false").lower() == "true"
LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "/var/log/classly/app.log")

# Metrics Definitions
CLASSLY_USERS_TOTAL = Gauge(
    "classly_users_total",
    "Total number of users",
    ["role"]
)
CLASSLY_EVENTS_TOTAL = Gauge(
    "classly_events_total",
    "Total number of events",
    ["type"]
)

def setup_logging():
    handlers = []

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    if LOG_FORMAT.lower() == "json":
        from pythonjsonlogger import jsonlogger
        formatter = jsonlogger.JsonFormatter(
            "%(asctime)s %(levelname)s %(name)s %(message)s"
        )
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    console_handler.setFormatter(formatter)
    handlers.append(console_handler)

    # File Handler
    if LOG_TO_FILE:
        # Ensure directory exists
        log_dir = os.path.dirname(LOG_FILE_PATH)
        if log_dir and not os.path.exists(log_dir):
            try:
                os.makedirs(log_dir, exist_ok=True)
            except OSError:
                print(f"Could not create log directory {log_dir}, skipping file logging.")
            else:
                file_handler = logging.FileHandler(LOG_FILE_PATH)
                file_handler.setFormatter(formatter)
                handlers.append(file_handler)

    logging.basicConfig(
        level=LOG_LEVEL,
        handlers=handlers,
        force=True # Override existing config
    )

    logging.info("Logging setup complete", extra={"log_format": LOG_FORMAT, "log_level": LOG_LEVEL})

def setup_sentry():
    if SENTRY_ENABLED and SENTRY_DSN:
        sentry_sdk.init(
            dsn=SENTRY_DSN,
            environment=SENTRY_ENVIRONMENT,
            traces_sample_rate=SENTRY_TRACES_SAMPLE_RATE,
        )
        logging.info("Sentry initialized")
    elif SENTRY_ENABLED and not SENTRY_DSN:
        logging.warning("Sentry enabled but no DSN provided")

def update_db_metrics():
    """Updates Gauge metrics by querying the database."""
    if not ENABLE_PROMETHEUS_METRICS:
        return

    try:
        db = SessionLocal()

        # User Counts by Role
        try:
            # Query count grouped by role
            from sqlalchemy import func
            user_counts = db.query(models.User.role, func.count(models.User.id)).group_by(models.User.role).all()
            for role, count in user_counts:
                CLASSLY_USERS_TOTAL.labels(role=role.value).set(count)
        except Exception as e:
            logging.error(f"Error counting users: {e}")

        # Event Counts by Type
        try:
            event_counts = db.query(models.Event.type, func.count(models.Event.id)).group_by(models.Event.type).all()
            for type_, count in event_counts:
                CLASSLY_EVENTS_TOTAL.labels(type=type_.value).set(count)
        except Exception as e:
            logging.error(f"Error counting events: {e}")

    except Exception as e:
        logging.error(f"Error updating DB metrics: {e}")
    finally:
        db.close()

def setup_prometheus(app: FastAPI):
    if ENABLE_PROMETHEUS_METRICS:
        # We don't use expose() here because we want to handle the endpoint manually
        # in the router to support our custom auth logic.
        # instrument() registers the middleware.
        instrumentator = Instrumentator()
        instrumentator.instrument(app)
