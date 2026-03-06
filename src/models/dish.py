"""
献立モデル
"""

from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from src.database import Base


class DishType(str, enum.Enum):
    """献立タイプ"""
    MAIN = "main"      # 主菜
    SIDE = "side"      # 副菜
    SOUP = "soup"      # 汁物


class Difficulty(str, enum.Enum):
    """難易度"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class Dish(Base):
    """献立モデル"""

    __tablename__ = "dishes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    type = Column(Enum(DishType), nullable=False, index=True)
    description = Column(Text, nullable=True)
    difficulty = Column(Enum(Difficulty), nullable=True)
    prep_time = Column(Integer, nullable=True)  # 調理時間（分）

    # 栄養情報（1人前）
    calories = Column(Float, nullable=True)     # カロリー（kcal/1人前）
    protein = Column(Float, nullable=True)      # タンパク質（g/1人前）
    fat = Column(Float, nullable=True)          # 脂質（g/1人前）
    sodium = Column(Float, nullable=True)       # 塩分（g/1人前）

    # レシピ情報
    servings = Column(Integer, nullable=False, default=2)  # 人数（デフォルト2人前）

    # 血栓の病気に良いかどうか
    good_for_brain_health = Column(Boolean, default=False, index=True)

    # タイムスタンプ
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # リレーション
    recipe = relationship("Recipe", back_populates="dish", uselist=False, cascade="all, delete-orphan")
    ingredients = relationship("DishIngredient", back_populates="dish", cascade="all, delete-orphan")
    tags = relationship("DishTag", back_populates="dish", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Dish(id={self.id}, name='{self.name}', type='{self.type}')>"

    def to_dict(self):
        """辞書形式に変換"""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type.value,
            "description": self.description,
            "difficulty": self.difficulty.value if self.difficulty else None,
            "prep_time": self.prep_time,
            "calories": self.calories,
            "protein": self.protein,
            "fat": self.fat,
            "sodium": self.sodium,
            "servings": getattr(self, 'servings', 2),  # デフォルト2人前
            "good_for_brain_health": self.good_for_brain_health,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
