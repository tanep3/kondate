# APIリファレンス: Kondate - 献立管理システム

**バージョン:** 1.0  
**作成日:** 2026-03-08  
**作成者:** Amaterasu(OpenClaw) & Tane Channel Technology

---

## 1. 概要

### 1.1 ベースURL

```
http://localhost:10141
```

### 1.2 共通仕様

#### リクエストヘッダー
```json
{
  "Content-Type": "application/json"
}
```

#### レスポンス形式
```json
{
  "data": { ... },
  "error": null
}
```

#### エラーレスポンス
```json
{
  "detail": "エラーメッセージ"
}
```

#### HTTPステータスコード

| コード | 説明 |
|--------|------|
| 200 | 成功 |
| 201 | 作成成功 |
| 400 | リクエストエラー |
| 404 | リソース未検出 |
| 409 | 競合（既存リソース） |
| 422 | バリデーションエラー |
| 500 | サーバーエラー |

---

## 2. 献立API

### 2.1 献立一覧取得

**エンドポイント:** `GET /api/dishes`

**クエリパラメータ:**

| パラメータ | 型 | 必須 | 説明 |
|-----------|------|------|------|
| skip | Integer | | スキップ数（デフォルト: 0） |
| limit | Integer | | 取得数（デフォルト: 50, 最大: 100） |
| type | String | | 献立タイプ（main/side/soup/staple/dessert） |
| good_for_brain_health | Boolean | | 血栓の病気に良いかどうか |

**リクエスト例:**
```bash
curl -X GET "http://localhost:10141/api/dishes?skip=0&limit=30&type=main"
```

**レスポンス例:**
```json
{
  "items": [
    {
      "id": 1,
      "name": "とんかつ",
      "type": "main",
      "description": "豚ロース肉を使ったとんかつ",
      "difficulty": "medium",
      "prep_time": 30,
      "servings": 2,
      "calories": 700,
      "protein": 30,
      "fat": 40,
      "sodium": 1.5,
      "good_for_brain_health": false,
      "created_at": "2026-03-08T12:00:00",
      "updated_at": "2026-03-08T12:00:00"
    }
  ],
  "total": 107
}
```

---

### 2.2 献立詳細取得

**エンドポイント:** `GET /api/dishes/{id}`

**パスパラメータ:**

| パラメータ | 型 | 必須 | 説明 |
|-----------|------|------|------|
| id | Integer | ✓ | 献立ID |

**リクエスト例:**
```bash
curl -X GET "http://localhost:10141/api/dishes/1"
```

**レスポンス例:**
```json
{
  "id": 1,
  "name": "とんかつ",
  "type": "main",
  "description": "豚ロース肉を使ったとんかつ",
  "difficulty": "medium",
  "prep_time": 30,
  "servings": 2,
  "calories": 700,
  "protein": 30,
  "fat": 40,
  "sodium": 1.5,
  "good_for_brain_health": false,
  "recipe": {
    "ingredients": "豚ロース肉 2枚、小麦粉 適量、卵 1個、パン粉 適量",
    "steps": [
      "豚肉を叩いて伸ばす",
      "小麦粉、溶き卵、パン粉の順につける",
      "180℃の油で揚げる"
    ],
    "tips": "油は170-180℃に温度設定してください。衣がカリッとなるまで揚げます。"
  },
  "ingredients": [
    {
      "id": 1,
      "name": "豚ロース肉",
      "amount": "2枚"
    },
    {
      "id": 2,
      "name": "小麦粉",
      "amount": "適量"
    }
  ],
  "tags": [
    {
      "id": 1,
      "name": "主菜"
    },
    {
      "id": 2,
      "name": "揚げ物"
    }
  ],
  "created_at": "2026-03-08T12:00:00",
  "updated_at": "2026-03-08T12:00:00"
}
```

---

### 2.3 献立作成

**エンドポイント:** `POST /api/dishes`

**リクエストボディ:**

