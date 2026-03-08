"""
献立APIルーター
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from src.database import get_db
from src.services.dish_service import DishService
from src.schemas.dish import (
    DishCreate,
    DishUpdate,
    DishResponse,
    DishListResponse
)

router = APIRouter(prefix="/api/dishes", tags=["dishes"])


@router.get("", response_model=DishListResponse)
def get_dishes(
    skip: int = Query(0, ge=0, description="スキップ数"),
    limit: int = Query(50, ge=1, le=100, description="取得上限"),
    type: Optional[str] = Query(None, description="献立タイプでフィルタ"),
    good_for_brain_health: Optional[bool] = Query(None, description="血栓の病気に良いかでフィルタ"),
    db: Session = Depends(get_db)
):
    """
    献立一覧を取得

    - **skip**: スキップ数（ページネーション用）
    - **limit**: 取得上限（最大100）
    - **type**: 献立タイプ（main, side, soup）
    - **good_for_brain_health**: 血栓の病気に良いかどうか
    """
    service = DishService(db)
    dishes, total = service.get_all(
        skip=skip,
        limit=limit,
        dish_type=type,
        good_for_brain_health=good_for_brain_health
    )

    # レスポンス形式に変換
    items = []
    for dish in dishes:
        dish_dict = dish.to_dict()
        # レシピを追加
        if dish.recipe:
            dish_dict["recipe"] = dish.recipe.to_dict()
        # 食材を追加
        if dish.ingredients:
            dish_dict["ingredients"] = [di.to_dict() for di in dish.ingredients]
        # タグを追加
        if dish.tags:
            dish_dict["tags"] = [dt.tag.to_dict() for dt in dish.tags]
        items.append(DishResponse(**dish_dict))

    return DishListResponse(total=total, items=items)


@router.get("/{dish_id}", response_model=DishResponse)
def get_dish(
    dish_id: int,
    db: Session = Depends(get_db)
):
    """
    献立詳細を取得

    - **dish_id**: 献立ID
    """
    service = DishService(db)
    dish = service.get_by_id(dish_id)

    if not dish:
        raise HTTPException(status_code=404, detail="献立が見つかりません")

    dish_dict = dish.to_dict()
    if dish.recipe:
        dish_dict["recipe"] = dish.recipe.to_dict()
    if dish.ingredients:
        dish_dict["ingredients"] = [di.to_dict() for di in dish.ingredients]
    if dish.tags:
        dish_dict["tags"] = [dt.tag.to_dict() for dt in dish.tags]

    return DishResponse(**dish_dict)


@router.post("", response_model=DishResponse, status_code=201)
def create_dish(
    dish_data: DishCreate,
    db: Session = Depends(get_db)
):
    """
    献立を作成

    - **name**: 献立名（必須）
    - **type**: 献立タイプ（必須: main, side, soup）
    - **description**: 説明
    - **difficulty**: 難易度（easy, medium, hard）
    - **prep_time**: 調理時間（分）
    - **calories**: カロリー（kcal/人前）
    - **protein**: タンパク質（g/人前）
    - **fat**: 脂質（g/人前）
    - **sodium**: 塩分（g/人前）
    - **good_for_brain_health**: 血栓の病気に良いかどうか
    - **recipe**: レシピ（steps, tips）
    - **ingredients**: 食材リスト（name, amount）
    - **tags**: タグリスト（タグ名の文字列リスト）
    """
    service = DishService(db)
    dish = service.create(dish_data)

    dish_dict = dish.to_dict()
    if dish.recipe:
        dish_dict["recipe"] = dish.recipe.to_dict()
    if dish.ingredients:
        dish_dict["ingredients"] = [di.to_dict() for di in dish.ingredients]
    if dish.tags:
        dish_dict["tags"] = [dt.tag.to_dict() for dt in dish.tags]

    return DishResponse(**dish_dict)


@router.put("/{dish_id}", response_model=DishResponse)
def update_dish(
    dish_id: int,
    dish_data: DishUpdate,
    db: Session = Depends(get_db)
):
    """
    献立を更新

    全フィールドがオプションです。指定したフィールドのみ更新されます。
    """
    service = DishService(db)
    dish = service.update(dish_id, dish_data)

    if not dish:
        raise HTTPException(status_code=404, detail="献立が見つかりません")

    dish_dict = dish.to_dict()
    if dish.recipe:
        dish_dict["recipe"] = dish.recipe.to_dict()
    if dish.ingredients:
        dish_dict["ingredients"] = [di.to_dict() for di in dish.ingredients]
    if dish.tags:
        dish_dict["tags"] = [dt.tag.to_dict() for dt in dish.tags]

    return DishResponse(**dish_dict)


@router.delete("/{dish_id}", status_code=204)
def delete_dish(
    dish_id: int,
    db: Session = Depends(get_db)
):
    """
    献立を削除
    """
    service = DishService(db)
    success = service.delete(dish_id)

    if not success:
        raise HTTPException(status_code=404, detail="献立が見つかりません")

    return None


@router.post("/bulk", response_model=dict)
def create_dishes_bulk(
    dishes_data: dict,
    db: Session = Depends(get_db)
):
    """
    献立を一括作成

    - **dishes**: 献立リスト（最大5000件）
    """
    if "dishes" not in dishes_data:
        raise HTTPException(status_code=400, detail="dishesフィールドが必須です")
    
    dishes_list = dishes_data["dishes"]
    
    if len(dishes_list) > 5000:
        raise HTTPException(status_code=400, detail="最大5000件まで登録できます")
    
    service = DishService(db)
    created_dishes = []
    failed_dishes = []
    
    for i, dish_data in enumerate(dishes_list):
        try:
            # dictをDishCreateに変換
            dish_create = DishCreate(**dish_data)
            dish = service.create(dish_create)
            
            dish_dict = dish.to_dict()
            if dish.recipe:
                dish_dict["recipe"] = dish.recipe.to_dict()
            if dish.ingredients:
                dish_dict["ingredients"] = [di.to_dict() for di in dish.ingredients]
            if dish.tags:
                dish_dict["tags"] = [dt.tag.to_dict() for dt in dish.tags]
            
            created_dishes.append({
                "index": i,
                "dish_id": dish.id,
                "name": dish.name,
                "type": dish.type
            })
        except Exception as e:
            failed_dishes.append({
                "index": i,
                "name": dish_data.get("name", "Unknown"),
                "error": str(e)
            })
    
    return {
        "total": len(dishes_list),
        "created": len(created_dishes),
        "failed": len(failed_dishes),
        "created_dishes": created_dishes,
        "failed_dishes": failed_dishes
    }
