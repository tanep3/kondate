"""
献立-タグ関連モデル
"""

from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from src.database import Base


class DishTag(Base):
    """献立-タグ関連モデル"""

    __tablename__ = "dish_tags"

    id = Column(Integer, primary_key=True, index=True)
    dish_id = Column(Integer, ForeignKey("dishes.id", ondelete="CASCADE"), nullable=False, index=True)
    tag_id = Column(Integer, ForeignKey("tags.id", ondelete="CASCADE"), nullable=False, index=True)

    # リレーション
    dish = relationship("Dish", back_populates="tags")
    tag = relationship("Tag", back_populates="dish_tags")

    def __repr__(self):
        return f"<DishTag(dish_id={self.dish_id}, tag_id={self.tag_id})>"

    def to_dict(self):
        """辞書形式に変換"""
        return {
            "id": self.id,
            "dish_id": self.dish_id,
            "tag_id": self.tag_id,
            "tag": self.tag.to_dict() if self.tag else None
        }