| 項目 | 型 | 必須 | 説明 |
|------|------|------|------|
| name | String | ✓ | 献立名 |
| type | String | ✓ | 献立タイプ（main/side/soup/staple/dessert） |
| description | String | ✓ | 説明 |
| difficulty | String | ✓ | 難易度（easy/medium/hard） |
| prep_time | Integer | ✓ | 調理時間（分） |
| servings | Integer | ✓ | 人数（デフォルト: 2） |
| calories | Float | ✓ | カロリー（kcal/総量） |
| protein | Float | ✓ | タンパク質（g/総量） |
| fat | Float | ✓ | 脂質（g/総量） |
| sodium | Float | ✓ | 塩分（g/総量） |
| good_for_brain_health | Boolean | | 血栓の病気に良いかどうか |
| recipe | Object | | レシピ情報 |
| recipe.ingredients | String | ✓ | 材料 |
| recipe.steps | Array | ✓ | 調理手順 |
| recipe.tips | String | ✓ | コツ・ヒント |
| ingredients | Array | ✓ | 食材リスト |
| ingredients[].name | String | ✓ | 食材名 |
| ingredients[].amount | String | ✓ | 分量 |
| tags | Array | ✓ | タグリスト |
| tags[].name | String | ✓ | タグ名 |

**リクエスト例:**
```bash
curl -X POST "http://localhost:10141/api/dishes" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "焼き魚定食",
    "type": "main",
    "description": "鮭の塩焼き定食",
    "difficulty": "easy",
    "prep_time": 20,
    "servings": 2,
    "calories": 400,
    "protein": 35,
    "fat": 15,
    "sodium": 1.2,
    "good_for_brain_health": true,
    "recipe": {
      "ingredients": "鮭 2切れ、塩 適量、大根 1/4本",
      "steps": [
        "鮭に塩を振る",
        "グリルで焼く"
      ],
      "tips": "塩は焼く30分前に振ると味が馴染みます"
    },
    "ingredients": [
      {"name": "鮭", "amount": "2切れ"},
      {"name": "塩", "amount": "適量"}
    ],
    "tags": [
      {"name": "主菜"},
      {"name": "焼き魚"},
      {"name": "簡単"}
    ]
  }'
```

**レスポンス例:**
```json
{
  "id": 108,
  "name": "焼き魚定食",
  "type": "main",
  ...
}
```

**ステータスコード:** `201 Created`

---

### 2.4 献立更新

**エンドポイント:** `PUT /api/dishes/{id}`

**パスパラメータ:**

| パラメータ | 型 | 必須 | 説明 |
|-----------|------|------|------|
| id | Integer | ✓ | 献立ID |

**リクエストボディ:**
- 献立作成と同じ（すべてオプション）

**リクエスト例:**
```bash
curl -X PUT "http://localhost:10141/api/dishes/108" \
  -H "Content-Type: application/json" \
  -d '{
    "calories": 420
  }'
```

**レスポンス例:**
```json
{
  "id": 108,
  "name": "焼き魚定食",
  "calories": 420,
  ...
}
```

---

### 2.5 献立削除

**エンドポイント:** `DELETE /api/dishes/{id}`

**パスパラメータ:**

| パラメータ | 型 | 必須 | 説明 |
|-----------|------|------|------|
| id | Integer | ✓ | 献立ID |

**リクエスト例:**
```bash
curl -X DELETE "http://localhost:10141/api/dishes/108"
```

**レスポンス例:**
```json
{
  "success": true
}
```

---

## 3. 検索API

### 3.1 献立検索（セマンティック検索）

**エンドポイント:** `GET /api/search/dishes`

**クエリパラメータ:**

| パラメータ | 型 | 必須 | 説明 |
|-----------|------|------|------|
| q | String | ✓ | 検索クエリ |
| limit | Integer | | 取得数（デフォルト: 50, 最大: 100） |
| type | String | | 献立タイプフィルタ |
| good_for_brain_health | Boolean | | 血栓の病気に良いかどうかフィルタ |

**リクエスト例:**
```bash
curl -X GET "http://localhost:10141/api/search/dishes?q=血栓の病気に良い&limit=10"
```

