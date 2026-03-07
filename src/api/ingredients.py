"""
食材APIルーター
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from src.database import get_db
from src.models.ingredient import Ingredient
from src.schemas.dish import IngredientResponse


router = APIRouter(prefix="/api/ingredients", tags=["ingredients"])


@router.get("", response_model=List[IngredientResponse])
def get_ingredients(db: Session = Depends(get_db)):
    """
    全食材を取得
    """
    ingredients = db.query(Ingredient).order_by(Ingredient.name).all()
    return [
        IngredientResponse(
            id=i.id,
            name=i.name,
            unit=i.unit,
            epa=i.epa,
            dha=i.dha
        )
        for i in ingredients
    ]


@router.post("", response_model=IngredientResponse)
def create_ingredient(
    name: str,
    unit: str = None,
    epa: float = None,
    dha: float = None,
    db: Session = Depends(get_db)
):
    """
    食材を作成
    """
    ingredient = Ingredient(
        name=name,
        unit=unit,
        epa=epa,
        dha=dha
    )
    db.add(ingredient)
    db.commit()
    db.refresh(ingredient)

    return IngredientResponse(
        id=ingredient.id,
        name=ingredient.name,
        unit=ingredient.unit,
        epa=ingredient.epa,
        dha=ingredient.dha
    )


@router.put("/{ingredient_id}", response_model=IngredientResponse)
def update_ingredient(
    ingredient_id: int,
    name: str = None,
    unit: str = None,
    epa: float = None,
    dha: float = None,
    db: Session = Depends(get_db)
):
    """
    食材を更新
    """
    ingredient = db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()

    if not ingredient:
        raise HTTPException(status_code=404, detail="食材が見つかりません")

    if name is not None:
        ingredient.name = name
    if unit is not None:
        ingredient.unit = unit
    if epa is not None:
        ingredient.epa = epa
    if dha is not None:
        ingredient.dha = dha

    db.commit()
    db.refresh(ingredient)

    return IngredientResponse(
        id=ingredient.id,
        name=ingredient.name,
        unit=ingredient.unit,
        epa=ingredient.epa,
        dha=ingredient.dha
    )


@router.delete("/{ingredient_id}")
def delete_ingredient(ingredient_id: int, db: Session = Depends(get_db)):
    """
    食材を削除
    """
    ingredient = db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()

    if not ingredient:
        raise HTTPException(status_code=404, detail="食材が見つかりません")

    db.delete(ingredient)
    db.commit()

    return {"message": "食材を削除しました"}
