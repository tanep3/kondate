"""
提案サービス
献立の提案・組み合わせ生成
"""

from sqlalchemy.orm import Session
from typing import List, Optional
import random
from src.models import Dish, DishType


class SuggestService:
    """提案サービスクラス"""

    def __init__(self, db: Session):
        self.db = db

    def suggest_menu(
        self,
        prefer: Optional[str] = None,
        max_sodium: Optional[float] = None
    ) -> dict:
        """
        献立を提案

        Args:
            prefer: 優先するタイプ（fish, meat, vegetableなど）
            max_sodium: 塩分上限（g）

        Returns:
            提案メニュー辞書
        """
        # 主菜を取得
        main_dishes = self._get_dishes_by_type(DishType.MAIN, prefer)
        main = random.choice(main_dishes) if main_dishes else None

        # 副菜を取得（2つ）
        side_dishes = self._get_dishes_by_type(DishType.SIDE)
        sides = random.sample(side_dishes, min(2, len(side_dishes))) if side_dishes else []

        # 汁物を取得
        soup_dishes = self._get_dishes_by_type(DishType.SOUP)
        soup = random.choice(soup_dishes) if soup_dishes else None

        # 栄養合計を計算
        total_nutrition = self._calculate_total([main] + sides + ([soup] if soup else []))

        # 塩分チェック
        if max_sodium and total_nutrition["sodium"] > max_sodium:
            # 塩分オーバーなら再帰的に再試行（最大3回）
            if random.random() < 0.7:  # 70%の確率で再試行
                return self.suggest_menu(prefer, max_sodium)

        return {
            "main": main.to_dict() if main else None,
            "side1": sides[0].to_dict() if len(sides) > 0 else None,
            "side2": sides[1].to_dict() if len(sides) > 1 else None,
            "soup": soup.to_dict() if soup else None,
            "total_nutrition": total_nutrition
        }

    def _get_dishes_by_type(
        self,
        dish_type: DishType,
        prefer: Optional[str] = None
    ) -> List[Dish]:
        """
        タイプ別に献立を取得

        Args:
            dish_type: 献立タイプ
            prefer: 優先条件（簡易実装：血栓の病気に良いものを優先）

        Returns:
            献立リスト
        """
        query = self.db.query(Dish).filter(Dish.type == dish_type)

        # 優先条件がある場合
        if prefer == "healthy" or prefer == "brain":
            # 血栓の病気に良いものを優先
            healthy_dishes = query.filter(Dish.good_for_brain_health == True).all()
            if healthy_dishes:
                return healthy_dishes

        return query.all()

    def _calculate_total(self, dishes: List[Dish]) -> dict:
        """
        栄養合計を計算

        Args:
            dishes: 献立リスト

        Returns:
            栄養合計辞書
        """
        total = {
            "calories": 0,
            "protein": 0,
            "fat": 0,
            "sodium": 0
        }

        for dish in dishes:
            if dish:
                total["calories"] += dish.calories or 0
                total["protein"] += dish.protein or 0
                total["fat"] += dish.fat or 0
                total["sodium"] += dish.sodium or 0

        return total