**レスポンス例:**
```json
{
  "items": [
    {
      "id": 6,
      "name": "サバ缶サラダ",
      "type": "side",
      "description": "キャベツとサバ缶で簡単サラダ",
      "similarity": 0.92,
      "calories": 180,
      "protein": 12,
      "sodium": 0.8,
      "servings": 2
    }
  ],
  "total": 5
}
```

**注意:** 
- `similarity`は0-1の範囲で類似度を示す（1.0が完全一致）
- ChromaDBのコサイン距離を `(2 - distance) / 2` で正規化

---

## 4. 提案API

### 4.1 献立提案

**エンドポイント:** `GET /api/suggest`

**クエリパラメータ:**

| パラメータ | 型 | 必須 | 説明 |
|-----------|------|------|------|
| prefer | String | | 優先献立タイプ（fish/meat/etc.） |
| limit | Integer | | 取得数（デフォルト: 50） |

**リクエスト例:**
```bash
curl -X GET "http://localhost:10141/api/suggest?prefer=fish&limit=10"
```

**レスポンス例:**
```json
{
  "items": [
    {
      "id": 1,
      "name": "焼き魚",
      "type": "main",
      "calories": 200,
      "protein": 25,
      "sodium": 1.0
    }
  ]
}
```

---

## 5. カレンダーAPI

### 5.1 カレンダー取得（日付範囲）

**エンドポイント:** `GET /api/calendar`

**クエリパラメータ:**

| パラメータ | 型 | 必須 | 説明 |
|-----------|------|------|------|
| start | String | | 開始日（YYYY-MM-DD） |
| end | String | | 終了日（YYYY-MM-DD） |
| year | Integer | | 年 |
| month | Integer | | 月 |
| date | String | | 日付（YYYY-MM-DD） |

**リクエスト例（日付範囲）:**
```bash
curl -X GET "http://localhost:10141/api/calendar?start=2026-03-01&end=2026-03-07"
```

**レスポンス例（日付範囲）:**
```json
{
  "start": "2026-03-01",
  "end": "2026-03-07",
  "items": [
    {
      "id": 1,
      "date": "2026-03-07",
      "meal_type": "breakfast",
      "main": {
        "id": 8,
        "name": "ごはん",
        "calories": 115,
        "protein": 2,
        "sodium": 0,
        "servings": 2
      },
      "side": {
        "id": 7,
        "name": "豆腐の味噌汁",
        "calories": 25,
        "protein": 2.5,
        "sodium": 0.45,
        "servings": 2
      },
      "soup": null,
      "staple": null,
      "dessert": null,
      "nutrition": {
        "calories": 140,
        "protein": 4.5,
        "sodium": 0.45
      }
    }
  ]
}
```

**注意:** 栄養情報は**1人前**に換算されています（総量 ÷ 人数）

---

**リクエスト例（月間）:**
```bash
curl -X GET "http://localhost:10141/api/calendar?year=2026&month=3"
```

**レスポンス例（月間）:**
```json
{
  "start": "2026-03-01",
  "end": "2026-03-31",
  "items": [...]
}
```

---

**リクエスト例（1日分の3食）:**
```bash
curl -X GET "http://localhost:10141/api/calendar?date=2026-03-07"
```

**レスポンス例（1日分の3食）:**
```json
{
  "date": "2026-03-07",
  "meals": [
    {
      "id": 1,
      "date": "2026-03-07",
      "meal_type": "breakfast",
      "main": {...},
      "side": {...},
      "nutrition": {...}
    },
    {
      "id": 2,
      "date": "2026-03-07",
      "meal_type": "lunch",
      ...
    },
    {
      "id": 3,
      "date": "2026-03-07",
      "meal_type": "dinner",
      ...
    }
  ],
  "total_nutrition": {
    "calories": 1845,
    "protein": 91,
    "sodium": 8.9
  }
}
```

---

### 5.2 カレンダー登録

**エンドポイント:** `POST /api/calendar`

