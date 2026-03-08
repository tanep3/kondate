#!/usr/bin/env python3
"""
献立管理システム APIクライアント

献立の作成・検索・カレンダー登録・栄養計算を行うクライアント。
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta
from typing import List, Dict, Optional

try:
    import requests
    from dotenv import load_dotenv
except ImportError:
    print("Error: Required packages not installed.")
    print("Install: pip install requests python-dotenv")
    sys.exit(1)

# 環境変数をロード
load_dotenv()

API_URL = os.getenv("KONDATE_API_URL", "http://localhost:10141")
API_KEY = os.getenv("KONDATE_API_KEY", "")


class KondateClient:
    """献立管理システム APIクライアント"""

    def __init__(self, api_url: str = API_URL, api_key: str = API_KEY):
        self.api_url = api_url
        self.api_key = api_key
        self.headers = {}
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"

    def _request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """APIリクエストを送信"""
        url = f"{self.api_url}{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url, headers=self.headers, params=data)
            elif method == "POST":
                response = requests.post(url, headers=self.headers, json=data)
            elif method == "PUT":
                response = requests.put(url, headers=self.headers, json=data)
            elif method == "DELETE":
                response = requests.delete(url, headers=self.headers, params=data)
            else:
                raise ValueError(f"Invalid method: {method}")

            response.raise_for_status()

            # レスポンスボディが空の場合は空辞書を返す
            if not response.content:
                return {}

            return response.json()

        except requests.exceptions.HTTPError as e:
            # 409 Conflictエラーはそのまま返す（呼び出し元でハンドリング）
            raise
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            sys.exit(1)

    # 献立管理

    def get_dishes(self, skip: int = 0, limit: int = 50, dish_type: Optional[str] = None) -> List[Dict]:
        """献立一覧を取得"""
        params = {"skip": skip, "limit": limit}
        if dish_type:
            params["type"] = dish_type
        
        result = self._request("GET", "/api/dishes", params)
        return result.get("items", [])

    def get_dish(self, dish_id: int) -> Dict:
        """献立詳細を取得"""
        return self._request("GET", f"/api/dishes/{dish_id}")

    def create_dish(self, dish_data: Dict) -> Dict:
        """献立を作成（全項目必須バリデーション付き）"""
        # 必須項目チェック
        required_fields = {
            "name": "献立名",
            "type": "献立タイプ",
            "difficulty": "難易度",
            "cooking_time": "調理時間",
            "servings": "人数",
            "description": "説明",
            "calories": "カロリー",
            "protein": "タンパク質",
            "fat": "脂質",
            "sodium": "塩分"
        }
        
        for field, label in required_fields.items():
            if field not in dish_data or dish_data[field] is None or dish_data[field] == "":
                raise ValueError(f"必須項目 '{label}' が入力されていません")
        
        # レシピ情報チェック
        if "recipe" not in dish_data or not dish_data["recipe"]:
            raise ValueError("レシピ情報（recipe）が入力されていません")
        
        recipe = dish_data["recipe"]
        
        if "steps" not in recipe or not recipe["steps"]:
            raise ValueError("調理手順（recipe.steps）が入力されていません")
        
        if "tips" not in recipe or not recipe["tips"]:
            raise ValueError("コツ・ポイント（recipe.tips）が入力されていません")
        
        # 食材チェック
        if "ingredients" not in dish_data or not dish_data["ingredients"]:
            raise ValueError("食材（ingredients）が入力されていません")
        
        # タグチェック
        if "tags" not in dish_data or not dish_data["tags"]:
            raise ValueError("タグ（tags）が入力されていません")
        
        return self._request("POST", "/api/dishes", dish_data)

    def update_dish(self, dish_id: int, dish_data: Dict) -> Dict:
        """献立を更新"""
        return self._request("PUT", f"/api/dishes/{dish_id}", dish_data)

    def delete_dish(self, dish_id: int) -> None:
        """献立を削除"""
        self._request("DELETE", f"/api/dishes/{dish_id}")

    # 検索

    def search_dishes(self, query: str, limit: int = 50, dish_type: Optional[str] = None) -> List[Dict]:
        """献立を検索"""
        params = {"q": query, "limit": limit}
        if dish_type:
            params["type"] = dish_type
        
        result = self._request("GET", "/api/search/dishes", params)
        return result.get("items", [])

    def suggest_dishes(self, prefer: Optional[str] = None, limit: int = 50) -> List[Dict]:
        """献立を提案"""
        params = {"limit": limit}
        if prefer:
            params["prefer"] = prefer
        
        result = self._request("GET", "/api/suggest", params)
        return result.get("items", [])

    # カレンダー

    def get_calendar(self, start_date: str, end_date: str) -> List[Dict]:
        """カレンダーを取得（日付範囲指定）"""
        params = {"start": start_date, "end": end_date}
        result = self._request("GET", "/api/calendar", params)
        return result.get("items", [])

    def register_calendar(self, date: str, meal_type: str, dish_ids: List[int]) -> Dict:
        """カレンダーに献立を登録（既存の場合は409 Conflictエラー）"""
        data = {
            "date": date,
            "meal_type": meal_type,
            "dishes": [{"dish_id": did} for did in dish_ids]
        }
        return self._request("POST", "/api/calendar", data)

    def register_or_update_calendar(self, date: str, meal_type: str, dish_ids: List[int], auto_update: bool = False) -> Dict:
        """カレンダーに献立を登録または更新（Skillイテレーション方式）"""
        data = {
            "date": date,
            "meal_type": meal_type,
            "dishes": [{"dish_id": did} for did in dish_ids]
        }
        
        try:
            # 新規登録を試みる
            return self._request("POST", "/api/calendar", data)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 409:
                # 既存の場合
                if auto_update:
                    # 自動更新
                    return self._request("PUT", f"/api/calendar/{date}?meal_type={meal_type}", data)
                else:
                    # エラーを返す
                    error_data = e.response.json()
                    raise Exception(f"既存登録: {error_data.get('detail', 'Unknown error')}")
            else:
                raise

    def update_calendar(self, date: str, meal_type: str, dish_ids: List[int]) -> Dict:
        """カレンダーの献立を更新"""
        data = {
            "date": date,
            "meal_type": meal_type,
            "dishes": [{"dish_id": did} for did in dish_ids]
        }
        return self._request("PUT", f"/api/calendar/{date}", data)

    def delete_calendar(self, date: str, meal_type: str) -> None:
        """カレンダーの献立を削除"""
        self._request("DELETE", f"/api/calendar/{date}?meal_type={meal_type}")

    # 栄養計算

    def calculate_nutrition(self, date: str, target: str) -> Dict:
        """栄養バランスを計算"""
        params = {"date": date, "target": target}
        return self._request("GET", "/api/nutrition/calculate", params)


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description="献立管理システム APIクライアント")
    
    subparsers = parser.add_subparsers(dest="command", help="コマンド")

    # 献立一覧取得
    get_dishes_parser = subparsers.add_parser("get-dishes", help="献立一覧を取得")
    get_dishes_parser.add_argument("--detail", action="store_true", help="詳細表示")
    get_dishes_parser.add_argument("--type", choices=["main", "side", "soup", "staple", "dessert"], help="献立タイプでフィルタ")
    get_dishes_parser.add_argument("--limit", type=int, default=10, help="表示件数（0で全件、デフォルト10件）")
    get_dishes_parser.add_argument("--offset", type=int, default=0, help="オフセット（デフォルト0）")

    # 献立詳細取得
    get_dish_parser = subparsers.add_parser("get-dish", help="献立詳細を取得")
    get_dish_parser.add_argument("--dish-id", type=int, required=True, help="献立ID")

    # 献立作成
    create_parser = subparsers.add_parser("create-dish", help="献立を作成（JSON指定のみ）")
    create_parser.add_argument("--json", required=True, help="JSONファイルまたはJSON文字列")

    # 献立更新
    update_parser = subparsers.add_parser("update-dish", help="献立を更新")
    update_parser.add_argument("--dish-id", type=int, required=True, help="献立ID")
    update_parser.add_argument("--json", required=True, help="JSONファイルまたはJSON文字列（更新する項目のみ）")

    # 献立削除
    delete_parser = subparsers.add_parser("delete-dish", help="献立を削除")
    delete_parser.add_argument("--dish-id", type=int, required=True, help="献立ID")

    # 献立検索
    search_parser = subparsers.add_parser("search-dishes", help="献立を検索")
    search_parser.add_argument("query", help="検索クエリ")
    search_parser.add_argument("--type", choices=["main", "side", "soup", "staple", "dessert"], help="献立タイプ")
    search_parser.add_argument("--limit", type=int, default=10, help="表示件数（0で全件、デフォルト10件）")
    search_parser.add_argument("--show-score", action="store_true", help="類似度スコアを表示")

    # カレンダー登録
    calendar_parser = subparsers.add_parser("register-calendar", help="カレンダーに献立を登録（JSON指定のみ）")
    calendar_parser.add_argument("--json", required=True, help="JSONファイルまたはJSON文字列")

    # カレンダー取得
    get_calendar_parser = subparsers.add_parser("get-calendar", help="カレンダーを取得")
    get_calendar_parser.add_argument("--start-date", required=True, help="開始日（YYYY-MM-DD）")
    get_calendar_parser.add_argument("--end-date", required=True, help="終了日（YYYY-MM-DD）")
    get_calendar_parser.add_argument("--detail", action="store_true", help="詳細表示")

    # カレンダー更新
    update_calendar_parser = subparsers.add_parser("update-calendar", help="カレンダーを更新（JSON指定のみ）")
    update_calendar_parser.add_argument("--json", required=True, help="JSONファイルまたはJSON文字列")

    # カレンダー削除
    delete_calendar_parser = subparsers.add_parser("delete-calendar", help="カレンダーを削除")
    delete_calendar_parser.add_argument("--date", required=True, help="日付（YYYY-MM-DD）")
    delete_calendar_parser.add_argument("--meal-type", required=True, choices=["breakfast", "lunch", "dinner"], help="食事タイプ")

    # 栄養計算
    nutrition_parser = subparsers.add_parser("calculate-nutrition", help="栄養バランスを計算")
    nutrition_parser.add_argument("--date", required=True, help="日付（YYYY-MM-DD）")
    nutrition_parser.add_argument("--target", required=True, help="対象モデル（例: 50代男性）")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    client = KondateClient()

    try:
        if args.command == "get-dishes":
            dishes = client.get_dishes(dish_type=getattr(args, 'type', None))
            limit = args.limit if args.limit > 0 else len(dishes)
            offset = args.offset

            # 表示範囲を決定
            dishes_to_show = dishes[offset:offset + limit]

            print(f"総献立数: {len(dishes)}件（表示: {offset + 1}〜{min(offset + limit, len(dishes))}件）")

            if args.detail:
                # 詳細表示
                for dish in dishes_to_show:
                    print(f"\n🍽️  {dish['name']} (ID: {dish['id']})")
                    print(f"   タイプ: {dish['type']}")
                    print(f"   説明: {dish['description']}")
                    print(f"   栄養: {dish['calories']}kcal, タンパク質{dish['protein']}g, 塩分{dish['sodium']}g, 脂質{dish['fat']}g")
                    print(f"   難易度: {dish['difficulty']}, 調理時間: {dish['prep_time']}分, 人数: {dish['servings']}人")
                    print(f"   good_for_brain_health: {dish['good_for_brain_health']}")

                    # レシピ
                    if dish.get('recipe'):
                        print(f"   レシピ:")
                        for i, step in enumerate(dish['recipe']['steps'], 1):
                            print(f"     {i}. {step}")
                        if dish['recipe'].get('tips'):
                            print(f"   コツ: {dish['recipe']['tips']}")

                    # 食材
                    if dish.get('ingredients'):
                        print(f"   食材:")
                        for ing in dish['ingredients']:
                            print(f"     - {ing['ingredient']['name']}: {ing['amount']}")

                    # タグ
                    if dish.get('tags'):
                        tags = ", ".join([tag['name'] for tag in dish['tags']])
                        print(f"   タグ: {tags}")
            else:
                # 簡易表示
                for dish in dishes_to_show:
                    print(f"- {dish['name']} (ID: {dish['id']}, {dish['type']})")
                if offset + limit < len(dishes):
                    print(f"... 他 {len(dishes) - offset - limit} 件")

        elif args.command == "get-dish":
            dish = client.get_dish(args.dish_id)
            print(f"\n🍽️  {dish['name']} (ID: {dish['id']})")
            print(f"   タイプ: {dish['type']}")
            print(f"   説明: {dish['description']}")
            print(f"   栄養: {dish['calories']}kcal, タンパク質{dish['protein']}g, 塩分{dish['sodium']}g, 脂質{dish['fat']}g")
            print(f"   難易度: {dish['difficulty']}, 調理時間: {dish['prep_time']}分, 人数: {dish['servings']}人")
            print(f"   good_for_brain_health: {dish['good_for_brain_health']}")

            # レシピ
            if dish.get('recipe'):
                print(f"   レシピ:")
                for i, step in enumerate(dish['recipe']['steps'], 1):
                    print(f"     {i}. {step}")
                if dish['recipe'].get('tips'):
                    print(f"   コツ: {dish['recipe']['tips']}")

            # 食材
            if dish.get('ingredients'):
                print(f"   食材:")
                for ing in dish['ingredients']:
                    print(f"     - {ing['ingredient']['name']}: {ing['amount']}")

            # タグ
            if dish.get('tags'):
                tags = ", ".join([tag['name'] for tag in dish['tags']])
                print(f"   タグ: {tags}")

        elif args.command == "create-dish":
            # ファイルから読み込み
            if os.path.isfile(args.json):
                with open(args.json, "r", encoding="utf-8") as f:
                    dish_data = json.load(f)
            # JSON文字列として解析
            else:
                dish_data = json.loads(args.json)

            # 単数の献立データの場合
            if isinstance(dish_data, dict):
                dish = client.create_dish(dish_data)
                print(f"✅ 献立を作成しました: {dish['name']} (ID: {dish['id']})")
            # 複数の献立データの場合（リスト）
            elif isinstance(dish_data, list):
                for i, data in enumerate(dish_data, 1):
                    dish = client.create_dish(data)
                    print(f"✅ [{i}/{len(dish_data)}] 献立を作成しました: {dish['name']} (ID: {dish['id']})")

        elif args.command == "delete-dish":
            client.delete_dish(args.dish_id)
            print(f"✅ 献立を削除しました: ID {args.dish_id}")

        elif args.command == "search-dishes":
            dishes = client.search_dishes(args.query, dish_type=args.type)
            limit = args.limit if args.limit > 0 else len(dishes)

            print(f"検索結果: {len(dishes)}件（表示: {min(limit, len(dishes))}件）")

            for i, dish in enumerate(dishes[:limit], 1):
                if args.show_score:
                    # 類似度スコア付き表示
                    score = dish.get('score', dish.get('similarity', 'N/A'))
                    print(f"{i}. {dish['name']} (ID: {dish['id']}, {dish['type']}) [スコア: {score}]")
                else:
                    # 通常表示
                    print(f"{i}. {dish['name']} (ID: {dish['id']}, {dish['type']})")

        elif args.command == "update-dish":
            # ファイルから読み込み
            if os.path.isfile(args.json):
                with open(args.json, "r", encoding="utf-8") as f:
                    update_data = json.load(f)
            # JSON文字列として解析
            else:
                update_data = json.loads(args.json)

            # 更新実行
            dish = client.update_dish(args.dish_id, update_data)
            print(f"✅ 献立を更新しました: {dish['name']} (ID: {dish['id']})")

        elif args.command == "register-calendar":
            # ファイルから読み込み
            if os.path.isfile(args.json):
                with open(args.json, "r", encoding="utf-8") as f:
                    calendar_data = json.load(f)
            # JSON文字列として解析
            else:
                calendar_data = json.loads(args.json)

            # 複数のカレンダーデータの場合（リスト）
            if isinstance(calendar_data, list):
                success_items = []
                conflict_items = []

                for i, data in enumerate(calendar_data, 1):
                    try:
                        result = client.register_calendar(data['date'], data['meal_type'], data['dish_ids'])
                        print(f"✅ [{i}/{len(calendar_data)}] カレンダーに登録しました: {data['date']} {data['meal_type']}")
                        success_items.append(i)
                    except requests.exceptions.HTTPError as e:
                        if e.response.status_code == 409:
                            item_key = f"{data['date']}_{data['meal_type']}"
                            print(f"⚠️  [{i}/{len(calendar_data)}] 既に登録されています: {data['date']} {data['meal_type']} (ID: {item_key})")
                            conflict_items.append({"index": i, "key": item_key, "data": data})
                        else:
                            raise

                # 409エラーがあった場合、サマリーを表示
                if conflict_items:
                    print(f"\n📊 登録結果: 成功 {len(success_items)}件, 衝突 {len(conflict_items)}件")
                    print(f"衝突したID: {', '.join([item['key'] for item in conflict_items])}")

                    # ユーザー確認（対話モードのみ）
                    try:
                        user_input = input("\n上書きしてもよろしいですか？ (y/n): ")
                        if user_input.lower() == 'y':
                            print("\n🔄 上書き処理を開始します...")
                            for item in conflict_items:
                                data = item['data']
                                result = client.update_calendar(data['date'], data['meal_type'], data['dish_ids'])
                                print(f"✅ [{item['index']}/{len(calendar_data)}] カレンダーを更新しました: {data['date']} {data['meal_type']}")
                            print(f"\n✨ すべての処理が完了しました！")
                        else:
                            print(f"\n❌ キャンセルしました。衝突した {len(conflict_items)} 件は登録されていません。")
                    except (EOFError, KeyboardInterrupt):
                        # 非対話モードの場合
                        print(f"\n⚠️  衝突した {len(conflict_items)} 件を上書きするには、update-calendar コマンドを使用してください。")
            # 単数のカレンダーデータの場合（辞書）
            elif isinstance(calendar_data, dict):
                result = client.register_calendar(calendar_data['date'], calendar_data['meal_type'], calendar_data['dish_ids'])
                print(f"✅ カレンダーに登録しました: {calendar_data['date']} {calendar_data['meal_type']}")

        elif args.command == "get-calendar":
            items = client.get_calendar(args.start_date, args.end_date)
            print(f"📅 {args.start_date} から {args.end_date} までの献立カレンダー")
            print(f"総数: {len(items)}件")
            
            if args.detail:
                # 詳細表示
                for item in items:
                    print(f"\n📅 {item['date']} {item['meal_type']}")
                    if item['main']:
                        print(f"  🍖 主菜: {item['main']['name']}")
                    if item['side']:
                        print(f"  🥗 副菜: {item['side']['name']}")
                    if item['soup']:
                        print(f"  🍲 汁物: {item['soup']['name']}")
                    if item['staple']:
                        print(f"  🍚 主食: {item['staple']['name']}")
                    if item['dessert']:
                        print(f"  🍰 デザート: {item['dessert']['name']}")
                    if item.get('nutrition'):
                        print(f"  📊 栄養: {item['nutrition']['calories']}kcal, タンパク質{item['nutrition']['protein']}g, 塩分{item['nutrition']['sodium']}g")
            else:
                # 簡易表示
                for item in items[:10]:
                    dishes = []
                    if item['main']:
                        dishes.append(item['main']['name'])
                    if item['side']:
                        dishes.append(item['side']['name'])
                    if item['soup']:
                        dishes.append(item['soup']['name'])
                    dish_list = ", ".join(dishes) if dishes else "なし"
                    print(f"- {item['date']} {item['meal_type']}: {dish_list}")
                
                if len(items) > 10:
                    print(f"... 他{len(items) - 10}件")

        elif args.command == "update-calendar":
            # ファイルから読み込み
            if os.path.isfile(args.json):
                with open(args.json, "r", encoding="utf-8") as f:
                    calendar_data = json.load(f)
            # JSON文字列として解析
            else:
                calendar_data = json.loads(args.json)

            # 複数のカレンダーデータの場合（リスト）
            if isinstance(calendar_data, list):
                for i, data in enumerate(calendar_data, 1):
                    result = client.update_calendar(data['date'], data['meal_type'], data['dish_ids'])
                    print(f"✅ [{i}/{len(calendar_data)}] カレンダーを更新しました: {data['date']} {data['meal_type']}")
            # 単数のカレンダーデータの場合（辞書）
            elif isinstance(calendar_data, dict):
                result = client.update_calendar(calendar_data['date'], calendar_data['meal_type'], calendar_data['dish_ids'])
                print(f"✅ カレンダーを更新しました: {calendar_data['date']} {calendar_data['meal_type']}")

        elif args.command == "delete-calendar":
            client.delete_calendar(args.date, args.meal_type)
            print(f"✅ カレンダーを削除しました: {args.date} {args.meal_type}")

        elif args.command == "calculate-nutrition":
            result = client.calculate_nutrition(args.date, args.target)
            print(f"📊 栄養バランス計算結果 ({args.date}, {args.target})")
            if "total" in result:
                total = result["total"]
                print(f"総カロリー: {total.get('calories', 0)}kcal")
                print(f"総タンパク質: {total.get('protein', 0)}g")
                print(f"総塩分: {total.get('sodium', 0)}g")
            if "balance" in result:
                balance = result["balance"]
                print(f"\nバランス:")
                for key, value in balance.items():
                    print(f"- {key}: {value}")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
