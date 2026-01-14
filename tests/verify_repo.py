import sys
import os
sys.path.append(os.getcwd())
from app.repository.factory import get_repository
from app.repository.sql import SqlAlchemyRepository
from app.repository.appwrite import AppwriteRepository
from app import models

def test_repo_factory():
    print("Testing Factory...")
    # Default (SQL)
    if "APPWRITE" in os.environ: del os.environ["APPWRITE"]
    repo_gen = get_repository()
    repo = next(repo_gen)
    assert isinstance(repo, SqlAlchemyRepository)
    print("SQL Factory OK")

    # Appwrite
    os.environ["APPWRITE"] = "true"
    repo_gen = get_repository()
    repo = next(repo_gen)
    assert isinstance(repo, AppwriteRepository)
    print("Appwrite Factory OK")

def verify_repo_methods():
    print("Verifying Repo Methods exist...")
    # Check if AppwriteRepo has all methods from Base
    import inspect
    from app.repository.base import BaseRepository
    
    base_methods = {x[0] for x in inspect.getmembers(BaseRepository, predicate=inspect.isfunction) if not x[0].startswith("_")}
    appwrite_methods = {x[0] for x in inspect.getmembers(AppwriteRepository, predicate=inspect.isfunction) if not x[0].startswith("_")}
    
    missing = base_methods - appwrite_methods
    if missing:
        print(f"AppwriteRepo MISSING: {missing}")
    else:
        print("AppwriteRepo implements all methods.")

    sql_methods = {x[0] for x in inspect.getmembers(SqlAlchemyRepository, predicate=inspect.isfunction) if not x[0].startswith("_")}
    missing_sql = base_methods - sql_methods
    if missing_sql:
         print(f"SqlRepo MISSING: {missing_sql}")
    else:
         print("SqlRepo implements all methods.")

if __name__ == "__main__":
    try:
        test_repo_factory()
        verify_repo_methods()
        print("Verification Complete!")
    except Exception as e:
        print(f"Verification FAILED: {e}")
        exit(1)
