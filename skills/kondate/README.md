# Kondate Skill

献立管理システム「献立（Kondate）」のためのOpenClawスキル。

## セットアップ

```bash
# 依存関係をインストール（uvを使用）
uv sync

# 環境変数を設定
export KONDATE_API_URL="http://localhost:10141"
export KONDATE_API_KEY=""  # 認証なしの場合は空
```

## 使い方

### Pythonクライアント

**献立管理:**
```bash
# 献立一覧取得
uv run python3 scripts/client.py get-dishes

# 詳細表示
uv run python3 scripts/client.py get-dishes --detail

# ページング（21件目から40件目）
uv run python3 scripts/client.py get-dishes --limit 20 --offset 20

# 献立詳細取得
uv run python3 scripts/client.py get-dish --dish-id 1

# 献立作成（JSON指定）
uv run python3 scripts/client.py create-dish --json '{
  "name": "魚の唐揚げ",
  "type": "main",
  "description": "白身魚を唐揚げにした料理",
  "calories": 250,
  "protein": 20,
  "sodium": 1.2,
  "fat": 15,
  "difficulty": "easy",
  "prep_time": 20,
  "servings": 2,
  "good_for_brain_health": false,
  "recipe": {
    "steps": ["白身魚を一口大に切る", "塩を振って10分置く", "小麦粉をまぶす", "180度の油で3分揚げる"],
    "tips": "魚は水分をよく拭き取るとカリッと揚がります"
  },
  "ingredients": [
    {"name": "白身魚", "amount": "200g"},
    {"name": "小麦粉", "amount": "適量"}
  ],
  "tags": ["主菜", "揚げ物"]
}'

# 献立更新（JSON指定）
uv run python3 scripts/client.py update-dish --dish-id 1 --json '{"calories": 300}'

# 献立削除
uv run python3 scripts/client.py delete-dish --dish-id 1

# 献立検索
uv run python3 scripts/client.py search-dishes "血栓の病気に良い"
uv run python3 scripts/client.py search-dishes "血栓の病気に良い" --limit 20 --show-score
```

**カレンダー管理:**
```bash
# カレンダー取得（範囲指定）
uv run python3 scripts/client.py get-calendar --start-date 2026-03-01 --end-date 2026-03-31

# カレンダー詳細表示
uv run python3 scripts/client.py get-calendar --start-date 2026-03-01 --end-date 2026-03-31 --detail

# カレンダー登録（JSON指定）
uv run python3 scripts/client.py register-calendar --json '{
  "date": "2026-03-09",
  "meal_type": "breakfast",
  "dish_ids": [1, 5, 8]
}'

# カレンダー一括登録（JSONファイル）
uv run python3 scripts/client.py register-calendar --json /path/to/calendar.json

# カレンダー更新
uv run python3 scripts/client.py update-calendar --json '{
  "date": "2026-03-09",
  "meal_type": "breakfast",
  "dish_ids": [2, 6, 9]
}'

# カレンダー削除
uv run python3 scripts/client.py delete-calendar --date 2026-03-09 --meal-type breakfast
```

**栄養計算:**
```bash
# 特定の日の栄養計算
uv run python3 scripts/client.py calculate-nutrition \
  --date 2026-03-09 \
  --target "50代男性"
```

## 機能

### 献立管理
- ✅ 献立の作成・編集・削除
- ✅ 献立の検索（セマンティック検索対応）
- ✅ タグによる分類・検索
- ✅ 栄養情報の管理
- ✅ ページング対応（`--limit`, `--offset`）
- ✅ 類似度スコア表示（`--show-score`）

### カレンダー管理
- ✅ 1日3食（朝・昼・夜）の献立登録
- ✅ 日付範囲指定でカレンダー取得
- ✅ カレンダー一括登録（JSONファイル）
- ✅ 409 Conflictエラーの対話的処理

### 栄養バランス計算
- ✅ 1食単位の栄養計算
- ✅ 1日単位の栄養計算（3食合計）
- ✅ 年代・性別モデルとの比較
- ✅ 適正値からの乖離判定
- ✅ **人数で割って1人前に換算**

## 献立タイプ

- **main**: 主菜（肉・魚・卵・大豆製品）
- **side**: 副菜（野菜・海藻・きのこ）
- **soup**: 汁物（味噌汁・スープ）
- **staple**: 主食（ごはん・パン・麺）
- **dessert**: デザート（果物・ヨーグルト）

## 栄養情報の登録ルール

**重要**: 栄養情報（カロリー、タンパク質、脂質、塩分）は **人数分の総量** を登録してください。

- 4人前のカレーライスで550kcal → 550kcal を登録
- 2人前の豚汁で180kcal → 180kcal を登録
- 1人前のサラダで100kcal → 100kcal を登録

カレンダーに登録すると、API側が自動的に人数で割って **1人前** の栄養値に換算して返却します。

## 栄養推奨値

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

## サーバー起動

```bash
cd /path/to/kondate
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 10141
```

## ドキュメント

詳細な使い方は [SKILL.md](./SKILL.md) を参照してください。

## ライセンス

MIT License
