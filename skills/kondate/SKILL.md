---
name: kondate
description: Meal management system for creating, searching, calendar registration, and nutrition balance calculation. Supports low-sodium, high-EPA/DHA diets for post-thrombosis recovery. Use when managing daily meals, calculating nutrition, or planning meal calendars.
---

# Kondate Skill - 献立管理システムスキル

献立管理システム「献立（Kondate）」のためのOpenClawスキル。

## 概要

献立の作成・検索・カレンダー登録・栄養バランス計算を行うスキルです。特に血栓の病気（脳梗塞など）の回復期に適した低塩・高EPA/DHA食の管理に対応しています。

**使い方**: このスキルのPythonスクリプト（`scripts/client.py`）を使って献立システムを操作します。

## 主な機能

### 1. 献立管理
- 献立の作成・編集・削除
- 献立の検索（セマンティック検索対応）
- タグによる分類・検索
- 栄養情報の管理（カロリー、タンパク質、塩分、脂質）

### 2. カレンダー管理
- 1日3食（朝・昼・夜）の献立登録
- 1ヶ月分のカレンダー一括登録
- 日次・週次・月次の献立計画

### 3. 栄養バランス計算
- 1食単位の栄養計算
- 1日単位の栄養計算（3食合計）
- 年代・性別モデルとの比較
- 適正値からの乖離判定

### 4. 献立提案
- 栄養バランスを考慮した献立提案
- 「血栓の病気に良い」献立の提案
- 好み・食材に基づいた提案

---

## Pythonスクリプトの使い方

### 基本コマンド

**実行方法（uv必須）:**
```bash
cd <openclaw-workspace>/skills/public/kondate
uv run python3 scripts/client.py <コマンド> [オプション]
```

### 献立管理

#### 献立一覧を取得

```bash
# 簡易表示（デフォルト10件）
uv run python3 scripts/client.py get-dishes

# 表示件数を指定
uv run python3 scripts/client.py get-dishes --limit 20

# オフセットを指定（21件目から40件目）
uv run python3 scripts/client.py get-dishes --limit 20 --offset 20

# 全件表示
uv run python3 scripts/client.py get-dishes --limit 0

# 詳細表示
uv run python3 scripts/client.py get-dishes --detail

# タイプでフィルタ
uv run python3 scripts/client.py get-dishes --type main --detail
```

#### 献立詳細を取得

```bash
uv run python3 scripts/client.py get-dish --dish-id 116
```

#### 献立を作成（JSON指定のみ）

**単数の献立を作成:**
```bash
uv run python3 scripts/client.py create-dish --json '{
  "name": "魚の唐揚げ",
  "type": "main",
  "description": "白身魚を唐揚げにした料理です",
  "calories": 250,
  "protein": 20,
  "sodium": 1.2,
  "fat": 15,
  "difficulty": "easy",
  "prep_time": 20,
  "servings": 2,
  "good_for_brain_health": false,
  "recipe": {
    "steps": [
      "白身魚を一口大に切る",
      "塩を振って10分置く",
      "小麦粉をまぶす",
      "180度の油で3分揚げる"
    ],
    "tips": "魚は水分をよく拭き取るとカリッと揚がります"
  },
  "ingredients": [
    {"name": "白身魚", "amount": "200g"},
    {"name": "小麦粉", "amount": "適量"}
  ],
  "tags": ["子供に人気", "揚げ物"]
}'
```

**複数の献立を一括作成（JSONファイル）:**

**単数の献立を作成:**
```bash
uv run python3 scripts/client.py create-dish --json '{
  "name": "魚の唐揚げ",
  "type": "main",
  "description": "白身魚を唐揚げにした料理です",
  "calories": 250,
  "protein": 20,
  "sodium": 1.2,
  "fat": 15,
  "difficulty": "easy",
  "prep_time": 20,
  "servings": 2,
  "good_for_brain_health": false
}'
```

**複数の献立を一括作成（JSONファイル）:**
```bash
uv run python3 scripts/client.py create-dish --json /path/to/dishes.json
```

