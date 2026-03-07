"""
献立スキーマ
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class DishType(str, Enum):
    """献立タイプ"""
    MAIN = "main"
    SIDE = "side"
    SOUP = "soup"
    STAPLE = "staple"
    DESSERT = "dessert"


class Difficulty(str, Enum):
    """難易度"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class DishBase(BaseModel):
    """献立ベーススキーマ"""
    name: str = Field(..., description="献立名")
    type: DishType = Field(..., description="献立タイプ")
    description: Optional[str] = Field(None, description="説明")
    difficulty: Optional[Difficulty] = Field(None, description="難易度")
    prep_time: Optional[int] = Field(None, description="調理時間（分）")
    calories: Optional[float] = Field(None, description="カロリー（kcal/1人前）")
    protein: Optional[float] = Field(None, description="タンパク質（g/1人前）")
    fat: Optional[float] = Field(None, description="脂質（g/1人前）")
    sodium: Optional[float] = Field(None, description="塩分（g/1人前）")
    servings: int = Field(2, description="人数（デフォルト2人前）")
    good_for_brain_health: Optional[bool] = Field(False, description="血栓の病気に良いかどうか")


class DishCreate(DishBase):
    """献立作成スキーマ"""
    recipe: Optional["RecipeCreate"] = None
    ingredients: Optional[List["IngredientCreate"]] = None
    tags: Optional[List[str]] = None  # タグ名のリスト


class DishUpdate(BaseModel):
    """献立更新スキーマ（部分更新）"""
    name: Optional[str] = None
    type: Optional[DishType] = None
    description: Optional[str] = None
    difficulty: Optional[Difficulty] = None
    prep_time: Optional[int] = None
    calories: Optional[float] = None
    protein: Optional[float] = None
    fat: Optional[float] = None
    sodium: Optional[float] = None
    good_for_brain_health: Optional[bool] = None
    recipe: Optional["RecipeUpdate"] = None
    ingredients: Optional[List["IngredientCreate"]] = None
    tags: Optional[List[str]] = None


class IngredientCreate(BaseModel):
    """食材作成スキーマ"""
    name: str
    amount: str


class RecipeCreate(BaseModel):
    """レシピ作成スキーマ"""
    steps: List[str] = Field(..., description="調理手順")
    tips: Optional[str] = Field(None, description="コツ・ヒント")


class RecipeUpdate(BaseModel):
    """レシピ更新スキーマ"""
    steps: Optional[List[str]] = None
    tips: Optional[str] = None


class IngredientResponse(BaseModel):
    """食材レスポンススキーマ（献立-食材関連）"""
    id: int
    dish_id: int
    ingredient_id: int
    amount: str
    ingredient: Optional["IngredientDetailResponse"] = None

    class Config:
        from_attributes = True


class IngredientDetailResponse(BaseModel):
    """食材詳細レスポンススキーマ"""
    id: int
    name: str

    class Config:
        from_attributes = True


class RecipeResponse(BaseModel):
    """レシピレスポンススキーマ"""
    id: int
    dish_id: int
    steps: List[str]
    tips: Optional[str] = None

    class Config:
        from_attributes = True


class TagResponse(BaseModel):
    """タグレスポンススキーマ"""
    id: int
    name: str

    class Config:
        from_attributes = True


class DishResponse(DishBase):
    """献立レスポンススキーマ"""
    id: int
    created_at: datetime
    updated_at: datetime
    recipe: Optional[RecipeResponse] = None
    ingredients: Optional[List[IngredientResponse]] = None
    tags: Optional[List[TagResponse]] = None

    class Config:
        from_attributes = True


class DishListResponse(BaseModel):
    """献立一覧レスポンススキーマ"""
    total: int
    items: List[DishResponse]
