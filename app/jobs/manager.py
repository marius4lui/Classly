import logging
import asyncio
import datetime
import json
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import SystemJob, JobStatus

logger = logging.getLogger(__name__)

class JobManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(JobManager, cls).__new__(cls)
            cls._instance.scheduler = BackgroundScheduler()
            # cls._instance.scheduler.start() # Delayed start
            # cls._instance._recover_jobs() # Delayed recovery
        return cls._instance

    def start(self):
        """Starts the scheduler and recovers jobs. Should be called after DB init."""
        if not self.scheduler.running:
            self.scheduler.start()
            self._recover_jobs()

    def _recover_jobs(self):
        """Recover jobs after restart"""
        db = SessionLocal()
        try:
            # 1. Mark stale RUNNING jobs as FAILED
            stale_jobs = db.query(SystemJob).filter(SystemJob.status == JobStatus.RUNNING).all()
            for job in stale_jobs:
                job.status = JobStatus.FAILED
                job.message = "System restarted while job was running."
                job.finished_at = datetime.datetime.utcnow()
                logger.warning(f"Marked stale job {job.id} as FAILED")

            # 2. Mark PENDING as FAILED for safety
            pending_jobs = db.query(SystemJob).filter(SystemJob.status == JobStatus.PENDING).all()
            for job in pending_jobs:
                 job.status = JobStatus.FAILED
                 job.message = "System restarted. Please retry."
                 job.finished_at = datetime.datetime.utcnow()

            db.commit()
        except Exception as e:
            logger.error(f"Job recovery failed: {e}")
        finally:
            db.close()

    def submit_job(self, job_type: str, job_func, created_by: str = "system", **kwargs):
        """Creates a job in DB and submits it to APScheduler"""
        db = SessionLocal()
        try:
            job = SystemJob(
                type=job_type,
                status=JobStatus.PENDING,
                created_by=created_by,
                meta_data=json.dumps(kwargs)
            )
            db.add(job)
            db.commit()
            db.refresh(job)

            # Add to scheduler
            self.scheduler.add_job(
                func=self._run_wrapper,
                args=[job.id, job_func, kwargs],
                id=job.id,
                name=f"{job_type}-{job.id}",
                misfire_grace_time=3600
            )

            return job.id
        except Exception as e:
            logger.error(f"Failed to submit job: {e}")
            return None
        finally:
            db.close()

    def _run_wrapper(self, job_id, func, kwargs):
        """Wraps the actual job function to handle status updates and logging"""
        db = SessionLocal()
        job = db.query(SystemJob).filter(SystemJob.id == job_id).first()
        if not job:
            return

        job.status = JobStatus.RUNNING
        job.started_at = datetime.datetime.utcnow()
        db.commit()

        log_buffer = []

        def log(msg):
            print(f"[JOB {job_id}] {msg}")
            log_buffer.append(f"{datetime.datetime.utcnow().isoformat()} - {msg}")
            # In a real system, we might want to append to DB periodically to see live logs
            # but for now we save at end to reduce DB writes,
            # unless we implement a separate Log table.

            # OPTIONAL: Live log update
            try:
                # Re-fetch to avoid stale object if session was closed?
                # Using same session object `job`
                current_logs = job.logs or ""
                job.logs = current_logs + f"{datetime.datetime.utcnow().isoformat()} - {msg}\n"
                db.commit()
            except:
                pass

        def update_progress(current, total, msg=None):
            job.current_step = current
            job.total_steps = total
            job.progress = int((current / total) * 100) if total > 0 else 0
            if msg:
                job.message = msg
            db.commit()

        try:
            # Run the actual function
            if asyncio.iscoroutinefunction(func):
                 asyncio.run(func(job_id=job_id, log=log, progress=update_progress, **kwargs))
            else:
                 func(job_id=job_id, log=log, progress=update_progress, **kwargs)

            job.status = JobStatus.COMPLETED
            job.message = "Completed successfully"
        except Exception as e:
            logger.exception(f"Job {job_id} failed")
            job.status = JobStatus.FAILED
            job.message = str(e)
            log(f"ERROR: {str(e)}")
        finally:
            job.finished_at = datetime.datetime.utcnow()
            # Final log save
            # job.logs = "\n".join(log_buffer) # Already saving live
            db.commit()
            db.close()

    def get_job(self, job_id: str):
        db = SessionLocal()
        try:
            return db.query(SystemJob).filter(SystemJob.id == job_id).first()
        finally:
            db.close()

    def list_jobs(self, limit=50):
        db = SessionLocal()
        try:
             return db.query(SystemJob).order_by(SystemJob.created_at.desc()).limit(limit).all()
        finally:
            db.close()

job_manager = JobManager()
