"""
栄養計算APIルーター
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from src.database import get_db
from src.services.calendar_service import CalendarService
from src.services.dish_service import DishService


router = APIRouter(prefix="/api/nutrition", tags=["nutrition"])


# 年代・性別別の栄養推奨値
NUTRITION_RECOMMENDATIONS = {
    "30代男性": {"calories": 2650, "protein": 65, "sodium": 7.5},
    "30代女性": {"calories": 2050, "protein": 50, "sodium": 7.0},
    "50代男性": {"calories": 2400, "protein": 60, "sodium": 7.5},
    "50代女性": {"calories": 1850, "protein": 50, "sodium": 7.0},
    "70代男性": {"calories": 2000, "protein": 55, "sodium": 7.0},
    "70代女性": {"calories": 1550, "protein": 45, "sodium": 6.5},
    "80代男性": {"calories": 1800, "protein": 50, "sodium": 7.0},
    "80代女性": {"calories": 1400, "protein": 40, "sodium": 6.0},
}


@router.get("/calculate")
def calculate_nutrition(
    date: str = Query(..., description="日付（ISO 8601形式: YYYY-MM-DD）"),
    target: str = Query("50代男性", description="対象モデル（例: 50代男性）"),
    db: Session = Depends(get_db)
):
    """
    栄養バランスを計算

    - **date**: 日付（ISO 8601形式: YYYY-MM-DD）
    - **target**: 対象モデル（例: 50代男性, 80代女性）
    """
    # 推奨値を取得
    if target not in NUTRITION_RECOMMENDATIONS:
        raise HTTPException(
            status_code=400,
            detail=f"対象モデルが無効です: {target}。有効な値: {', '.join(NUTRITION_RECOMMENDATIONS.keys())}"
        )
    
    recommendations = NUTRITION_RECOMMENDATIONS[target]
    
    # カレンダーサービスで3食を取得
    calendar_service = CalendarService(db)
    calendars = calendar_service.get_by_date_all_meals(date)
    
    if not calendars:
        return {
            "date": date,
            "target": target,
            "recommendations": recommendations,
            "meals": [],
            "total": {"calories": 0, "protein": 0, "sodium": 0},
            "balance": {
                "calories": "0%",
                "protein": "0%",
                "sodium": "0%"
            }
        }
    
    # 各食の栄養を計算
    dish_service = DishService(db)
    meals = []
    total_calories = 0
    total_protein = 0
    total_sodium = 0
    
    for calendar in calendars:
        meal_dict = calendar_service.to_detail_dict(calendar)
        
        # 栄養を計算
        calories = meal_dict.get("nutrition", {}).get("calories", 0)
        protein = meal_dict.get("nutrition", {}).get("protein", 0)
        sodium = meal_dict.get("nutrition", {}).get("sodium", 0)
        
        meals.append({
            "meal_type": meal_dict["meal_type"],
            "calories": calories,
            "protein": protein,
            "sodium": sodium
        })
        
        total_calories += calories
        total_protein += protein
        total_sodium += sodium
    
    # バランスを計算
    calories_percent = (total_calories / recommendations["calories"] * 100) if recommendations["calories"] > 0 else 0
    protein_percent = (total_protein / recommendations["protein"] * 100) if recommendations["protein"] > 0 else 0
    sodium_percent = (total_sodium / recommendations["sodium"] * 100) if recommendations["sodium"] > 0 else 0
    
    # ステータス判定
    def get_status(percent, nutrient_type):
        if nutrient_type == "sodium":
            if percent > 110:
                return "多め"
            elif percent < 80:
                return "少なめ"
            else:
                return "適正"
        else:
            if percent > 110:
                return "多め"
            elif percent < 80:
                return "少なめ"
            else:
                return "適正"
    
    balance = {
        "calories": f"{calories_percent:.1f}% ({get_status(calories_percent, 'calories')})",
        "protein": f"{protein_percent:.1f}% ({get_status(protein_percent, 'protein')})",
        "sodium": f"{sodium_percent:.1f}% ({get_status(sodium_percent, 'sodium')})"
    }
    
    return {
        "date": date,
        "target": target,
        "recommendations": recommendations,
        "meals": meals,
        "total": {
            "calories": round(total_calories, 1),
            "protein": round(total_protein, 1),
            "sodium": round(total_sodium, 1)
        },
        "balance": balance
    }