`dishes.json` の例:
```json
[
  {
    "name": "青椒肉絲",
    "type": "main",
    "description": "ピーマンと肉の細切り炒め",
    "calories": 350,
    "protein": 18,
    "sodium": 1.8,
    "fat": 18,
    "difficulty": "easy",
    "prep_time": 20,
    "servings": 2,
    "good_for_brain_health": false,
    "recipe": {
      "steps": ["ピーマンを細切りにする", "肉を炒める", "合わせる"],
      "tips": "強火で手早く炒めるのがコツです"
    },
    "ingredients": [
      {"name": "豚ひき肉", "amount": "150g"},
      {"name": "ピーマン", "amount": "2個"}
    ],
    "tags": ["主菜", "炒め物", "中華"]
  },
  {
    "name": "麻婆豆腐",
    "type": "main",
    "description": "定番の中華料理",
    "calories": 420,
    "protein": 22,
    "sodium": 2.1,
    "fat": 25,
    "difficulty": "medium",
    "prep_time": 25,
    "servings": 2,
    "good_for_brain_health": false,
    "recipe": {
      "steps": ["豆腐を切る", "ひき肉を炒める", "合わせて煮込む"],
      "tips": "豆腐は水切りしておきましょう"
    },
    "ingredients": [
      {"name": "木綿豆腐", "amount": "1丁"},
      {"name": "豚ひき肉", "amount": "150g"}
    ],
    "tags": ["主菜", "炒め物", "中華", "ピリ辛"]
  }
]
```

#### 献立を更新（JSON指定のみ）

**部分更新（カロリーのみ変更）:**
```bash
uv run python3 scripts/client.py update-dish --dish-id 116 --json '{"calories": 200}'
```

**複数項目の更新:**
```bash
uv run python3 scripts/client.py update-dish --dish-id 116 --json '{
  "calories": 200,
  "protein": 25,
  "sodium": 1.5
}'
```

#### 献立を削除

```bash
uv run python3 scripts/client.py delete-dish --dish-id 1
  --description "更新後の説明"
```

#### 献立を削除

```bash
uv run python3 scripts/client.py delete-dish --dish-id 1
```

#### 献立を検索

```bash
# 基本的な検索（デフォルト10件）
uv run python3 scripts/client.py search-dishes "血栓の病気に良い"

# 表示件数を指定
uv run python3 scripts/client.py search-dishes "血栓の病気に良い" --limit 20

# 類似度スコアを表示
uv run python3 scripts/client.py search-dishes "血栓の病気に良い" --show-score

# 全件表示
uv run python3 scripts/client.py search-dishes "血栓の病気に良い" --limit 0

# タイプでフィルタ
uv run python3 scripts/client.py search-dishes "簡単で時短の主菜" --type main
```

### カレンダー管理

#### カレンダーを取得（簡易表示）

```bash
# 3月1日から3月31日まで
uv run python3 scripts/client.py get-calendar --start-date 2026-03-01 --end-date 2026-03-31

# 今週1週間分
uv run python3 scripts/client.py get-calendar --start-date 2026-03-01 --end-date 2026-03-07
```

#### カレンダーを取得（詳細表示）

```bash
uv run python3 scripts/client.py get-calendar --start-date 2026-03-01 --end-date 2026-03-31 --detail
```

#### カレンダーに献立を登録（JSON指定のみ）

**単数のカレンダーを登録:**
```bash
uv run python3 scripts/client.py register-calendar --json '{
  "date": "2026-03-09",
  "meal_type": "breakfast",
  "dish_ids": [1, 5, 8]
}'
```

**複数のカレンダーを一括登録（JSONファイル）:**
```bash
uv run python3 scripts/client.py register-calendar --json /path/to/calendar.json
```

`calendar.json` の例:
```json
[
  {
    "date": "2026-03-09",
    "meal_type": "breakfast",
    "dish_ids": [1, 5, 8]
  },
  {
    "date": "2026-03-09",
    "meal_type": "lunch",
    "dish_ids": [2, 6, 9]
  },
  {
    "date": "2026-03-09",
    "meal_type": "dinner",
    "dish_ids": [3, 7, 10]
  }
]
```

**重要**: 既に登録されている日付・食事タイプの場合、**409 Conflictエラー**が返されます。

**エラー時の処理フロー:**
1. 登録処理を継続し、成功・失敗（409）を記録
2. 全件処理後、サマリーを表示（成功件数、衝突件数）
3. 衝突したID一覧を表示（例: `2026-03-09_breakfast`, `2026-03-09_lunch`）
4. ユーザーに上書き確認を求める
5. ユーザーが「y」の場合、衝突した項目のみ `update-calendar` で上書き
6. ユーザーが「n」の場合、衝突した項目はスキップ

**非対話モードの場合:**
- 衝突した項目はスキップされます
- 上書きする場合は `update-calendar` コマンドを別途実行してください

