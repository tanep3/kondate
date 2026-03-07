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
        ).order_by(Calendar.date, Calendar.meal_type).all()

        return calendars

    def get_by_date(self, date: str, meal_type: str = "dinner") -> Optional[Calendar]:
        """
        日付と食事タイプでカレンダーを取得

        Args:
            date: 日付（ISO 8601）
            meal_type: 食事タイプ（breakfast, lunch, dinner）

        Returns:
            カレンダーオブジェクト
        """
        return self.db.query(Calendar).filter(
            Calendar.date == date,
            Calendar.meal_type == meal_type
        ).first()

    def get_by_date_all_meals(self, date: str) -> List[Calendar]:
        """
        日付ですべての食事を取得

        Args:
            date: 日付（ISO 8601）

        Returns:
            カレンダーリスト（朝、昼、晩）
        """
        return self.db.query(Calendar).filter(
            Calendar.date == date
        ).order_by(Calendar.meal_type).all()

    def create(self, date: str, data: CalendarCreate) -> Calendar:
        """
        カレンダーを作成

        Args:
            date: 日付（ISO 8601）
            data: 作成データ

        Returns:
            作成されたカレンダー
        """
        main_dish_id = data.main_dish_id
        side1_dish_id = data.side1_dish_id
        side2_dish_id = data.side2_dish_id
        soup_dish_id = data.soup_dish_id
        staple_dish_id = data.staple_dish_id
        dessert_dish_id = data.dessert_dish_id

        if data.dishes:
            for item in data.dishes:
                dish = self.db.query(Dish).filter(Dish.id == item.dish_id).first()
                if dish:
                    if dish.type == "main":
                        main_dish_id = item.dish_id
                    elif dish.type == "side":
                        if not side1_dish_id:
                            side1_dish_id = item.dish_id
                        else:
                            side2_dish_id = item.dish_id
                    elif dish.type == "soup":
                        soup_dish_id = item.dish_id
                    elif dish.type == "staple":
                        staple_dish_id = item.dish_id
                    elif dish.type == "dessert":
                        dessert_dish_id = item.dish_id

        calendar = Calendar(
            date=date,
            meal_type=data.meal_type,
            main_dish_id=main_dish_id,
            side1_dish_id=side1_dish_id,
            side2_dish_id=side2_dish_id,
            soup_dish_id=soup_dish_id,
            staple_dish_id=staple_dish_id,
            dessert_dish_id=dessert_dish_id
        )
        self.db.add(calendar)
        self.db.commit()
        self.db.refresh(calendar)
        return calendar

    def update(self, date: str, meal_type: str, data: CalendarUpdate) -> Optional[Calendar]:
        """
        カレンダーを更新

        Args:
            date: 日付（ISO 8601）
            meal_type: 食事タイプ
            data: 更新データ

        Returns:
            更新されたカレンダー
        """
        calendar = self.get_by_date(date, meal_type)
        if not calendar:
            return None

        update_data = data.model_dump(exclude_unset=True)

        if "dishes" in update_data and update_data["dishes"]:
            dishes = update_data.pop("dishes")
            main_dish_id = None
            side1_dish_id = None
            side2_dish_id = None
            soup_dish_id = None
            staple_dish_id = None
            dessert_dish_id = None

            for item in dishes:
                dish_id = item.get("dish_id") if isinstance(item, dict) else item.dish_id
                dish = self.db.query(Dish).filter(Dish.id == dish_id).first()
                if dish:
                    if dish.type == "main":
                        main_dish_id = dish_id
                    elif dish.type == "side":
                        if not side1_dish_id:
                            side1_dish_id = dish_id
                        else:
                            side2_dish_id = dish_id
                    elif dish.type == "soup":
                        soup_dish_id = dish_id
                    elif dish.type == "staple":
                        staple_dish_id = dish_id
                    elif dish.type == "dessert":
                        dessert_dish_id = dish_id

            update_data["main_dish_id"] = main_dish_id
            update_data["side1_dish_id"] = side1_dish_id
            update_data["side2_dish_id"] = side2_dish_id
            update_data["soup_dish_id"] = soup_dish_id
            update_data["staple_dish_id"] = staple_dish_id
            update_data["dessert_dish_id"] = dessert_dish_id
        else:
            update_data["main_dish_id"] = None
            update_data["side1_dish_id"] = None
            update_data["side2_dish_id"] = None
            update_data["soup_dish_id"] = None
            update_data["staple_dish_id"] = None
            update_data["dessert_dish_id"] = None

        for field, value in update_data.items():
            setattr(calendar, field, value)

        self.db.commit()
        self.db.refresh(calendar)
        return calendar

    def delete(self, date: str, meal_type: str) -> bool:
        """
        カレンダーを削除

        Args:
            date: 日付（ISO 8601）
            meal_type: 食事タイプ

        Returns:
            削除成功したかどうか
        """
        calendar = self.get_by_date(date, meal_type)
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
            "date": calendar.date,
            "meal_type": calendar.meal_type
        }

        dish_ids = [
            ("main", calendar.main_dish_id),
            ("side1", calendar.side1_dish_id),
            ("side2", calendar.side2_dish_id),
            ("soup", calendar.soup_dish_id),
            ("staple", calendar.staple_dish_id),
            ("dessert", calendar.dessert_dish_id)
        ]

        total_calories = 0
        total_protein = 0
        total_sodium = 0

        for key, dish_id in dish_ids:
            if dish_id:
                dish = self.db.query(Dish).filter(Dish.id == dish_id).first()
                dish_dict = dish.to_dict() if dish else None
                
                if dish_dict:
                    if dish.calories:
                        total_calories += dish.calories
                    if dish.protein:
                        total_protein += dish.protein
                    if dish.sodium:
                        total_sodium += dish.sodium
                
                if key == "side1":
                    result["side"] = dish_dict
                elif key == "side2":
                    result["side2"] = dish_dict
                else:
                    result[key] = dish_dict
            else:
                if key == "side1":
                    result["side"] = None
                elif key == "side2":
                    result["side2"] = None
                else:
                    result[key] = None

        result["nutrition"] = {
            "calories": round(total_calories, 1),
            "protein": round(total_protein, 1),
            "sodium": round(total_sodium, 1)
        }

        return result
