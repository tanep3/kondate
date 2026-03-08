"""
献立サービス
献立に関するビジネスロジック
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from src.models import Dish, Recipe, Ingredient, DishIngredient, Tag, DishTag
from src.schemas.dish import DishCreate, DishUpdate, IngredientCreate
from src.chroma_service import chroma_service
import json


class DishService:
    """献立サービスクラス"""

    def __init__(self, db: Session):
        self.db = db

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        dish_type: Optional[str] = None,
        good_for_brain_health: Optional[bool] = None
    ) -> tuple[List[Dish], int]:
        """
        献立一覧を取得

        Args:
            skip: スキップ数
            limit: 取得上限
            dish_type: 献立タイプでフィルタ
            good_for_brain_health: 血栓の病気に良いかでフィルタ

        Returns:
            (献立リスト, 総数)
        """
        query = self.db.query(Dish)

        # フィルタ適用
        if dish_type:
            query = query.filter(Dish.type == dish_type)
        if good_for_brain_health is not None:
            query = query.filter(Dish.good_for_brain_health == good_for_brain_health)

        # 総数取得
        total = query.count()

        # ページネーション適用
        dishes = query.offset(skip).limit(limit).all()

        # リレーションをロード
        for dish in dishes:
            self._load_relations(dish)

        return dishes, total

    def get_by_id(self, dish_id: int) -> Optional[Dish]:
        """
        IDで献立を取得

        Args:
            dish_id: 献立ID

        Returns:
            献立オブジェクト（存在しない場合はNone）
        """
        dish = self.db.query(Dish).filter(Dish.id == dish_id).first()
        if dish:
            self._load_relations(dish)
        return dish

    def _load_relations(self, dish: Dish):
        """献立のリレーションをロード"""
        # レシピ
        if not dish.recipe:
            recipe = self.db.query(Recipe).filter(Recipe.dish_id == dish.id).first()
            dish.recipe = recipe

        # 食材
        if not dish.ingredients:
            dish_ingredients = self.db.query(DishIngredient).filter(
                DishIngredient.dish_id == dish.id
            ).all()
            for di in dish_ingredients:
                ingredient = self.db.query(Ingredient).filter(
                    Ingredient.id == di.ingredient_id
                ).first()
                di.ingredient = ingredient
            dish.ingredients = dish_ingredients

        # タグ
        if not dish.tags:
            dish_tags = self.db.query(DishTag).filter(DishTag.dish_id == dish.id).all()
            for dt in dish_tags:
                tag = self.db.query(Tag).filter(Tag.id == dt.tag_id).first()
                dt.tag = tag
            dish.tags = dish_tags

    def create(self, dish_data: DishCreate) -> Dish:
        """
        献立を作成

        Args:
            dish_data: 献立作成データ

        Returns:
            作成された献立
        """
        # 献立を作成
        dish_dict = dish_data.model_dump(exclude={"recipe", "ingredients", "tags"})
        dish = Dish(**dish_dict)
        self.db.add(dish)
        self.db.flush()  # IDを取得するためにflush

        # レシピを作成
        if dish_data.recipe:
            # stepsがNoneまたは空の場合は空のJSONにする
            steps = dish_data.recipe.steps if dish_data.recipe.steps else []
            recipe = Recipe(
                dish_id=dish.id,
                steps=json.dumps(steps, ensure_ascii=False),
                tips=dish_data.recipe.tips
            )
            self.db.add(recipe)

        # 食材を登録・紐付け
        if dish_data.ingredients:
            for ing_data in dish_data.ingredients:
                # 食材を取得または作成
                ingredient = self.db.query(Ingredient).filter(
                    Ingredient.name == ing_data.name
                ).first()
                if not ingredient:
                    ingredient = Ingredient(name=ing_data.name)
                    self.db.add(ingredient)
                    self.db.flush()

                # 献立-食材関連を作成
                dish_ingredient = DishIngredient(
                    dish_id=dish.id,
                    ingredient_id=ingredient.id,
                    amount=ing_data.amount
                )
                self.db.add(dish_ingredient)

        # タグを登録・紐付け
        if dish_data.tags:
            for tag_name in dish_data.tags:
                # タグを取得または作成
                tag = self.db.query(Tag).filter(Tag.name == tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    self.db.add(tag)
                    self.db.flush()

                # 献立-タグ関連を作成
                dish_tag = DishTag(dish_id=dish.id, tag_id=tag.id)
                self.db.add(dish_tag)

        self.db.commit()
        self.db.refresh(dish)

        # ChromaDBに同期
        self._sync_to_chroma(dish)

        return dish

    def update(self, dish_id: int, dish_data: DishUpdate) -> Optional[Dish]:
        """
        献立を更新

        Args:
            dish_id: 献立ID
            dish_data: 更新データ

        Returns:
            更新された献立（存在しない場合はNone）
        """
        dish = self.get_by_id(dish_id)
        if not dish:
            return None

        # 基本フィールドを更新
        update_data = dish_data.model_dump(exclude_unset=True, exclude={"recipe", "ingredients", "tags"})
        for field, value in update_data.items():
            setattr(dish, field, value)

        # レシピを更新
        if dish_data.recipe is not None:
            if not dish.recipe:
                recipe = Recipe(dish_id=dish.id)
                self.db.add(recipe)
                self.db.flush()
                dish.recipe = recipe

            if dish_data.recipe.steps is not None:
                dish.recipe.set_steps(dish_data.recipe.steps)
            if dish_data.recipe.tips is not None:
                dish.recipe.tips = dish_data.recipe.tips

        # 食材を更新（一度削除して再登録）
        if dish_data.ingredients is not None:
            # 既存の関連を削除
            self.db.query(DishIngredient).filter(
                DishIngredient.dish_id == dish_id
            ).delete()

            # 新しい関連を登録
            for ing_data in dish_data.ingredients:
                ingredient = self.db.query(Ingredient).filter(
                    Ingredient.name == ing_data.name
                ).first()
                if not ingredient:
                    ingredient = Ingredient(name=ing_data.name)
                    self.db.add(ingredient)
                    self.db.flush()

                dish_ingredient = DishIngredient(
                    dish_id=dish.id,
                    ingredient_id=ingredient.id,
                    amount=ing_data.amount
                )
                self.db.add(dish_ingredient)

        # タグを更新（一度削除して再登録）
        if dish_data.tags is not None:
            # 既存の関連を削除
            self.db.query(DishTag).filter(DishTag.dish_id == dish_id).delete()

            # 新しい関連を登録
            for tag_name in dish_data.tags:
                tag = self.db.query(Tag).filter(Tag.name == tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    self.db.add(tag)
                    self.db.flush()

                dish_tag = DishTag(dish_id=dish.id, tag_id=tag.id)
                self.db.add(dish_tag)

        self.db.commit()
        self.db.refresh(dish)

        # ChromaDBに同期
        self._sync_to_chroma(dish)

        return dish

    def delete(self, dish_id: int) -> bool:
        """
        献立を削除

        Args:
            dish_id: 献立ID

        Returns:
            削除成功したかどうか
        """
        dish = self.db.query(Dish).filter(Dish.id == dish_id).first()
        if not dish:
            return False

        # ChromaDBから削除
        chroma_service.delete_dish(dish_id)

        # データベースから削除（CASCADEにより関連も削除）
        self.db.delete(dish)
        self.db.commit()

        return True

    def _sync_to_chroma(self, dish: Dish):
        """
        献立をChromaDBに同期

        Args:
            dish: 献立オブジェクト
        """
        # リレーションをロード
        self._load_relations(dish)

        # 食材をまとめる
        ingredients_summary = ", ".join([
            f"{di.ingredient.name}" for di in dish.ingredients
        ]) if dish.ingredients else ""

        # ドキュメント構築
        document = f"{dish.name}"
        if dish.description:
            document += f": {dish.description}"
        if ingredients_summary:
            document += f". 食材: {ingredients_summary}"

        # メタデータ構築
        metadata = {
            "dish_id": dish.id,
            "name": dish.name,
            "type": dish.type.value,
            "calories": dish.calories or 0,
            "protein": dish.protein or 0,
            "sodium": dish.sodium or 0,
            "good_for_brain_health": dish.good_for_brain_health or False
        }

        # ChromaDBに追加/更新
        chroma_service.add_dish(dish.id, document, metadata)
