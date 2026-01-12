import os
import shutil
import datetime
import glob
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import boto3
from botocore.exceptions import NoCredentialsError
from cryptography.fernet import Fernet
import sqlite3
import fcntl
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
BACKUP_ENABLED = os.getenv("BACKUP_ENABLED", "false").lower() == "true"
BACKUP_CRON = os.getenv("BACKUP_CRON", "0 3 * * *")  # Daily at 3 AM
BACKUP_RETENTION_DAYS = int(os.getenv("BACKUP_RETENTION_DAYS", "30"))
BACKUP_ENCRYPT = os.getenv("BACKUP_ENCRYPT", "false").lower() == "true"
BACKUP_ENCRYPTION_KEY = os.getenv("BACKUP_ENCRYPTION_KEY")

S3_ENABLED = os.getenv("S3_ENABLED", "false").lower() == "true"
S3_ENDPOINT = os.getenv("S3_ENDPOINT")
S3_REGION = os.getenv("S3_REGION", "eu-central-1")
S3_BUCKET = os.getenv("S3_BUCKET", "classly-backups")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY")
S3_PATH_PREFIX = os.getenv("S3_PATH_PREFIX", "backups/")

LOCAL_BACKUP_PATH = os.getenv("LOCAL_BACKUP_PATH", "/var/backups/classly")
LOCAL_BACKUP_ENABLED = os.getenv("LOCAL_BACKUP_ENABLED", "true").lower() == "true"
DB_PATH = os.getenv("DATABASE_URL", "sqlite:///./classly.db").replace("sqlite:///", "")

scheduler = BackgroundScheduler()

