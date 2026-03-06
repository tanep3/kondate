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
    db: Session = Depends(get_db)
):
    """
    カレンダーを取得

    - **start**: 開始日（指定しない場合は今日）
    - **end**: 終了日（指定しない場合は7日後）
    """
    service = CalendarService(db)

    # デフォルト値設定
    if not start:
        from datetime import datetime, timedelta
        start = (datetime.now() + timedelta(hours=9)).strftime("%Y-%m-%d")  # JST
    if not end:
        from datetime import datetime, timedelta
        end = (datetime.now() + timedelta(days=7, hours=9)).strftime("%Y-%m-%d")  # JST

    calendars = service.get_by_date_range(start, end)

    items = []
    for calendar in calendars:
        items.append(service.to_detail_dict(calendar))

    return {"start": start, "end": end, "items": items}


@router.get("/{date}")
def get_calendar_by_date(
    date: str,
    db: Session = Depends(get_db)
):
    """
    日付でカレンダーを取得

    - **date**: 日付（ISO 8601形式: YYYY-MM-DD）
    """
    service = CalendarService(db)
    calendar = service.get_by_date(date)

    if not calendar:
        return {"date": date, "main": None, "side1": None, "side2": None, "soup": None}

    return service.to_detail_dict(calendar)


@router.post("/{date}")
def create_calendar(
    date: str,
    data: CalendarCreate,
    db: Session = Depends(get_db)
):
    """
    カレンダーを作成

    - **date**: 日付（ISO 8601形式: YYYY-MM-DD）
    - **main_dish_id**: 主菜ID
    - **side1_dish_id**: 副菜1 ID
    - **side2_dish_id**: 副菜2 ID
    - **soup_dish_id**: 汁物ID
    """
    service = CalendarService(db)

    # 既存チェック
    existing = service.get_by_date(date)
    if existing:
        raise HTTPException(status_code=400, detail="既に登録されています")

    calendar = service.create(date, data)
    return service.to_detail_dict(calendar)


@router.put("/{date}")
def update_calendar(
    date: str,
    data: CalendarUpdate,
    db: Session = Depends(get_db)
):
    """
    カレンダーを更新

    全フィールドがオプションです。指定したフィールドのみ更新されます。
    """
    service = CalendarService(db)
    calendar = service.update(date, data)

    if not calendar:
        raise HTTPException(status_code=404, detail="カレンダーが見つかりません")

    return service.to_detail_dict(calendar)


@router.delete("/{date}", status_code=204)
def delete_calendar(
    date: str,
    db: Session = Depends(get_db)
):
    """
    カレンダーを削除
    """
    service = CalendarService(db)
    success = service.delete(date)

    if not success:
        raise HTTPException(status_code=404, detail="カレンダーが見つかりません")

    return None
