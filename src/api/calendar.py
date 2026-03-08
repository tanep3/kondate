"""
カレンダーAPIルーター
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from src.database import get_db
from src.services.calendar_service import CalendarService
from src.schemas.calendar import CalendarCreate, CalendarUpdate, CalendarResponse, CalendarDetailResponse


router = APIRouter(prefix="/api/calendar", tags=["calendar"])


@router.get("")
def get_calendar(
    start: Optional[str] = Query(None, description="開始日（ISO 8601）"),
    end: Optional[str] = Query(None, description="終了日（ISO 8601）"),
    year: Optional[int] = Query(None, description="年"),
    month: Optional[int] = Query(None, description="月"),
    date: Optional[str] = Query(None, description="日付（ISO 8601）"),
    db: Session = Depends(get_db)
):
    """
    カレンダーを取得

    - **start**: 開始日（指定しない場合は今日）
    - **end**: 終了日（指定しない場合は7日後）
    - **year**: 年（指定すると月間カレンダーを返す）
    - **month**: 月（指定すると月間カレンダーを返す）
    - **date**: 日付（指定するとその日の3食を返す）
    """
    service = CalendarService(db)

    # 特定の日付の3食を取得
    if date:
        calendars = service.get_by_date_all_meals(date)
        items = [service.to_detail_dict(c) for c in calendars]
        
        # 3食の総栄養データを計算
        total_calories = sum(item.get("nutrition", {}).get("calories", 0) for item in items)
        total_protein = sum(item.get("nutrition", {}).get("protein", 0) for item in items)
        total_sodium = sum(item.get("nutrition", {}).get("sodium", 0) for item in items)
        
        return {
            "date": date,
            "meals": items,
            "total_nutrition": {
                "calories": round(total_calories, 1),
                "protein": round(total_protein, 1),
                "sodium": round(total_sodium, 1)
            }
        }

    # 月間カレンダー
    if year and month:
        from datetime import datetime, timedelta
        import calendar
        
        start = f"{year}-{month:02d}-01"
        last_day = calendar.monthrange(year, month)[1]
        end = f"{year}-{month:02d}-{last_day:02d}"

    # デフォルト値設定（startとendが指定されていない場合のみ）
    else:
        from datetime import datetime, timedelta
        if not start:
            start = (datetime.now() + timedelta(hours=9)).strftime("%Y-%m-%d")  # JST
        if not end:
            end = (datetime.now() + timedelta(days=7, hours=9)).strftime("%Y-%m-%d")  # JST

    calendars = service.get_by_date_range(start, end)

    items = []
    for calendar in calendars:
        items.append(service.to_detail_dict(calendar))

    return {"start": start, "end": end, "items": items}


@router.post("", status_code=201)
def create_calendar(
    data: CalendarCreate,
    db: Session = Depends(get_db)
):
    """
    カレンダーを作成

    - **date**: 日付（ISO 8601形式: YYYY-MM-DD）
    - **meal_type**: 食事タイプ（breakfast, lunch, dinner）
    - **dishes**: 献立リスト（dish_idのペア）
    """
    service = CalendarService(db)

    # 既存チェック
    existing = service.get_by_date(data.date, data.meal_type)
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"{data.date}の{data.meal_type}は既に登録されています。更新するにはPUTメソッドを使用してください。"
        )

    calendar = service.create(data.date, data)
    return service.to_detail_dict(calendar)


@router.get("/{date}")
def get_calendar_by_date(
    date: str,
    db: Session = Depends(get_db)
):
    """
    日付でカレンダーを取得（3食）

    - **date**: 日付（ISO 8601形式: YYYY-MM-DD）
    """
    service = CalendarService(db)
    calendars = service.get_by_date_all_meals(date)

    items = [service.to_detail_dict(c) for c in calendars]
    
    # 3食の総栄養データを計算
    total_calories = sum(item.get("nutrition", {}).get("calories", 0) for item in items)
    total_protein = sum(item.get("nutrition", {}).get("protein", 0) for item in items)
    total_sodium = sum(item.get("nutrition", {}).get("sodium", 0) for item in items)
    
    return {
        "date": date,
        "meals": items,
        "total_nutrition": {
            "calories": round(total_calories, 1),
            "protein": round(total_protein, 1),
            "sodium": round(total_sodium, 1)
        }
    }


@router.post("/{date}")
def create_calendar_by_date(
    date: str,
    data: CalendarCreate,
    db: Session = Depends(get_db)
):
    """
    カレンダーを作成

    - **date**: 日付（ISO 8601形式: YYYY-MM-DD）
    - **meal_type**: 食事タイプ（breakfast, lunch, dinner）
    - **dishes**: 献立リスト
    """
    service = CalendarService(db)

    # 既存チェック
    existing = service.get_by_date(date, data.meal_type)
    if existing:
        raise HTTPException(status_code=400, detail="既に登録されています")

    calendar = service.create(date, data)
    return service.to_detail_dict(calendar)


@router.put("/{date}")
def update_calendar(
    date: str,
    data: CalendarUpdate,
    meal_type: str = Query("dinner", description="食事タイプ"),
    db: Session = Depends(get_db)
):
    """
    カレンダーを更新

    全フィールドがオプションです。指定したフィールドのみ更新されます。
    """
    service = CalendarService(db)
    
    # meal_typeをdataから取得
    if data.meal_type:
        meal_type = data.meal_type
    
    calendar = service.update(date, meal_type, data)

    if not calendar:
        raise HTTPException(status_code=404, detail="カレンダーが見つかりません")

    return service.to_detail_dict(calendar)


@router.delete("/{date}")
def delete_calendar(
    date: str,
    meal_type: str = Query("dinner", description="食事タイプ"),
    db: Session = Depends(get_db)
):
    """
    カレンダーを削除
    """
    service = CalendarService(db)
    success = service.delete(date, meal_type)

    if not success:
        raise HTTPException(status_code=404, detail="カレンダーが見つかりません")

    return {"success": True}
