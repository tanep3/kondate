"""
カレンダーモデル
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship
import enum

from src.database import Base


class MealType(str, enum.Enum):
    """食事タイプ"""
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"


class Calendar(Base):
    """カレンダーモデル"""

    __tablename__ = "calendar"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(String(10), nullable=False, index=True)  # ISO 8601形式 (YYYY-MM-DD)
    meal_type = Column(String(10), nullable=False, default=MealType.DINNER, index=True)  # 食事タイプ

    # 献立ID（外部キー）
    main_dish_id = Column(Integer, ForeignKey("dishes.id", ondelete="SET NULL"), nullable=True)
    side1_dish_id = Column(Integer, ForeignKey("dishes.id", ondelete="SET NULL"), nullable=True)
    side2_dish_id = Column(Integer, ForeignKey("dishes.id", ondelete="SET NULL"), nullable=True)
    soup_dish_id = Column(Integer, ForeignKey("dishes.id", ondelete="SET NULL"), nullable=True)
    staple_dish_id = Column(Integer, ForeignKey("dishes.id", ondelete="SET NULL"), nullable=True)  # 主食
    dessert_dish_id = Column(Integer, ForeignKey("dishes.id", ondelete="SET NULL"), nullable=True)  # デザート

    def __repr__(self):
        return f"<Calendar(id={self.id}, date='{self.date}', meal_type='{self.meal_type}')>"

    def to_dict(self):
        """辞書形式に変換"""
        return {
            "id": self.id,
            "date": self.date,
            "meal_type": self.meal_type,
            "main_dish_id": self.main_dish_id,
            "side1_dish_id": self.side1_dish_id,
            "side2_dish_id": self.side2_dish_id,
            "soup_dish_id": self.soup_dish_id,
            "staple_dish_id": self.staple_dish_id,
            "dessert_dish_id": self.dessert_dish_id
        }
