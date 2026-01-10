import argparse
import sys
import os

# Add parent directory to path so we can import 'app'
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
sys.path.append(os.getcwd()) # For when run from a temp file or via curl

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app import crud, models, core

# Ensure tables exist
Base.metadata.create_all(bind=engine)

def create_initial_class(class_name, user_name, email=None, password=None):
    db = SessionLocal()
    try:
        print(f"Creating class '{class_name}'...")
        
        # Generate token
        token = core.security.generate_join_token()
        while crud.get_class_by_token(db, token):
            token = core.security.generate_join_token()
            
        # Create Class
        new_class = crud.create_class(db, name=class_name, join_token=token)
        print(f"Class created: ID={new_class.id}")
        
        # Create Owner
        print(f"Creating owner '{user_name}'...")
        new_user = crud.create_user(
            db, 
            name=user_name, 
            class_id=new_class.id, 
            role=models.UserRole.OWNER,
            email=email,
            password=password
        )
        
        # Update Class owner
        new_class.owner_id = new_user.id
        db.commit()
        
        print("\n" + "="*50)
        print("SUCCESS! Class setup complete.")
        print("="*50)
        print(f"Class Name: {class_name}")
        print(f"Owner:      {user_name}")
        if email:
            print(f"Email:      {email}")
        print("-" * 50)
        if email and password:
            print("Login with Email/Password at /login")
        else:
            print(f"Login Link (Open this to log in):")
            print(f"https://YOUR-DOMAIN/join/{new_user.session_token}") # We don't know the domain here easily without env or request
            print(f"(Token: {new_user.session_token})")
        print("-" * 50)
        print(f"Invite Link for others:")
        print(f"https://YOUR-DOMAIN/join/{new_class.join_token}")
        print("="*50 + "\n")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pre-configure a Classly class")
    parser.add_argument("--class-name", required=True, help="Name of the class (e.g. 10B)")
    parser.add_argument("--user-name", required=True, help="Name of the owner (e.g. Mr. Smith)")
    parser.add_argument("--email", help="Email for login (optional)")
    parser.add_argument("--password", help="Password for login (optional)")
    
    args = parser.parse_args()
    
    create_initial_class(args.class_name, args.user_name, args.email, args.password)
