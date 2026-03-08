#!/usr/bin/env python3
"""
初期化スクリプト
"""
from src.database import engine, Base
from src.models import *  # noqa: F401,F403

if __name__ == "__main__":
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")
