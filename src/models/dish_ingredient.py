"""
献立-食材関連モデル
"""

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from src.database import Base


class DishIngredient(Base):
    """献立-食材関連モデル"""

    __tablename__ = "dish_ingredients"

    id = Column(Integer, primary_key=True, index=True)
    dish_id = Column(Integer, ForeignKey("dishes.id", ondelete="CASCADE"), nullable=False, index=True)
    ingredient_id = Column(Integer, ForeignKey("ingredients.id", ondelete="CASCADE"), nullable=False, index=True)
    amount = Column(String(100), nullable=False)  # 分量（例: "1/2個", "100g"）

    # リレーション
    dish = relationship("Dish", back_populates="ingredients")
    ingredient = relationship("Ingredient", back_populates="dish_ingredients")

    def __repr__(self):
        return f"<DishIngredient(dish_id={self.dish_id}, ingredient_id={self.ingredient_id}, amount='{self.amount}')>"

    def to_dict(self):
        """辞書形式に変換"""
        return {
            "id": self.id,
            "dish_id": self.dish_id,
            "ingredient_id": self.ingredient_id,
            "amount": self.amount,
            "ingredient": self.ingredient.to_dict() if self.ingredient else None
        }
