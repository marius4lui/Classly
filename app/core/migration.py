import os
import sys
import sqlite3
import time
import secrets
import warnings
from datetime import datetime
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.services.users import Users
from appwrite.id import ID
from appwrite.query import Query
from appwrite.exception import AppwriteException

# Suppress DeprecationWarnings from Appwrite SDK
warnings.filterwarnings("ignore", category=DeprecationWarning)

DEFAULT_DB_PATH = "./classly.db"

def connect_sqlite(db_path):
    if not os.path.exists(db_path):
        print(f"❌ SQLite Datenbank nicht gefunden unter: {db_path}")
        return None
    return sqlite3.connect(db_path)

def setup_appwrite():
    endpoint = os.getenv("APPWRITE_ENDPOINT", "https://cloud.appwrite.io/v1")
    project_id = os.getenv("APPWRITE_PROJECT_ID")
    api_key = os.getenv("APPWRITE_API_KEY")
    
    if not project_id or not api_key:
        print("❌ Bitte setze APPWRITE_PROJECT_ID und APPWRITE_API_KEY Environment Variablen.")
        return None, None
    
    client = Client()
    client.set_endpoint(endpoint)
    client.set_project(project_id)
    client.set_key(api_key)
    
    return Databases(client), Users(client)

def wait_for_attribute(db_service, database_id, collection_id, key):
    """Polls attribute status until it is 'available'."""
    print(f"    ⏳ Warte auf Attribut '{key}'...", end="", flush=True)
    for _ in range(30):
        try:
            attr = db_service.get_attribute(database_id, collection_id, key)
            if attr['status'] == 'available':
                print(" ✅")
                return
        except:
            pass
        time.sleep(2)
        print(".", end="", flush=True)
    print(" ⚠️ (Timeout, mache weiter)")

def migrate_users_to_auth(sqlite_conn, users_service):
    cursor = sqlite_conn.cursor()
    try:
        cursor.execute("SELECT * FROM users")
    except sqlite3.OperationalError:
        print("⚠️ Tabelle 'users' nicht gefunden.")
        return

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
        
        # Random Password
        password = secrets.token_urlsafe(16)
        
        # Attributes to Prefs
        prefs = {}
        for key in ['role', 'class_id', 'is_registered', 'language']:
            if key in user_data and user_data[key] is not None:
                val = user_data[key]
                if isinstance(val, int) and (key == 'is_registered'): 
                    val = bool(val)
                prefs[key] = val
        
        try:
            # Check if user exists
            try:
                users_service.get(uid)
                # Update prefs
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
            # print(f"    + User '{user_data.get('name')}' angelegt.", end="\r")
            
        except Exception as e:
            print(f"    ⚠️ Fehler bei User {uid}: {e}")
            
    print(f"  ✓ {count} Benutzer in Auth migriert.")

