"""
レシピモデル
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
import json

from src.database import Base


class Recipe(Base):
    """レシピモデル"""

    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    dish_id = Column(Integer, ForeignKey("dishes.id", ondelete="CASCADE"), nullable=False, unique=True)

    # 調理手順（JSON配列）
    steps = Column(Text, nullable=True)  # JSON文字列で保存

    # コツ・ヒント
    tips = Column(Text, nullable=True)

    # リレーション
    dish = relationship("Dish", back_populates="recipe")

    def __repr__(self):
        return f"<Recipe(id={self.id}, dish_id={self.dish_id})>"

    def get_steps(self):
        """調理手順をリストとして取得"""
        if isinstance(self.steps, str):
            return json.loads(self.steps)
        return self.steps

    def set_steps(self, steps_list):
        """調理手順をJSON文字列として保存"""
        if isinstance(steps_list, list):
            self.steps = json.dumps(steps_list, ensure_ascii=False)
        else:
            self.steps = steps_list

    def to_dict(self):
        """辞書形式に変換"""
        return {
            "id": self.id,
            "dish_id": self.dish_id,
            "steps": self.get_steps(),
            "tips": self.tips
        }
