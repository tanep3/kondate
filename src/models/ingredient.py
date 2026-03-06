"""
食材モデル
"""

from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship

from src.database import Base


class Ingredient(Base):
    """食材モデル"""

    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, unique=True, index=True)
    category = Column(String(100), nullable=True, index=True)  # 野菜、肉、魚など
    season = Column(String(50), nullable=True)  # 旬の季節

    # リレーション
    dish_ingredients = relationship("DishIngredient", back_populates="ingredient", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Ingredient(id={self.id}, name='{self.name}', category='{self.category}')>"

    def to_dict(self):
        """辞書形式に変換"""
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "season": self.season
        }
