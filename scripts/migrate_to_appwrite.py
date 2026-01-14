import os
import sys
import sqlite3
import argparse
from datetime import datetime

# Try to import appwrite
try:
    from appwrite.client import Client
    from appwrite.services.databases import Databases
    from appwrite.id import ID
    from appwrite.permission import Permission
    from appwrite.role import Role
except ImportError:
    print("❌ Das 'appwrite' Paket fehlt. Bitte installiere es mit: pip install appwrite")
    sys.exit(1)

# Default Configuration
DEFAULT_DB_PATH = "./classly.db"
APPWRITE_ENDPOINT = os.getenv("APPWRITE_ENDPOINT", "https://cloud.appwrite.io/v1")
APPWRITE_PROJECT_ID = os.getenv("APPWRITE_PROJECT_ID")
APPWRITE_API_KEY = os.getenv("APPWRITE_API_KEY")
APPWRITE_DB_ID = os.getenv("APPWRITE_DATABASE_ID", "classly_db")

# Try to import appwrite
try:
    from appwrite.client import Client
    from appwrite.services.databases import Databases
    from appwrite.services.users import Users
    from appwrite.id import ID
except ImportError:
    print("❌ Das 'appwrite' Paket fehlt. Bitte installiere es mit: pip install appwrite")
    sys.exit(1)

import time
import warnings
import secrets

# Suppress DeprecationWarnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

def connect_sqlite(db_path):
    if not os.path.exists(db_path):
        print(f"❌ SQLite Datenbank nicht gefunden unter: {db_path}")
        sys.exit(1)
    return sqlite3.connect(db_path)

def setup_appwrite():
    if not APPWRITE_PROJECT_ID or not APPWRITE_API_KEY:
        print("❌ Bitte setze APPWRITE_PROJECT_ID und APPWRITE_API_KEY Environment Variablen.")
        sys.exit(1)
    
    client = Client()
    client.set_endpoint(APPWRITE_ENDPOINT)
    client.set_project(APPWRITE_PROJECT_ID)
    client.set_key(APPWRITE_API_KEY)
    
    return Databases(client), Users(client)

def wait_for_attribute(db_service, collection_id, key):
    """Polls attribute status until it is 'available'."""
    print(f"    ⏳ Warte auf Attribut '{key}'...", end="", flush=True)
    for _ in range(30):
        try:
            attr = db_service.get_attribute(APPWRITE_DB_ID, collection_id, key)
            if attr['status'] == 'available':
                print(" ✅")
                return
        except:
            pass
        time.sleep(2)
        print(".", end="", flush=True)
    print(" ⚠️ (Timeout, mache weiter)")

def migrate_to_appwrite(sqlite_conn, db_service, users_service):
    print("🚀 Starte Migration zu Appwrite...")
    
    # Check Database
    try:
        db_service.get(APPWRITE_DB_ID)
        print(f"✓ Datenbank '{APPWRITE_DB_ID}' gefunden.")
    except:
        print(f"Erstelle Datenbank '{APPWRITE_DB_ID}'...")
        db_service.create(APPWRITE_DB_ID, APPWRITE_DB_ID)

    # --- 1. Classes ---
    print("\n📦 Migriere Klassen...")
    migrate_table(
        sqlite_conn, db_service, 
        table_name="classes", 
        collection_id="classes",
        attributes=[
            ("name", "string", 255, True),
            ("owner_id", "string", 255, True),
            ("join_token", "string", 255, False),
            ("join_enabled", "boolean", 0, False),
        ]
    )

    # --- 2. Users (to Appwrite Auth) ---
    print("\n👤 Migriere Benutzer (in Auth)...")
    migrate_users_to_auth(sqlite_conn, users_service)

    # --- 3. Events ---
    print("\n📅 Migriere Events...")
    migrate_table(
        sqlite_conn, db_service,
        table_name="events",
        collection_id="events",
        attributes=[
            ("title", "string", 255, False),
            ("class_id", "string", 255, True),
            ("type", "string", 50, True),
            ("priority", "string", 50, False),
            ("date", "datetime", 0, False),
            ("author_id", "string", 255, True),
        ]
    )

    print("\n✅ Migration abgeschlossen!")

def migrate_users_to_auth(sqlite_conn, users_service):
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT * FROM users")
    # Get columns
    cols = [description[0] for description in cursor.description]
    rows = cursor.fetchall()
    
    count = 0
    for row in rows:
        user_data = dict(zip(cols, row))
        uid = user_data['id']
        
        # Sanitize ID
        uid = uid[:36].replace("-", "").replace("_", "")
        if not uid: uid = ID.unique()

        # Email & Password
        email = user_data.get('email')
        if not email:
            # Fallback email for users without one
            email = f"{uid}@classly.local"
        
        # We cannot migrate the unknown hash easily without knowing the algo details and salt format
        # So we set a dummy password or keep it empty if allowed (but email users need pass)
        # For now: Random Password (User must reset or use Magic Link)
        password = secrets.token_urlsafe(16)
        
        # Attributes to Prefs
        prefs = {}
        for key in ['role', 'class_id', 'is_registered', 'language']:
            if key in user_data and user_data[key] is not None:
                # Convert bools for prefs (Appwrite prefs values must be strings/numbers/bools)
                val = user_data[key]
                if isinstance(val, int) and (key == 'is_registered'): # SQLite bool might be int
                    val = bool(val)
                prefs[key] = val
        
        try:
            # Check if user exists
            try:
                users_service.get(uid)
                print(f"    User {uid} existiert bereits (skip).")
                # Update prefs?
                users_service.update_prefs(uid, prefs)
                continue
            except:
                pass

            # Create User
            users_service.create(
                user_id=uid,
                email=email,
                password=password,
                name=user_data.get('name')
            )
            # Update Prefs (Classly specific data)
            users_service.update_prefs(uid, prefs)
            
            count += 1
            print(f"    + User '{user_data.get('name')}' angelegt.", end="\r")
            
        except Exception as e:
            print(f"    ⚠️ Fehler bei User {uid}: {e}")
            
    print(f"  ✓ {count} Benutzer in Auth migriert.")

