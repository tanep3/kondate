"""
カレンダースキーマ
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date


class CalendarDishItem(BaseModel):
    """カレンダー献立アイテム"""
    dish_id: int = Field(..., description="献立ID")


class CalendarCreate(BaseModel):
    """カレンダー作成スキーマ"""
    date: str = Field(..., description="日付（ISO 8601形式: YYYY-MM-DD）")
    meal_type: str = Field("dinner", description="食事タイプ（breakfast, lunch, dinner）")
    dishes: List[CalendarDishItem] = Field(default_factory=list, description="献立リスト")
    main_dish_id: Optional[int] = Field(None, description="主菜ID（非推奨、dishesを使用）")
    side1_dish_id: Optional[int] = Field(None, description="副菜1 ID（非推奨、dishesを使用）")
    side2_dish_id: Optional[int] = Field(None, description="副菜2 ID（非推奨、dishesを使用）")
    soup_dish_id: Optional[int] = Field(None, description="汁物ID（非推奨、dishesを使用）")
    staple_dish_id: Optional[int] = Field(None, description="主食ID（非推奨、dishesを使用）")
    dessert_dish_id: Optional[int] = Field(None, description="デザートID（非推奨、dishesを使用）")


class CalendarUpdate(BaseModel):
    """カレンダー更新スキーマ"""
    date: Optional[str] = None
    meal_type: Optional[str] = None
    dishes: Optional[List[CalendarDishItem]] = Field(default_factory=list, description="献立リスト")
    main_dish_id: Optional[int] = None
    side1_dish_id: Optional[int] = None
    side2_dish_id: Optional[int] = None
    soup_dish_id: Optional[int] = None
    staple_dish_id: Optional[int] = None
    dessert_dish_id: Optional[int] = None


class CalendarResponse(BaseModel):
    """カレンダーレスポンススキーマ"""
    id: int
    date: str
    meal_type: str
    main_dish_id: Optional[int] = None
    side1_dish_id: Optional[int] = None
    side2_dish_id: Optional[int] = None
    soup_dish_id: Optional[int] = None
    staple_dish_id: Optional[int] = None
    dessert_dish_id: Optional[int] = None

    class Config:
        from_attributes = True


class CalendarDetailResponse(BaseModel):
    """カレンダー詳細レスポンススキーマ（献立情報付き）"""
    id: int
    date: str
    meal_type: str
    main: Optional[dict] = None
    side: Optional[dict] = None
    side2: Optional[dict] = None
    soup: Optional[dict] = None
    staple: Optional[dict] = None
    dessert: Optional[dict] = None
    nutrition: Optional[dict] = None
