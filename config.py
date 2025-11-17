import os
from pathlib import Path

basedir = Path(__file__).resolve().parent

class Config:
    # Use DATABASE_URL env var if present, otherwise SQLite file in project root
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{basedir / 'expenses.db'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
