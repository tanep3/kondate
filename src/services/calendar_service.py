"""
カレンダーサービス
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from src.models import Calendar, Dish
from src.schemas.calendar import CalendarCreate, CalendarUpdate


class CalendarService:
    """カレンダーサービスクラス"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_date_range(self, start: str, end: str) -> List[Calendar]:
        """
        日付範囲でカレンダーを取得

        Args:
            start: 開始日（ISO 8601）
            end: 終了日（ISO 8601）

        Returns:
            カレンダーリスト
        """
        calendars = self.db.query(Calendar).filter(
            Calendar.date >= start,
            Calendar.date <= end
        ).order_by(Calendar.date).all()

        return calendars

    def get_by_date(self, date: str) -> Optional[Calendar]:
        """
        日付でカレンダーを取得

        Args:
            date: 日付（ISO 8601）

        Returns:
            カレンダーオブジェクト
        """
        return self.db.query(Calendar).filter(Calendar.date == date).first()

    def create(self, date: str, data: CalendarCreate) -> Calendar:
        """
        カレンダーを作成

        Args:
            date: 日付（ISO 8601）
            data: 作成データ

        Returns:
            作成されたカレンダー
        """
        calendar = Calendar(
            date=date,
            main_dish_id=data.main_dish_id,
            side1_dish_id=data.side1_dish_id,
            side2_dish_id=data.side2_dish_id,
            soup_dish_id=data.soup_dish_id
        )
        self.db.add(calendar)
        self.db.commit()
        self.db.refresh(calendar)
        return calendar

    def update(self, date: str, data: CalendarUpdate) -> Optional[Calendar]:
        """
        カレンダーを更新

        Args:
            date: 日付（ISO 8601）
            data: 更新データ

        Returns:
            更新されたカレンダー
        """
        calendar = self.get_by_date(date)
        if not calendar:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(calendar, field, value)

        self.db.commit()
        self.db.refresh(calendar)
        return calendar

    def delete(self, date: str) -> bool:
        """
        カレンダーを削除

        Args:
            date: 日付（ISO 8601）

        Returns:
            削除成功したかどうか
        """
        calendar = self.get_by_date(date)
        if not calendar:
            return False

        self.db.delete(calendar)
        self.db.commit()
        return True

    def to_detail_dict(self, calendar: Calendar) -> dict:
        """
        詳細辞書形式に変換（献立情報付き）

        Args:
            calendar: カレンダーオブジェクト

        Returns:
            詳細辞書
        """
        result = {
            "id": calendar.id,
            "date": calendar.date
        }

        # 各献立を取得
        dish_ids = [
            ("main", calendar.main_dish_id),
            ("side1", calendar.side1_dish_id),
            ("side2", calendar.side2_dish_id),
            ("soup", calendar.soup_dish_id)
        ]

        for key, dish_id in dish_ids:
            if dish_id:
                dish = self.db.query(Dish).filter(Dish.id == dish_id).first()
                result[key] = dish.to_dict() if dish else None
            else:
                result[key] = None

        return result