**リクエストボディ:**

| 項目 | 型 | 必須 | 説明 |
|------|------|------|------|
| date | String | ✓ | 日付（YYYY-MM-DD） |
| meal_type | String | ✓ | 食事タイプ（breakfast/lunch/dinner） |
| dishes | Array | ✓ | 献立リスト |
| dishes[].dish_id | Integer | ✓ | 献立ID |

**リクエスト例:**
```bash
curl -X POST "http://localhost:10141/api/calendar" \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2026-03-15",
    "meal_type": "dinner",
    "dishes": [
      {"dish_id": 3},
      {"dish_id": 5},
      {"dish_id": 7}
    ]
  }'
```

**レスポンス例:**
```json
{
  "id": 10,
  "date": "2026-03-15",
  "meal_type": "dinner",
  "main": {
    "id": 3,
    "name": "とんかつ",
    "calories": 350,
    "protein": 15,
    "sodium": 0.75,
    "servings": 2
  },
  "side": {
    "id": 5,
    "name": "キャベツの千切り",
    "calories": 45,
    "protein": 1.5,
    "sodium": 0,
    "servings": 2
  },
  "soup": {
    "id": 7,
    "name": "豆腐の味噌汁",
    "calories": 25,
    "protein": 2.5,
    "sodium": 0.45,
    "servings": 2
  },
  "nutrition": {
    "calories": 420,
    "protein": 19,
    "sodium": 1.2
  }
}
```

**エラーレスポンス（409 Conflict）:**
```json
{
  "detail": "2026-03-15のdinnerは既に登録されています。更新するにはPUTメソッドを使用してください。"
}
```

**ステータスコード:** 
- `201 Created`: 登録成功
- `409 Conflict`: 既存登録あり

---

### 5.3 カレンダー更新

**エンドポイント:** `PUT /api/calendar/{date}?meal_type={type}`

**パスパラメータ:**

| パラメータ | 型 | 必須 | 説明 |
|-----------|------|------|------|
| date | String | ✓ | 日付（YYYY-MM-DD） |

**クエリパラメータ:**

| パラメータ | 型 | 必須 | 説明 |
|-----------|------|------|------|
| meal_type | String | | 食事タイプ（デフォルト: dinner） |

**リクエストボディ:**
- カレンダー登録と同じ

**リクエスト例:**
```bash
curl -X PUT "http://localhost:10141/api/calendar/2026-03-15?meal_type=dinner" \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2026-03-15",
    "meal_type": "dinner",
    "dishes": [
      {"dish_id": 4},
      {"dish_id": 6},
      {"dish_id": 8}
    ]
  }'
```

**レスポンス例:**
```json
{
  "id": 10,
  "date": "2026-03-15",
  "meal_type": "dinner",
  ...
}
```

---

### 5.4 カレンダー削除

**エンドポイント:** `DELETE /api/calendar/{date}?meal_type={type}`

**パスパラメータ:**

| パラメータ | 型 | 必須 | 説明 |
|-----------|------|------|------|
| date | String | ✓ | 日付（YYYY-MM-DD） |

**クエリパラメータ:**

| パラメータ | 型 | 必須 | 説明 |
|-----------|------|------|------|
| meal_type | String | | 食事タイプ（デフォルト: dinner） |

**リクエスト例:**
```bash
curl -X DELETE "http://localhost:10141/api/calendar/2026-03-15?meal_type=dinner"
```

**レスポンス例:**
```json
{
  "success": true
}
```

---

## 6. 栄養計算API

### 6.1 栄養計算

**エンドポイント:** `GET /api/nutrition/calculate`

**クエリパラメータ:**

| パラメータ | 型 | 必須 | 説明 |
|-----------|------|------|------|
| date | String | ✓ | 日付（YYYY-MM-DD） |
| target | String | ✓ | 対象モデル（例: 50代男性） |

**対象モデル一覧:**

- `30代男性`
- `30代女性`
- `50代男性`
- `50代女性`
- `70代男性`
- `70代女性`
- `80代男性`
- `80代女性`