class BackupManager:
    @staticmethod
    def ensure_backup_dir():
        if not os.path.exists(LOCAL_BACKUP_PATH):
            os.makedirs(LOCAL_BACKUP_PATH)

    @staticmethod
    def _stream_encrypt_file(source_path, dest_path, key):
        fernet = Fernet(key)
        # Fernet doesn't support streaming encryption directly because it requires the whole block for padding/auth.
        # However, for large files, we can encrypt in chunks if we use a streaming cipher,
        # but Fernet is the easiest high-level API.
        # If we must stick to Fernet and avoid OOM, we can't easily stream with standard Fernet
        # because it produces a single token.
        # BUT: We can use `cryptography.hazmat.primitives.ciphers.aead.ChaCha20Poly1305` or `AESGCM` for streaming,
        # or just read the file into memory if we assume it fits (user risk).
        # Reviewer asked for "Stream Encryption".
        # Fernet is standard in `cryptography`. To stream, one might encrypt chunks and append,
        # but decryption needs to know boundaries.
        # A simpler way to reduce memory usage is to read/write in large chunks (e.g. 64MB)
        # IF the encryption mode supports it. Fernet does NOT support streaming natively.
        # So we will switch to a loop that reads a chunk, encrypts it independently, and writes it.
        # On decrypt, we read chunks and decrypt.
        # Warning: This changes the file format to a sequence of Fernet tokens.

        chunk_size = 64 * 1024 * 1024 # 64MB chunks
        with open(source_path, "rb") as fin, open(dest_path, "wb") as fout:
            while True:
                chunk = fin.read(chunk_size)
                if not chunk:
                    break
                encrypted_chunk = fernet.encrypt(chunk)
                # Write length of chunk first to know where to split?
                # Fernet output is base64url, so no fixed length expansion ratio.
                # Better: Use a length prefix.
                fout.write(len(encrypted_chunk).to_bytes(4, 'big'))
                fout.write(encrypted_chunk)

    @staticmethod
    def _stream_decrypt_file(source_path, dest_path, key):
        fernet = Fernet(key)
        with open(source_path, "rb") as fin, open(dest_path, "wb") as fout:
            while True:
                length_bytes = fin.read(4)
                if not length_bytes:
                    break
                length = int.from_bytes(length_bytes, 'big')
                chunk = fin.read(length)
                if not chunk:
                    break # Should not happen if file is valid
                decrypted_chunk = fernet.decrypt(chunk)
                fout.write(decrypted_chunk)

    @staticmethod
    def create_backup():
        BackupManager.ensure_backup_dir()
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"classly_backup_{timestamp}.db"
        filepath = os.path.join(LOCAL_BACKUP_PATH, filename)

        logger.info(f"Starting backup: {filename}")

        try:
            # 1. Create SQLite Backup (using VACUUM INTO for online backup)
            db_file = os.path.abspath(DB_PATH) if not os.path.isabs(DB_PATH) else DB_PATH

            if not os.path.exists(db_file):
                logger.error(f"Database file not found: {db_file}")
                return None

            # Use sqlite3 API to backup safely
            src = sqlite3.connect(db_file)
            dst = sqlite3.connect(filepath)
            with dst:
                src.backup(dst)
            dst.close()
            src.close()

            logger.info(f"Local backup created: {filepath}")

            # 2. Encrypt if enabled
            final_filepath = filepath
            if BACKUP_ENCRYPT and BACKUP_ENCRYPTION_KEY:
                logger.info("Encrypting backup...")
                final_filepath = filepath + ".enc"
                BackupManager._stream_encrypt_file(filepath, final_filepath, BACKUP_ENCRYPTION_KEY)

                # Remove unencrypted file
                os.remove(filepath)
                logger.info(f"Encrypted backup saved: {final_filepath}")

            # 3. Upload to S3 if enabled
            if S3_ENABLED:
                logger.info("Uploading to S3...")
                s3_filename = os.path.basename(final_filepath)
                s3_key = f"{S3_PATH_PREFIX}{s3_filename}"

                s3 = boto3.client(
                    's3',
                    endpoint_url=S3_ENDPOINT,
                    region_name=S3_REGION,
                    aws_access_key_id=S3_ACCESS_KEY,
                    aws_secret_access_key=S3_SECRET_KEY
                )
                s3.upload_file(final_filepath, S3_BUCKET, s3_key)
                logger.info(f"Uploaded to S3: {s3_key}")

            # 4. Cleanup old backups
            BackupManager.cleanup_old_backups()

            return final_filepath

        except Exception as e:
            logger.error(f"Backup failed: {e}")
            return None

    @staticmethod
    def cleanup_old_backups():
        # Local Cleanup
        if LOCAL_BACKUP_ENABLED:
            now = datetime.datetime.now()
            retention_delta = datetime.timedelta(days=BACKUP_RETENTION_DAYS)

            for f in os.listdir(LOCAL_BACKUP_PATH):
                f_path = os.path.join(LOCAL_BACKUP_PATH, f)
                if os.path.isfile(f_path):
                    creation_time = datetime.datetime.fromtimestamp(os.path.getmtime(f_path))
                    if now - creation_time > retention_delta:
                        os.remove(f_path)
                        logger.info(f"Deleted old local backup: {f}")

        # S3 Cleanup (List and delete)
        if S3_ENABLED:
            try:
                s3 = boto3.client(
                    's3',
                    endpoint_url=S3_ENDPOINT,
                    region_name=S3_REGION,
                    aws_access_key_id=S3_ACCESS_KEY,
                    aws_secret_access_key=S3_SECRET_KEY
                )

                response = s3.list_objects_v2(Bucket=S3_BUCKET, Prefix=S3_PATH_PREFIX)
                if 'Contents' in response:
                    now_utc = datetime.datetime.now(datetime.timezone.utc)
                    retention_delta = datetime.timedelta(days=BACKUP_RETENTION_DAYS)

                    for obj in response['Contents']:
                        last_modified = obj['LastModified']
                        if now_utc - last_modified > retention_delta:
                            s3.delete_object(Bucket=S3_BUCKET, Key=obj['Key'])
                            logger.info(f"Deleted old S3 backup: {obj['Key']}")
            except Exception as e:
                logger.error(f"S3 Cleanup failed: {e}")

    @staticmethod
    def list_backups():
        backups = []
        # List Local
        if LOCAL_BACKUP_ENABLED and os.path.exists(LOCAL_BACKUP_PATH):
            for f in os.listdir(LOCAL_BACKUP_PATH):
                f_path = os.path.join(LOCAL_BACKUP_PATH, f)
                if os.path.isfile(f_path):
                    backups.append({
                        "name": f,
                        "size": os.path.getsize(f_path),
                        "created_at": datetime.datetime.fromtimestamp(os.path.getmtime(f_path)),
                        "source": "local"
                    })

        # List S3
        if S3_ENABLED:
             try:
                s3 = boto3.client(
                    's3',
                    endpoint_url=S3_ENDPOINT,
                    region_name=S3_REGION,
                    aws_access_key_id=S3_ACCESS_KEY,
                    aws_secret_access_key=S3_SECRET_KEY
                )
                response = s3.list_objects_v2(Bucket=S3_BUCKET, Prefix=S3_PATH_PREFIX)
                if 'Contents' in response:
                    for obj in response['Contents']:
                        name = os.path.basename(obj['Key'])
                        backups.append({
                            "name": name,
                            "size": obj['Size'],
                            "created_at": obj['LastModified'],
                            "source": "s3"
                        })
             except Exception as e:
                 logger.error(f"Failed to list S3 backups: {e}")

        # Sort by date desc
        backups.sort(key=lambda x: x['created_at'], reverse=True)
        return backups

    @staticmethod
    def restore_backup(filename, source="local"):
        # 1. Sanitize filename (prevent path traversal)
        filename = os.path.basename(filename)

        logger.info(f"Restoring backup {filename} from {source}")
        temp_path = f"/tmp/{filename}"

        try:
            # 2. Fetch File
            if source == "s3":
                s3 = boto3.client(
                    's3',
                    endpoint_url=S3_ENDPOINT,
                    region_name=S3_REGION,
                    aws_access_key_id=S3_ACCESS_KEY,
                    aws_secret_access_key=S3_SECRET_KEY
                )
                key = f"{S3_PATH_PREFIX}{filename}"
                s3.download_file(S3_BUCKET, key, temp_path)
            else:
                local_path = os.path.join(LOCAL_BACKUP_PATH, filename)
                if not os.path.exists(local_path):
                     raise FileNotFoundError(f"Backup file not found: {local_path}")
                shutil.copy(local_path, temp_path)

            # 3. Decrypt if needed
            restore_path = temp_path
            if filename.endswith(".enc"):
                 if not BACKUP_ENCRYPTION_KEY:
                     raise ValueError("Backup is encrypted but no key provided")

                 decrypted_path = temp_path.replace(".enc", "")
                 BackupManager._stream_decrypt_file(temp_path, decrypted_path, BACKUP_ENCRYPTION_KEY)
                 restore_path = decrypted_path

            # 4. Replace Database
            db_file = os.path.abspath(DB_PATH) if not os.path.isabs(DB_PATH) else DB_PATH

            # Verify SQLite file integrity
            try:
                test_conn = sqlite3.connect(restore_path)
                test_conn.execute("PRAGMA integrity_check")
                test_conn.close()
            except Exception as e:
                raise ValueError(f"Backup file integrity check failed: {e}")

            # ATTEMPT TO DISPOSE ENGINE (Best Effort)
            try:
                from app.database import engine
                engine.dispose()
            except ImportError:
                pass
            except Exception as e:
                logger.warning(f"Could not dispose engine: {e}")

            if os.path.exists(db_file):
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                os.rename(db_file, f"{db_file}.pre_restore_{timestamp}.bak")

            shutil.move(restore_path, db_file)
            logger.info("Database restored successfully")
            return True

        except Exception as e:
            logger.error(f"Restore failed: {e}")
            raise e
        finally:
            # Cleanup temp files
            if os.path.exists(temp_path):
                os.remove(temp_path)
            if 'decrypted_path' in locals() and os.path.exists(decrypted_path):
                os.remove(decrypted_path)

def start_scheduler():
    if BACKUP_ENABLED:
        # File Lock to prevent multiple schedulers (e.g. Gunicorn workers)
        lock_file = open('/tmp/classly_scheduler.lock', 'w')
        try:
            # Try to acquire an exclusive lock
            fcntl.lockf(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except IOError:
            logger.info("Scheduler already running in another process.")
            return

        # If we got the lock, start the scheduler
        parts = BACKUP_CRON.split()
        if len(parts) == 5:
            scheduler.add_job(
                BackupManager.create_backup,
                CronTrigger(
                    minute=parts[0],
                    hour=parts[1],
                    day=parts[2],
                    month=parts[3],
                    day_of_week=parts[4]
                ),
                id="backup_job",
                replace_existing=True
            )
            scheduler.start()
            logger.info(f"Backup scheduler started with cron: {BACKUP_CRON}")
        else:
            logger.error(f"Invalid cron format: {BACKUP_CRON}")

        # Keep lock file open?
        # Yes, if we close it, we lose the lock.
        # But this function returns. The file handle `lock_file` is local var.
        # It will be garbage collected and closed.
        # We need to keep the reference globally.
        global _scheduler_lock
        _scheduler_lock = lock_file

_scheduler_lock = None
