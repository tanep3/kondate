"""
タグモデル
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from src.database import Base


class Tag(Base):
    """タグモデル"""

    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)

    # リレーション
    dish_tags = relationship("DishTag", back_populates="tag", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Tag(id={self.id}, name='{self.name}')>"

    def to_dict(self):
        """辞書形式に変換"""
        return {
            "id": self.id,
            "name": self.name
        }
