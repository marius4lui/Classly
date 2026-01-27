import os
import json
import datetime
import tempfile
import shutil
from app.providers.sqlite import SqliteProvider
from app.providers.s3 import S3Provider
from app.jobs.migration import MIGRATION_ORDER, get_provider

def run_backup(job_id, log, progress, source_config, target_config, **kwargs):
    log("Starting Backup...")

    source = get_provider(source_config["type"], source_config)
    s3 = None
    if target_config["type"] == "s3":
        s3 = S3Provider(
            endpoint=target_config.get("endpoint"),
            access_key=target_config.get("access_key"),
            secret_key=target_config.get("secret_key"),
            bucket=target_config.get("bucket")
        )

    temp_dir = tempfile.mkdtemp()
    backup_file = os.path.join(temp_dir, f"backup_{job_id}.jsonl")

    try:
        source.connect()

        total_rows = 0
        source_tables = source.list_tables()
        tables = [t for t in MIGRATION_ORDER if t in source_tables]

        for t in tables:
            total_rows += source.count(t)

        current_row = 0

        with open(backup_file, "w") as f:
            for table in tables:
                log(f"Exporting {table}...")
                offset = 0
                limit = 1000
                while True:
                    chunk = source.read_table(table, limit, offset)
                    if not chunk:
                        break

                    for row in chunk:
                        # Add metadata table name
                        record = {"_table": table, "data": row}
                        f.write(json.dumps(record, default=str) + "\n")

                    offset += len(chunk)
                    current_row += len(chunk)
                    progress(current_row, total_rows, f"Exporting {table}")

        log("Export complete. Uploading...")

        if s3:
            key = f"backups/{datetime.date.today().isoformat()}_{job_id}.jsonl"
            s3.upload_file(backup_file, key)
            log(f"Uploaded to S3: {key}")
        else:
            # Local move
            dest_dir = target_config.get("path", "./backups")
            os.makedirs(dest_dir, exist_ok=True)
            dest_path = os.path.join(dest_dir, f"backup_{job_id}.jsonl")
            shutil.copy(backup_file, dest_path)
            log(f"Saved locally to {dest_path}")

    except Exception as e:
        log(f"Backup failed: {e}")
        raise e
    finally:
        source.close()
        shutil.rmtree(temp_dir)

def run_restore(job_id, log, progress, target_config, backup_source, **kwargs):
    log("Starting Restore...")
    target = get_provider(target_config["type"], target_config)

    temp_file = None

    try:
        if backup_source["type"] == "s3":
            s3 = S3Provider(
                endpoint=backup_source.get("endpoint"),
                access_key=backup_source.get("access_key"),
                secret_key=backup_source.get("secret_key"),
                bucket=backup_source.get("bucket")
            )
            temp_fd, temp_path = tempfile.mkstemp()
            os.close(temp_fd)
            temp_file = temp_path

            log(f"Downloading from S3: {backup_source['key']}")
            s3.download_file(backup_source['key'], temp_file)
            input_file = temp_file
        else:
            input_file = backup_source["path"]

        target.connect()

        # Count lines for progress
        total_lines = 0
        try:
            with open(input_file, 'r') as f:
                for _ in f: total_lines += 1
        except FileNotFoundError:
            raise Exception(f"Backup file not found: {input_file}")

        log(f"Restoring {total_lines} records...")

        current = 0
        batch = {} # table -> list of rows

        with open(input_file, 'r') as f:
            for line in f:
                try:
                    record = json.loads(line)
                    table = record["_table"]
                    data = record["data"]

                    if table not in MIGRATION_ORDER:
                        log(f"Skipping unknown table: {table}")
                        continue

                    if table not in batch: batch[table] = []
                    batch[table].append(data)

                    # Write batch when full
                    if len(batch[table]) >= 1000:
                        target.write_table(table, batch[table])
                        batch[table] = []

                    current += 1
                    if current % 1000 == 0:
                        progress(current, total_lines, f"Restoring... {current}/{total_lines}")

                except Exception as ex:
                    log(f"Skipping bad line: {ex}")

        # Flush remaining
        for table, rows in batch.items():
            if rows:
                target.write_table(table, rows)

        log("Restore completed.")

    except Exception as e:
        log(f"Restore failed: {e}")
        raise e
    finally:
        if temp_file and os.path.exists(temp_file):
            os.unlink(temp_file)
        target.close()