def migrate_table(sqlite_conn, db_service, database_id, table_name, collection_id, attributes):
    # 1. Create Collection if not exists
    try:
        db_service.get_collection(database_id, collection_id)
        # print(f"  ✓ Collection '{collection_id}' existiert.")
    except:
        print(f"  Erstelle Collection '{collection_id}'...")
        try:
            db_service.create_collection(database_id, collection_id, collection_id)
        except Exception as e:
            print(f"Error creating collection {collection_id}: {e}")
            return

        # Create Attributes
        for attr_name, attr_type, size, required in attributes:
            try:
                if attr_type == "string":
                    db_service.create_string_attribute(database_id, collection_id, key=attr_name, size=size, required=required)
                elif attr_type == "boolean":
                    db_service.create_boolean_attribute(database_id, collection_id, key=attr_name, required=required)
                elif attr_type == "datetime":
                    db_service.create_datetime_attribute(database_id, collection_id, key=attr_name, required=required)
                
                # Wait for attribute to be ready
                # wait_for_attribute(db_service, database_id, collection_id, attr_name)
                # Optimization: Don't wait individually if possible? Appwrite requires it.
                # We will wait.
                
            except Exception as e:
                # if "Attribute already exists" in str(e): pass
                pass
        
        # Wait loop for all attributes together? No, create is async.
        # We must wait for each before proceeding to data insertion?
        # Actually, we can wait for all at end of schema creation.
        
        print("Waiting for attributes...")
        time.sleep(5) # Heuristic wait

    # 2. Migrate Data
    cursor = sqlite_conn.cursor()
    try:
        cursor.execute(f"PRAGMA table_info({table_name})")
        cols = [c[1] for c in cursor.fetchall()]
        if not cols:
            print(f"⚠️ Tabelle '{table_name}' leer oder nicht gefunden.")
            return

        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
    except Exception as e:
        print(f"Table error: {e}")
        return
    
    count = 0
    for row in rows:
        data = dict(zip(cols, row))
        
        # Prepare data for Appwrite
        doc_data = {}
        for attr_name, attr_type, _, _ in attributes:
            val = data.get(attr_name)
            
            # Fix Datetime format
            if val and "datetime" in str(type(val)): 
                val = val.isoformat()
            
            # Fix Boolean types
            if attr_type == "boolean":
                if val is None:
                    val = False 
                else:
                    val = bool(val)

            doc_data[attr_name] = val
        
        # Create Document
        try:
            doc_id = data.get('id') if data.get('id') else ID.unique()
            doc_id = doc_id[:36].replace("-", "").replace("_","")
            
            try:
                db_service.create_document(
                    database_id, collection_id, doc_id, doc_data
                )
                count += 1
            except AppwriteException as ae:
                if ae.code == 409: # Conflict / Exists
                    # Update?
                    pass
                else:
                    print(f"    ⚠️ Fehler bei ID {doc_id}: {ae}")

        except Exception as e:
             print(f"    ⚠️ Fehler bei ID {doc_id}: {e}")

    print(f"  ✓ {count} Dokumente in {collection_id} importiert.")

def migrate_to_appwrite():
    print("🚀 Auto-Migration zu Appwrite initialisiert...")
    
    appwrite_db_id = os.getenv("APPWRITE_DATABASE_ID", "classly_db")
    
    conn = connect_sqlite(DEFAULT_DB_PATH)
    if not conn:
        print("Migration abgebrochen: SQLite DB fehlt.")
        return

    db_service, users_service = setup_appwrite()
    if not db_service:
        return

    # Check/Create Database
    try:
        db_service.get(appwrite_db_id)
        print(f"✓ Datenbank '{appwrite_db_id}' gefunden.")
    except:
        print(f"Erstelle Datenbank '{appwrite_db_id}'...")
        try:
            db_service.create(appwrite_db_id, appwrite_db_id)
        except Exception as e:
            print(f"DB creation failed: {e}")
            return

    # --- Classes ---
    print("\n📦 Migriere Klassen...")
    migrate_table(
        conn, db_service, appwrite_db_id,
        table_name="classes", 
        collection_id="classes",
        attributes=[
            ("name", "string", 255, True),
            ("owner_id", "string", 255, True),
            ("join_token", "string", 255, False),
            ("join_enabled", "boolean", 0, False),
        ]
    )

    # --- Users ---
    print("\n👤 Migriere Benutzer...")
    migrate_users_to_auth(conn, users_service)

    # --- Events ---
    print("\n📅 Migriere Events...")
    migrate_table(
        conn, db_service, appwrite_db_id,
        table_name="events",
        collection_id="events",
        attributes=[
            ("title", "string", 255, False),
            ("class_id", "string", 255, True),
            ("type", "string", 50, True),
            ("priority", "string", 50, False),
            ("date", "datetime", 0, False),
            ("author_id", "string", 255, True),
            ("subject_name", "string", 255, False), 
            # Note: Subject Name is useful if subjects not fully migrated or linked yet
        ]
    )
    
     # --- Login Tokens ---
    print("\n🔑 Migriere Login Tokens...")
    migrate_table(
        conn, db_service, appwrite_db_id,
        table_name="login_tokens",
        collection_id="login_tokens",
        attributes=[
             ("class_id", "string", 255, True),
             ("token", "string", 255, True),
             ("user_id", "string", 255, False),
             ("user_name", "string", 255, False),
             ("role", "string", 50, True),
             ("created_by", "string", 255, True),
        ]
    )

    print("\n✅ Migration abgeschlossen!")
    conn.close()
