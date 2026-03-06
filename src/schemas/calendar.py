"""
カレンダースキーマ
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class CalendarCreate(BaseModel):
    """カレンダー作成スキーマ"""
    main_dish_id: Optional[int] = Field(None, description="主菜ID")
    side1_dish_id: Optional[int] = Field(None, description="副菜1 ID")
    side2_dish_id: Optional[int] = Field(None, description="副菜2 ID")
    soup_dish_id: Optional[int] = Field(None, description="汁物ID")


class CalendarUpdate(BaseModel):
    """カレンダー更新スキーマ"""
    main_dish_id: Optional[int] = None
    side1_dish_id: Optional[int] = None
    side2_dish_id: Optional[int] = None
    soup_dish_id: Optional[int] = None


class CalendarResponse(BaseModel):
    """カレンダーレスポンススキーマ"""
    id: int
    date: str
    main_dish_id: Optional[int] = None
    side1_dish_id: Optional[int] = None
    side2_dish_id: Optional[int] = None
    soup_dish_id: Optional[int] = None

    class Config:
        from_attributes = True


class CalendarDetailResponse(BaseModel):
    """カレンダー詳細レスポンススキーマ（献立情報付き）"""
    id: int
    date: str
    main: Optional[dict] = None
    side1: Optional[dict] = None
    side2: Optional[dict] = None
    soup: Optional[dict] = None
