"""
データベース接続管理
SQLite3を使用
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# データベースURL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./src/datas/database.db"
)

# エンジン作成
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # SQLiteの場合必要
)

# セッションローカルイベント
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ベースクラス
Base = declarative_base()


def get_db():
    """
    データベースセッションを取得する依存性注入関数
    FastAPIのDependsで使用
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    データベースを初期化する
    テーブルを作成
    """
    # データディレクトリが存在するか確認
    db_dir = os.path.dirname(DATABASE_URL.replace("sqlite:///", ""))
    if not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)

    # テーブル作成
    from src.models import dish, recipe, ingredient, tag, calendar
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully")
