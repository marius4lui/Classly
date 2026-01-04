import os
import bcrypt
from app import models
from icalendar import Calendar, Event
import datetime

RADICALE_DIR = os.getenv("RADICALE_DIR", "/radicale-data")
USERS_FILE = os.path.join(RADICALE_DIR, "users")
COLLECTIONS_DIR = os.path.join(RADICALE_DIR, "collections")

def setup_radicale():
    """Ensure directories exist"""
    os.makedirs(RADICALE_DIR, exist_ok=True)
    os.makedirs(COLLECTIONS_DIR, exist_ok=True)
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w") as f:
            f.write("")

def get_radicale_username(user: models.User) -> str:
    """Get unique username for Radicale (email or fallback)"""
    return user.email if user.email else f"{user.id}@classly.local"

def update_radicale_user(user: models.User, password_plain: str):
    """Update or add user to htpasswd file for Radicale"""
    setup_radicale()
    username = get_radicale_username(user)
    
    # Use bcrypt for password
    hashed = bcrypt.hashpw(password_plain.encode('utf-8'), bcrypt.gensalt(rounds=10)).decode('utf-8')
    entry = f"{username}:{hashed}\n"
    
    lines = []
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            lines = f.readlines()
            
    # Remove existing entry for this user
    lines = [l for l in lines if not l.startswith(f"{username}:")]
    lines.append(entry)
    
    with open(USERS_FILE, "w") as f:
        f.writelines(lines)
        
    # Create user directory structure
    # Collection: /collections/{username}/calendar/
    user_cal_dir = os.path.join(COLLECTIONS_DIR, "collection-root", username, "calendar")
    os.makedirs(user_cal_dir, exist_ok=True)
    
    # Create .Radicale.props for the calendar
    props_file = os.path.join(user_cal_dir, ".Radicale.props")
    if not os.path.exists(props_file):
        with open(props_file, "w") as f:
            f.write('{"D:displayname": "Classly Calendar", "tag": "VCALENDAR"}')

def sync_event_to_radicale(event: models.Event, users: list[models.User]):
    """Write event to all users' Radicale folders who are in the same class"""
    for user in users:
        username = get_radicale_username(user)
        # Check if user has initialized CalDAV (has directory)
        user_cal_dir = os.path.join(COLLECTIONS_DIR, "collection-root", username, "calendar")
        if not os.path.exists(user_cal_dir):
            continue

        # Create ICS
        cal = Calendar()
        cal.add('prodid', '-//Classly//Calendar//DE')
        cal.add('version', '2.0')
        
        ev = Event()
        ev.add('uid', f'{event.id}@classly')
        ev.add('summary', f'{event.type.value}: {event.subject_name or event.title or "Event"}')
        ev.add('dtstart', event.date.date())
        ev.add('dtend', event.date.date() + datetime.timedelta(days=1))
        if event.title:
            ev.add('description', event.title)
        
        cal.add_component(ev)
        
        # Write file
        filename = f"{event.id}.ics"
        with open(os.path.join(user_cal_dir, filename), 'wb') as f:
            f.write(cal.to_ical())

def delete_event_from_radicale(event_id: str, users: list[models.User]):
    """Remove .ics file"""
    for user in users:
        username = get_radicale_username(user)
        user_cal_dir = os.path.join(COLLECTIONS_DIR, "collection-root", username, "calendar")
        filepath = os.path.join(user_cal_dir, f"{event_id}.ics")
        if os.path.exists(filepath):
            os.remove(filepath)
