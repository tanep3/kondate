#!/usr/bin/env python3
"""
ChromaDBのベクトルを再生成するスクリプト
新しい埋め込みモデルに切り替えた後に実行
【実行手順】
cd /home/tane/dev/MyApplication/kondate
rm -rf ./src/datas/chroma
uv run python scripts/regenerate_chroma.py
"""

import sys
import os

# sentencepieceを先にインポート（tokenizerの問題回避）
import sentencepiece

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.database import get_db
from src.models.dish import Dish
from src.models.ingredient import Ingredient
from src.chroma_service import chroma_service


def regenerate_chroma():
    """ChromaDBのベクトルを再生成"""

    print("Starting ChromaDB vector regeneration...")

    # コレクションをリセット
    print("\n1. Resetting ChromaDB collection...")
    chroma_service.reset()

    # データベースから全献立を取得
    print("\n2. Loading dishes from database...")
    db = next(get_db())

    dishes = db.query(Dish).all()
    print(f"   Found {len(dishes)} dishes")

    # 各献立をChromaDBに追加
    print("\n3. Adding dishes to ChromaDB with new embeddings...")
    for dish in dishes:
        # 食材を取得（DishIngredient経由）
        from src.models.dish_ingredient import DishIngredient

        dish_ingredients = db.query(DishIngredient).filter(
            DishIngredient.dish_id == dish.id
        ).all()

        ingredient_names = [di.ingredient.name for di in dish_ingredients]

        # タグを取得（DishTag経由）
        from src.models.dish_tag import DishTag

        dish_tags = db.query(DishTag).filter(
            DishTag.dish_id == dish.id
        ).all()

        tag_names = [dt.tag.name for dt in dish_tags]

        # ドキュメントを作成（献立名 + 説明 + 食材 + タグ）
        document = f"{dish.name}: {dish.description or ''}. 食材: {', '.join(ingredient_names)}. タグ: {', '.join(tag_names)}"

        # メタデータを作成
        metadata = {
            "name": dish.name,
            "type": dish.type,
            "good_for_brain_health": dish.good_for_brain_health
        }

        # ChromaDBに追加
        chroma_service.add_dish(dish.id, document, metadata)
        print(f"   ✓ Added: {dish.name}")

    print(f"\n✓ Regeneration complete! Added {len(dishes)} dishes to ChromaDB.")


if __name__ == "__main__":
    regenerate_chroma()