import time
import warnings

# Suppress DeprecationWarnings from Appwrite SDK mismatch
warnings.filterwarnings("ignore", category=DeprecationWarning)

def wait_for_attribute(db_service, collection_id, key):
    """Polls attribute status until it is 'available'."""
    print(f"    ⏳ Warte auf Attribut '{key}'...", end="", flush=True)
    for _ in range(30): # Wait max 60 seconds
        try:
            attr = db_service.get_attribute(APPWRITE_DB_ID, collection_id, key)
            if attr['status'] == 'available':
                print(" ✅")
                return
        except:
            pass
        time.sleep(2)
        print(".", end="", flush=True)
    print(" ⚠️ (Timeout, mache weiter)")

def migrate_table(sqlite_conn, db_service, table_name, collection_id, attributes):
    # 1. Create Collection if not exists
    try:
        db_service.get_collection(APPWRITE_DB_ID, collection_id)
        print(f"  ✓ Collection '{collection_id}' existiert.")
    except:
        print(f"  Erstelle Collection '{collection_id}'...")
        db_service.create_collection(APPWRITE_DB_ID, collection_id, collection_id)
        
        # Create Attributes
        for attr_name, attr_type, size, required in attributes:
            try:
                if attr_type == "string":
                    db_service.create_string_attribute(APPWRITE_DB_ID, collection_id, key=attr_name, size=size, required=required)
                elif attr_type == "boolean":
                    db_service.create_boolean_attribute(APPWRITE_DB_ID, collection_id, key=attr_name, required=required)
                elif attr_type == "datetime":
                    db_service.create_datetime_attribute(APPWRITE_DB_ID, collection_id, key=attr_name, required=required)
                
                # Wait for attribute to be ready (Appwrite needs this before writing data)
                wait_for_attribute(db_service, collection_id, attr_name)
                
            except Exception as e:
                if "Attribute already exists" in str(e):
                    print(f"    ✓ Attribut '{attr_name}' existiert bereits.")
                else:
                    print(f"    ⚠️ Fehler bei Attribut '{attr_name}': {e}")


    # 2. Migrate Data
    cursor = sqlite_conn.cursor()
    # Get columns to map correctly
    cursor.execute(f"PRAGMA table_info({table_name})")
    cols = [c[1] for c in cursor.fetchall()]
    
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    
    count = 0
    for row in rows:
        data = dict(zip(cols, row))
        
        # Prepare data for Appwrite
        doc_data = {}
        for attr_name, attr_type, _, _ in attributes:
            if attr_name in data:
                val = data[attr_name]
                
                # Fix Datetime format
                if val and "datetime" in str(type(val)): 
                    val = val.isoformat()
                
                # Fix Boolean types (SQLite stores 0/1, Appwrite needs True/False)
                if attr_type == "boolean":
                    if val is None:
                        val = False # Default to False if Null
                    else:
                        val = bool(val)

                doc_data[attr_name] = val
        
        # Create Document
        try:
            # Use original ID if possible, else generate new
            doc_id = data.get('id') if data.get('id') else ID.unique()
            # Sanitize ID for Appwrite (max 36 chars, alphanumeric)
            doc_id = doc_id[:36].replace("-", "").replace("_","")
            
            db_service.create_document(
                APPWRITE_DB_ID, collection_id, doc_id, doc_data
            )
            count += 1
            print(f"    Importiere: {doc_id}", end="\r")
        except Exception as e:
            # If exists, update? Or skip.
            print(f"    ⚠️ Fehler bei ID {doc_id}: {e}")

    print(f"  ✓ {count} Dokumente importiert.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Classly Migration Tool")
    parser.add_argument("--migrate-from", default="sqlite", help="Quelle (default: sqlite)")
    parser.add_argument("--migrate-to", default="appwrite", help="Ziel (default: appwrite)")
    parser.add_argument("--db-path", default=DEFAULT_DB_PATH, help="Pfad zur SQLite DB")
    
    args = parser.parse_args()
    
    if args.migrate_from == "sqlite" and args.migrate_to == "appwrite":
        print(f"Modus: SQLite ({args.db_path}) -> Appwrite")
        conn = connect_sqlite(args.db_path)
        db, users = setup_appwrite()
        migrate_to_appwrite(conn, db, users)
    else:
        print(f"❌ Kombination {args.migrate_from} -> {args.migrate_to} wird (noch) nicht unterstützt.")