#### カレンダーの献立を更新（上書き）（JSON指定のみ）

**単数のカレンダーを更新:**
```bash
uv run python3 scripts/client.py update-calendar --json '{
  "date": "2026-03-09",
  "meal_type": "breakfast",
  "dish_ids": [2, 6, 9]
}'
```

**複数のカレンダーを一括更新（JSONファイル）:**
```bash
uv run python3 scripts/client.py update-calendar --json /path/to/calendar.json
```

JSON形式は登録と同じです：
```json
[
  {
    "date": "2026-03-09",
    "meal_type": "breakfast",
    "dish_ids": [2, 6, 9]
  },
  {
    "date": "2026-03-09",
    "meal_type": "lunch",
    "dish_ids": [3, 7, 10]
  }
]
```

#### カレンダーの献立を削除

```bash
uv run python3 scripts/client.py delete-calendar \
  --date 2026-03-09 \
  --meal-type breakfast
```

### 栄養計算

#### 特定の日の栄養を計算

```bash
uv run python3 scripts/client.py calculate-nutrition \
  --date 2026-03-09 \
  --target "50代男性"
```

---

## 献立データの必須項目

献立を作成する際は、以下の**全ての項目**を入力してください：

### 基本項目

| 項目 | フィールド名 | 型 | 説明 |
|------|-------------|------|------|
| 献立名 | `name` | string | 献立の名前 |
| タイプ | `type` | string | main, side, soup, staple, dessert のいずれか |
| 説明 | `description` | string | 献立の説明 |
| カロリー | `calories` | float | kcal単位 |
| タンパク質 | `protein` | float | g単位 |
| 塩分 | `sodium` | float | g単位 |
| 脂質 | `fat` | float | g単位 |
| 難易度 | `difficulty` | string | easy, medium, hard のいずれか |
| 調理時間 | `prep_time` | int | 分単位 |
| 人数 | `servings` | int | 何人分か |
| 脳健康への影響 | `good_for_brain_health` | boolean | 血栓の病気に良い献立かどうか |

**重要**: 栄養情報（カロリー、タンパク質、脂質、塩分）は **人数分の総量** を登録してください。

- 4人前のカレーライスで550kcal → 550kcal を登録
- 2人前の豚汁で180kcal → 180kcal を登録
- 1人前のサラダで100kcal → 100kcal を登録

カレンダーに登録すると、API側が自動的に人数で割って **1人前** の栄養値に換算して返却します。

### レシピ項目（必須）

| 項目 | フィールド名 | 型 | 説明 |
|------|-------------|------|------|
| レシピ手順 | `recipe.steps` | array | 調理手順の文字列配列 |
| レシピのコツ | `recipe.tips` | string | 調理のコツやポイント |

### 食材項目（必須）

| 項目 | フィールド名 | 型 | 説明 |
|------|-------------|------|------|
| 食材リスト | `ingredients` | array | `[{name: string, amount: string}, ...]` の形式 |
| | `name` | string | 食材名（例: "白身魚"）自動的にマスタ登録されます |
| | `amount` | string | 分量（例: "200g", "大さじ1"） |

### タグ項目（必須）

| 項目 | フィールド名 | 型 | 説明 |
|------|-------------|------|------|
| タグリスト | `tags` | array | タグ名の文字列配列（例: ["主菜", "焼き物"]）自動的にマスタ登録されます |

---

## 献立タイプ（type）

献立を作成する際は、必ず以下のいずれかを指定してください：

- **main**: 主菜（肉・魚・卵・大豆製品）
- **side**: 副菜（野菜・海藻・きのこ）
- **soup**: 汁物（味噌汁・スープ）
- **staple**: 主食（ごはん・パン・麺）
- **dessert**: デザート（果物・ヨーグルト）

## 難易度（difficulty）

献立を作成する際は、必ず以下のいずれかを指定してください：

- **easy**: 簡単（調理初心者向け）
- **medium**: 中級（多少の調理経験が必要）
- **hard**: 上級（熟練した技術が必要）

---

## 血栓の病気に良い献立（good_for_brain_health）

献立を作成する際、以下の条件を満たす場合は `good_for_brain_health: true` を設定してください：

- 低塩分（1食2g以下）
- 高タンパク質（1食20g以上）
- EPA/DHA豊富な魚料理（焼き魚、煮魚など）
- 野菜たっぷり
- 適度な脂質
- **揚げ物は控えめ（基本的に `good_for_brain_health: false`）**

