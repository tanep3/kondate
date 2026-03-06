"""
検索サービス
ChromaDBを使った献立のセマンティック検索
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from src.models import Dish
from src.chroma_service import chroma_service


class SearchService:
    """検索サービスクラス"""

    def __init__(self, db: Session):
        self.db = db

    def search_by_ingredients(
        self,
        query: str,
        n_results: int = 5,
        dish_type: Optional[str] = None,
        good_for_brain_health: Optional[bool] = None
    ) -> List[tuple[Dish, float]]:
        """
        食材から献立を検索

        Args:
            query: 検索クエリ（食材名など）
            n_results: 返却数
            dish_type: 献立タイプでフィルタ
            good_for_brain_health: 血栓の病気に良いかでフィルタ

        Returns:
            [(献立, 類似度スコア), ...] のリスト
        """
        # ChromaDBで検索
        where = {}
        if dish_type:
            where["type"] = dish_type
        if good_for_brain_health is not None:
            where["good_for_brain_health"] = good_for_brain_health
        
        # whereが空の場合はNoneを渡す
        where_clause = where if where else None
        results = chroma_service.search(query, n_results=n_results, where=where_clause)

        if not results or not results["ids"] or not results["ids"][0]:
            return []

        # 献立IDを取得
        dish_ids = []
        for dish_id_str in results["ids"][0]:
            dish_id = int(dish_id_str.replace("dish_", ""))
            dish_ids.append(dish_id)

        # データベースから献立を取得
        dishes = self.db.query(Dish).filter(Dish.id.in_(dish_ids)).all()

        # 血栓の病気に良いフィルタを適用
        if good_for_brain_health is not None:
            dishes = [d for d in dishes if d.good_for_brain_health == good_for_brain_health]

        # 類似度スコアとマッピング
        dish_map = {dish.id: dish for dish in dishes}
        dish_scores = []
        for i, dish_id_str in enumerate(results["ids"][0]):
            dish_id = int(dish_id_str.replace("dish_", ""))
            if dish_id in dish_map:
                # 距離を類似度に変換（コサイン距離は0-2の範囲）
                distance = results["distances"][0][i]
                # コサイン距離を0-1の類似度に変換: (2 - distance) / 2
                similarity = (2 - distance) / 2
                
                # 類似度が0.6以上のみを採用（日本語モデルなら精度が高い）
                if similarity >= 0.6:
                    dish_scores.append((dish_map[dish_id], similarity))

        # 類似度で降順ソート
        dish_scores.sort(key=lambda x: x[1], reverse=True)

        return dish_scores

    def search_similar(self, dish_id: int, n_results: int = 5) -> List[tuple[Dish, float]]:
        """
        類似献立を検索

        Args:
            dish_id: 基準献立ID
            n_results: 返却数

        Returns:
            [(献立, 類似度スコア), ...] のリスト
        """
        # 基準献立を取得
        dish = self.db.query(Dish).filter(Dish.id == dish_id).first()
        if not dish:
            return []

        # 献立名と説明で検索
        query = f"{dish.name}"
        if dish.description:
            query += f" {dish.description}"

        # ChromaDBで検索
        results = chroma_service.search(query, n_results=n_results + 1)  # +1は自分自身を除外するため

        if not results or not results["ids"] or not results["ids"][0]:
            return []

        # 類似献立を取得（自分自身を除外）
        dish_scores = []
        for i, dish_id_str in enumerate(results["ids"][0]):
            result_dish_id = int(dish_id_str.replace("dish_", ""))
            if result_dish_id == dish_id:
                continue  # 自分自身は除外

            result_dish = self.db.query(Dish).filter(Dish.id == result_dish_id).first()
            if result_dish:
                similarity = 1 - results["distances"][0][i]
                dish_scores.append((result_dish, similarity))
                if len(dish_scores) >= n_results:
                    break

        return dish_scores
