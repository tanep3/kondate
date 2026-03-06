"""
検索APIルーター
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from src.database import get_db
from src.services.search_service import SearchService
from src.schemas.dish import DishResponse


router = APIRouter(prefix="/api/search", tags=["search"])


@router.get("/dishes")
def search_dishes(
    q: str = Query(..., description="検索クエリ"),
    type: str = Query(None, description="献立タイプでフィルタ"),
    good_for_brain_health: bool = Query(None, description="血栓の病気に良いかでフィルタ"),
    db: Session = Depends(get_db)
):
    """
    献立名で検索
    """
    # TODO: 今回はChromaDB検索に流用
    service = SearchService(db)
    results = service.search_by_ingredients(q, n_results=50, dish_type=type, good_for_brain_health=good_for_brain_health)

    items = []
    for dish, similarity in results:
        dish_dict = dish.to_dict()
        dish_dict["similarity"] = round(similarity, 3)
        items.append(dish_dict)

    return {"query": q, "total": len(items), "items": items}


@router.get("/ingredients")
def search_by_ingredients(
    q: str = Query(..., description="食材クエリ"),
    n: int = Query(50, ge=1, le=50, description="返却数"),
    type: str = Query(None, description="献立タイプでフィルタ"),
    db: Session = Depends(get_db)
):
    """
    食材から献立を検索（ChromaDB）

    - **q**: 食材クエリ（例: "キャベツ 卵"）
    - **n**: 返却数（最大50）
    - **type**: 献立タイプ（main, side, soup）
    """
    service = SearchService(db)
    results = service.search_by_ingredients(q, n_results=n, dish_type=type)

    items = []
    for dish, similarity in results:
        dish_dict = dish.to_dict()
        items.append({
            "dish": dish_dict,
            "similarity": round(similarity, 3)
        })

    return {"query": q, "results": items}


@router.get("/similar")
def search_similar(
    id: int = Query(..., description="基準献立ID"),
    n: int = Query(5, ge=1, le=20, description="返却数"),
    db: Session = Depends(get_db)
):
    """
    類似献立を検索

    - **id**: 基準献立ID
    - **n**: 返却数（最大20）
    """
    service = SearchService(db)
    results = service.search_similar(id, n_results=n)

    items = []
    for dish, similarity in results:
        dish_dict = dish.to_dict()
        items.append({
            "dish": dish_dict,
            "similarity": round(similarity, 3)
        })

    return {"base_dish_id": id, "results": items}