**リクエスト例:**
```bash
curl -X GET "http://localhost:10141/api/nutrition/calculate?date=2026-03-15&target=50代男性"
```

**レスポンス例:**
```json
{
  "date": "2026-03-15",
  "target": "50代男性",
  "recommendations": {
    "calories": 2400,
    "protein": 60,
    "sodium": 7.5
  },
  "meals": [
    {
      "meal_type": "breakfast",
      "calories": 420,
      "protein": 19,
      "sodium": 1.2
    },
    {
      "meal_type": "lunch",
      "calories": 780,
      "protein": 22,
      "sodium": 3.0
    },
    {
      "meal_type": "dinner",
      "calories": 645,
      "protein": 50,
      "sodium": 4.7
    }
  ],
  "total": {
    "calories": 1845,
    "protein": 91,
    "sodium": 8.9
  },
  "balance": {
    "calories": "76.9% (少なめ)",
    "protein": "151.7% (多め)",
    "sodium": "118.7% (多め)"
  }
}
```

---

## 7. エラーハンドリング

### 7.1 409 Conflict（カレンダー）

カレンダー登録時に、既存の登録がある場合に返される。

**エラーレスポンス:**
```json
{
  "detail": "2026-03-15のdinnerは既に登録されています。更新するにはPUTメソッドを使用してください。"
}
```

**クライアント側のハンドリング:**

1. POSTで新規登録を試みる
2. 409エラーを受信
3. ユーザーに確認: "既に登録されています。上書きしてもよろしいですか？ (y/n)"
4. 「y」の場合: PUTで更新
5. 「n」の場合: キャンセル

**実装例（Python）:**
```python
import requests

try:
    result = client.register_calendar(date, meal_type, dish_ids)
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 409:
        # ユーザー確認
        user_ok = input("上書きしてもよろしいですか？ (y/n): ")
        if user_ok == 'y':
            result = client.update_calendar(date, meal_type, dish_ids)
```

---

## 8. 人数考慮

### 8.1 栄養情報の総量

献立テーブルの栄養情報は**総量**で登録する。

**例: 4人前のレシピ**
- カロリー: 800kcal（総量）
- タンパク質: 40g（総量）
- 塩分: 3.0g（総量）
- 人数: 4人

### 8.2 1人前への換算

カレンダー表示時、栄養計算APIで**1人前に換算**する。

**換算式:**
```
1人前の値 = 総量 ÷ 人数
```

**例:**
- 800kcal ÷ 4人 = 200kcal（1人前）

---

## 9. Skill使用方法

### 9.1 Pythonクライアント

**実行方法（uv必須）:**
```bash
cd /home/tane/clawd/skills/public/kondate
uv run python3 scripts/client.py get-dishes
```

**主要コマンド:**

```bash
# 献立一覧取得
uv run python3 scripts/client.py get-dishes

# 献立作成
uv run python3 scripts/client.py create-dish \
  --name "焼き魚" \
  --type main \
  --description "鮭の塩焼き" \
  --difficulty easy \
  --cooking-time 20 \
  --servings 2 \
  --calories 400 \
  --protein 35 \
  --fat 15 \
  --sodium 1.2

# カレンダー登録
uv run python3 scripts/client.py register-calendar \
  --date 2026-03-15 \
  --meal-type dinner \
  --dish-ids 3 5 7

# カレンダー取得
uv run python3 scripts/client.py get-calendar \
  --year 2026 \
  --month 3 \
  --detail

# 栄養計算
uv run python3 scripts/client.py calculate-nutrition \
  --date 2026-03-15 \
  --target "50代男性"
```

---

## 10. 制約事項

### 10.1 バルクAPI

バルク登録API（`/api/dishes/bulk`, `/api/calendar/bulk`）は**廃止**されました。

**代替手段:**
- Skill側でイテレーション（単一APIをループ呼び出し）

**実装例:**
```python
for dish_data in dishes_data:
    dish = client.create_dish(dish_data)
```

---

**文書終了**
