"""
提案APIルーター
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from src.database import get_db
from src.services.suggest_service import SuggestService


router = APIRouter(prefix="/api/suggest", tags=["suggest"])


@router.get("")
def suggest_menu(
    prefer: Optional[str] = Query(None, description="優先条件（healthy, brainなど）"),
    max_sodium: Optional[float] = Query(None, description="塩分上限（g）"),
    db: Session = Depends(get_db)
):
    """
    献立を提案

    - **prefer**: 優先条件（healthy: 健康的なもの優先, brain: 血栓の病気に良いもの優先）
    - **max_sodium**: 塩分上限（g）

    主菜 + 副菜2 + 汁物 の組み合わせを提案します。
    """
    service = SuggestService(db)
    menu = service.suggest_menu(prefer=prefer, max_sodium=max_sodium)

    return {
        "success": True,
        "data": menu
    }