### 血栓の病気に良い献立の例

- **焼き魚**: 焼き鮭、焼きサバ、焼きブリ
- **煮魚**: サバの味噌煮、ブリ大根
- **蒸し料理**: 蒸し鶏、茶碗蒸し
- **和え物**: おから和え、ほうれん草のごま和え
- **スープ**: 豆腐の味噌汁、具だくさん豚汁

### 揚げ物の扱い

- 揚げ物は基本的に「血栓の病気に良い」チェックはオフ（`false`）
- ただし、栄養バランスを考慮して「たまには」OK
- **テスト用**: データ確認のためにチェックを入れる場合あり

---

## 栄養推奨値

### 年代・性別別の推奨値

| モデル | カロリー | タンパク質 | 塩分 |
|--------|----------|------------|------|
| 30代男性 | 2650kcal | 65g | 7.5g |
| 30代女性 | 2050kcal | 50g | 7.0g |
| 50代男性 | 2400kcal | 60g | 7.5g |
| 50代女性 | 1850kcal | 50g | 7.0g |
| 70代男性 | 2000kcal | 55g | 7.0g |
| 70代女性 | 1550kcal | 45g | 6.5g |
| 80代男性 | 1800kcal | 50g | 7.0g |
| 80代女性 | 1400kcal | 40g | 6.0g |

---

## エラーハンドリング

### 409 Conflictエラー（カレンダー登録時）

カレンダーに献立を登録する際、既に同じ日付・食事タイプの登録がある場合は **409 Conflictエラー** が返されます。

**スクリプトの自動処理:**

1. 全件の登録処理を試行
2. 成功・失敗（409）を記録
3. サマリーを表示（成功件数、衝突件数）
4. 衝突したID一覧を表示（例: `2026-03-09_breakfast`）
5. ユーザーに上書き確認を求める
6. ユーザーが「y」の場合、衝突した項目のみ更新

**Pythonでの実装例:**
```python
import sys
sys.path.insert(0, '<openclaw-workspace>/skills/public/kondate/scripts')

from client import KondateClient

client = KondateClient()

calendar_data = [
    {"date": "2026-03-09", "meal_type": "breakfast", "dish_ids": [1, 5, 8]},
    {"date": "2026-03-09", "meal_type": "lunch", "dish_ids": [2, 6, 9]},
    {"date": "2026-03-09", "meal_type": "dinner", "dish_ids": [3, 7, 10]}
]

success_items = []
conflict_items = []

for i, data in enumerate(calendar_data, 1):
    try:
        result = client.register_calendar(data['date'], data['meal_type'], data['dish_ids'])
        print(f"✅ [{i}/{len(calendar_data)}] 登録成功: {data['date']} {data['meal_type']}")
        success_items.append(i)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 409:
            item_key = f"{data['date']}_{data['meal_type']}"
            print(f"⚠️  [{i}/{len(calendar_data)}] 衝突: {data['date']} {data['meal_type']} (ID: {item_key})")
            conflict_items.append({"index": i, "key": item_key, "data": data})
        else:
            raise

# サマリー
print(f"\n📊 登録結果: 成功 {len(success_items)}件, 衝突 {len(conflict_items)}件")
print(f"衝突したID: {', '.join([item['key'] for item in conflict_items])}")

# ユーザー確認
if conflict_items:
    user_input = input("\n上書きしてもよろしいですか？ (y/n): ")
    if user_input.lower() == 'y':
        for item in conflict_items:
            data = item['data']
            result = client.update_calendar(data['date'], data['meal_type'], data['dish_ids'])
            print(f"✅ [{item['index']}/{len(calendar_data)}] 更新成功: {data['date']} {data['meal_type']}")
```

---

## 環境設定

### 必要な環境変数

```bash
export KONDATE_API_URL="http://localhost:10141"
export KONDATE_API_KEY=""  # 認証なしの場合は空
```

### 依存関係

- Python 3.11+
- requests
- python-dotenv

---

## 制限事項

- **献立一括作成**: JSONファイルで複数件指定可能（単数・複数対応）
- **カレンダー一括登録**: Python内部で1件ずつ登録（ループ処理）、409エラー時は自動的にユーザー確認
- 検索結果は最大100件まで
- **重複登録**: POSTは既存の場合409エラー、ユーザー確認後、衝突した項目のみPUTで更新
- **食材・タグ**: 献立登録時に自動的にマスタ登録されます（同じ名前の既存食材・タグは再利用）

