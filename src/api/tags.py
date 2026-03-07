"""
タグAPIルーター
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from src.database import get_db
from src.models.tag import Tag


router = APIRouter(prefix="/api/tags", tags=["tags"])


class TagResponse(BaseModel):
    id: int
    name: str
    color: str

    class Config:
        from_attributes = True


@router.get("", response_model=List[TagResponse])
def get_tags(db: Session = Depends(get_db)):
    """
    全タグを取得
    """
    tags = db.query(Tag).order_by(Tag.name).all()
    return tags


@router.post("", response_model=TagResponse)
def create_tag(
    name: str,
    color: str = "#007bff",
    db: Session = Depends(get_db)
):
    """
    タグを作成
    """
    tag = Tag(
        name=name,
        color=color
    )
    db.add(tag)
    db.commit()
    db.refresh(tag)

    return tag


@router.put("/{tag_id}", response_model=TagResponse)
def update_tag(
    tag_id: int,
    name: str = None,
    color: str = None,
    db: Session = Depends(get_db)
):
    """
    タグを更新
    """
    tag = db.query(Tag).filter(Tag.id == tag_id).first()

    if not tag:
        raise HTTPException(status_code=404, detail="タグが見つかりません")

    if name is not None:
        tag.name = name
    if color is not None:
        tag.color = color

    db.commit()
    db.refresh(tag)

    return tag


@router.delete("/{tag_id}")
def delete_tag(tag_id: int, db: Session = Depends(get_db)):
    """
    タグを削除
    """
    tag = db.query(Tag).filter(Tag.id == tag_id).first()

    if not tag:
        raise HTTPException(status_code=404, detail="タグが見つかりません")

    db.delete(tag)
    db.commit()

    return {"message": "タグを削除しました"}
