# システム設計書: Kondate - 献立管理システム

**バージョン:** 1.0  
**作成日:** 2025-01-23  
**作成者:** Amaterasu(OpenClaw) & Tane Channel Technology

---

## 1. システムアーキテクチャ

### 1.1 全体構成

```
┌─────────────────────────────────────────────────────────────┐
│                        ユーザー層                            │
├─────────────────────────────────────────────────────────────┤
│  Web UI (Jinja2)  │  OpenClaw Skill (Python Client)        │
└──────────┬─────────────────────────────────┬────────────────┘
           │                                 │
           │ HTTP/REST API                   │ HTTP/REST API
           │                                 │
┌──────────▼─────────────────────────────────▼────────────────┐
│                   FastAPI Application                        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │    API      │  │   Services   │  │    ChromaDB      │   │
│  │   Routes    │  │  (Business)  │  │    Service       │   │
│  └──────┬──────┘  └──────┬───────┘  └──────────────────┘   │
│         │                │                                   │
│  ┌──────▼────────────────▼───────┐                          │
│  │      SQLAlchemy ORM            │                          │
│  └──────────────┬─────────────────┘                          │
└─────────────────┼────────────────────────────────────────────┘
                  │
         ┌────────▼────────┐
         │   SQLite3 DB    │
         │  (datas/db)     │
         └─────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              ChromaDB (Vector Store)                        │
│              (datas/chroma)                                 │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 レイヤー構造

```
src/
├── main.py                 # FastAPIアプリケーションエントリー
├── database.py             # SQLite接続管理
├── chroma_service.py       # ChromaDB接続管理
│
├── datas/                  # データ永続化（ボリュームマウント）
│   ├── database.db         # SQLiteデータベース（自動生成）
│   └── chroma/             # ChromaDB永続化データ（自動生成）
│
├── api/                    # APIルーター（プレゼンテーション層）
│   ├── __init__.py
│   ├── dishes.py           # 献立API
│   ├── recipes.py          # レシピAPI
│   ├── ingredients.py      # 食材API
│   ├── tags.py             # タグAPI
│   ├── search.py           # 検索API
│   ├── suggest.py          # 提案API
│   └── calendar.py         # カレンダーAPI
│
├── services/               # ビジネスロジック層
│   ├── __init__.py
│   ├── dish_service.py     # 献立サービス
│   ├── recipe_service.py   # レシピサービス
│   ├── search_service.py   # 検索サービス（ChromaDB連携）
│   └── suggest_service.py  # 提案サービス
│
├── models/                 # データモデル層
│   ├── __init__.py
│   ├── dish.py             # 献立モデル
│   ├── recipe.py           # レシピモデル
│   ├── ingredient.py       # 食材モデル
│   ├── tag.py              # タグモデル
│   └── calendar.py         # カレンダーモデル
│
├── schemas/                # Pydanticスキーマ（API入出力）
│   ├── __init__.py
│   ├── dish.py             # 献立スキーマ
│   ├── recipe.py           # レシピスキーマ
│   ├── ingredient.py       # 食材スキーマ
│   ├── tag.py              # タグスキーマ
│   └── calendar.py         # カレンダースキーマ
│
├── templates/              # Jinja2テンプレート
│   ├── base.html           # ベーステンプレート
│   ├── index.html          # トップページ
│   ├── dish_detail.html    # 献立詳細
│   ├── dish_edit.html      # 献立編集
│   ├── dish_new.html       # 献立新規作成
│   ├── calendar.html       # カレンダー
│   ├── admin.html          # 管理トップ
│   ├── admin_ingredients.html  # 食材管理
│   └── admin_tags.html     # タグ管理
│
└── static/                 # 静的ファイル
    ├── css/
    │   └── style.css
    └── js/
        └── app.js
```

---

## 2. データベース設計

### 2.1 ER図（テキスト表現）

```
┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│    dishes    │         │   recipes    │         │ ingredients  │
├──────────────┤         ├──────────────┤         ├──────────────┤
│ id (PK)      │────1:1─→│ id (PK)      │         │ id (PK)      │
│ name         │         │ dish_id (FK) │         │ name         │
│ type         │         │ steps (JSON) │         │ category     │
│ description  │         │ tips         │         │ season       │
│ difficulty   │         └──────────────┘         └───────┬──────┘
│ prep_time    │                                        │
│ calories     │         ┌──────────────┐              │
│ protein      │         │dish_ingredients│◄───────────┤
│ fat          │         ├──────────────┤              │
│ sodium       │         │ id (PK)      │              │
│ good_...     │         │ dish_id (FK) │              │
│ created_at   │         │ ingredient_id│              │
│ updated_at   │         │ amount       │              │
└──────┬───────┘         └──────────────┘              │
       │                                                 │
       │              ┌──────────────┐                  │
       │              │   tags       │                  │
       └─────────────→│────┬─────────┘                  │
              N:M    │ id (PK)      │                   │
              ┌──────│ name         │                   │
              │      └──────────────┘                   │
       ┌──────────────┐                                │
       │  dish_tags   │                                │
       ├──────────────┤                                │
       │ id (PK)      │                                │
       │ dish_id (FK) │                                │
       │ tag_id (FK)  │                                │
       └──────────────┘                                │
                                                        │
┌──────────────┐                                       │
│  calendar    │                                       │
├──────────────┤                                       │
│ id (PK)      │                                       │
│ date         │                                       │
│ main_dish... │───────────────────────────────────────┘
│ side1_dish... │
│ side2_dish... │
│ soup_dish...  │
└──────────────┘
```

### 2.2 テーブル詳細設計

#### 2.2.1 dishes（献立）

| カラム名 | データ型 | 制約 | 説明 |
|----------|----------|------|------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | 献立ID |
| name | TEXT | NOT NULL | 献立名 |
| type | TEXT | NOT NULL, CHECK(type IN ('main', 'side', 'soup')) | 献立タイプ |
| description | TEXT | | 説明 |
| difficulty | TEXT | CHECK(difficulty IN ('easy', 'medium', 'hard')) | 難易度 |
| prep_time | INTEGER | | 調理時間（分） |
| calories | REAL | | カロリー（kcal/人前） |
| protein | REAL | | タンパク質（g/人前） |
| fat | REAL | | 脂質（g/人前） |
| sodium | REAL | | 塩分（g/人前） |
| good_for_brain_health | BOOLEAN | DEFAULT 0 | 血栓の病気に良いか |
| created_at | TEXT | NOT NULL, DEFAULT CURRENT_TIMESTAMP | 作成日時 |
| updated_at | TEXT | NOT NULL, DEFAULT CURRENT_TIMESTAMP | 更新日時 |

**インデックス:**
```sql
CREATE INDEX idx_dishes_type ON dishes(type);
CREATE INDEX idx_dishes_brain_health ON dishes(good_for_brain_health);
CREATE INDEX idx_dishes_created ON dishes(created_at);
```

#### 2.2.2 recipes（レシピ）

| カラム名 | データ型 | 制約 | 説明 |
|----------|----------|------|------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | レシピID |
| dish_id | INTEGER | NOT NULL, FOREIGN KEY → dishes(id) | 献立ID |
| steps | TEXT | NOT NULL (JSON配列) | 調理手順 |
| tips | TEXT | | コツ・ヒント |

**インデックス:**
```sql
CREATE INDEX idx_recipes_dish_id ON recipes(dish_id);
```

#### 2.2.3 ingredients（食材）

| カラム名 | データ型 | 制約 | 説明 |
|----------|----------|------|------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | 食材ID |
| name | TEXT | NOT NULL, UNIQUE | 食材名 |
| category | TEXT | | カテゴリ（野菜、肉、魚、 etc.） |
| season | TEXT | | 旬の季節 |

**インデックス:**
```sql
CREATE INDEX idx_ingredients_name ON ingredients(name);
CREATE INDEX idx_ingredients_category ON ingredients(category);
```

#### 2.2.4 dish_ingredients（献立-食材関連）

| カラム名 | データ型 | 制約 | 説明 |
|----------|----------|------|------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | 関連ID |
| dish_id | INTEGER | NOT NULL, FOREIGN KEY → dishes(id) | 献立ID |
| ingredient_id | INTEGER | NOT NULL, FOREIGN KEY → ingredients(id) | 食材ID |
| amount | TEXT | NOT NULL | 分量 |

**インデックス:**
```sql
CREATE INDEX idx_dish_ingredients_dish ON dish_ingredients(dish_id);
CREATE INDEX idx_dish_ingredients_ingredient ON dish_ingredients(ingredient_id);
```

#### 2.2.5 tags（タグ）

| カラム名 | データ型 | 制約 | 説明 |
|----------|----------|------|------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | タグID |
| name | TEXT | NOT NULL, UNIQUE | タグ名 |

#### 2.2.6 dish_tags（献立-タグ関連）

| カラム名 | データ型 | 制約 | 説明 |
|----------|----------|------|------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | 関連ID |
| dish_id | INTEGER | NOT NULL, FOREIGN KEY → dishes(id) | 献立ID |
| tag_id | INTEGER | NOT NULL, FOREIGN KEY → tags(id) | タグID |

**インデックス:**
```sql
CREATE INDEX idx_dish_tags_dish ON dish_tags(dish_id);
CREATE INDEX idx_dish_tags_tag ON dish_tags(tag_id);
```

#### 2.2.7 calendar（カレンダー）

| カラム名 | データ型 | 制約 | 説明 |
|----------|----------|------|------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | カレンダーID |
| date | TEXT | NOT NULL, UNIQUE | 日付（ISO 8601） |
| main_dish_id | INTEGER | FOREIGN KEY → dishes(id) | 主菜 |
| side1_dish_id | INTEGER | FOREIGN KEY → dishes(id) | 副菜1 |
| side2_dish_id | INTEGER | FOREIGN KEY → dishes(id) | 副菜2 |
| soup_dish_id | INTEGER | FOREIGN KEY → dishes(id) | 汁物 |

**インデックス:**
```sql
CREATE INDEX idx_calendar_date ON calendar(date);
```

---

## 3. ChromaDB設計

### 3.1 コレクション構造

#### 3.1.1 dishesコレクション

**コレクション名:** `kondate_dishes`

**埋め込みモデル:** `all-MiniLM-L6-v2`（デフォルト）

**ドキュメント構造:**
```python
{
    "id": "dish_1",
    "document": "サバ缶ツナサラダ: キャベツとサバの水煮缶を使った簡単サラダ。EPA/DHAが豊富で血栓の病気に良い。",
    "metadata": {
        "dish_id": 1,
        "name": "サバ缶ツナサラダ",
        "type": "side",
        "calories": 180.0,
        "protein": 12.0,
        "sodium": 0.8,
        "good_for_brain_health": true
    }
}
```

**検索クエリ例:**
```python
# 食材からの検索
query = "キャベツ 卵 サバ"

# 説明からのセマンティック検索
query = "簡単で栄養のある副菜"

# メタデータフィルタ
where = {
    "type": "side",
    "good_for_brain_health": True
}
```

### 3.2 ChromaDB連携仕様

#### 3.2.1 データ追加・更新時

```python
async def sync_dish_to_chroma(dish_id: int):
    """献立データをChromaDBに同期"""
    dish = await get_dish_with_ingredients(dish_id)
    
    # ドキュメント構築
    ingredients_summary = ", ".join([i.name for i in dish.ingredients])
    document = f"{dish.name}: {dish.description}. 食材: {ingredients_summary}"
    
    # メタデータ構築
    metadata = {
        "dish_id": dish.id,
        "name": dish.name,
        "type": dish.type,
        "calories": dish.calories or 0,
        "protein": dish.protein or 0,
        "sodium": dish.sodium or 0,
        "good_for_brain_health": dish.good_for_brain_health or False
    }
    
    # ChromaDBに追加/更新
    collection.upsert(
        ids=[f"dish_{dish_id}"],
        documents=[document],
        metadatas=[metadata]
    )
```

#### 3.2.2 データ削除時

```python
async def remove_dish_from_chroma(dish_id: int):
    """献立データをChromaDBから削除"""
    collection.delete(ids=[f"dish_{dish_id}"])
```

---

## 4. API設計

### 4.1 共通仕様

#### 4.1.1 リクエスト/レスポンス形式

**Content-Type:** `application/json`

**共通レスポンス構造:**
```json
{
    "success": true,
    "data": {...},
    "error": null
}
```

**エラーレスポンス:**
```json
{
    "success": false,
    "data": null,
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "バリデーションエラーの詳細"
    }
}
```

#### 4.1.2 HTTPステータスコード

| コード | 説明 |
|--------|------|
| 200 | 成功 |
| 201 | 作成成功 |
| 400 | バリデーションエラー |
| 404 | リソース未検出 |
| 422 | リクエスト形式エラー |
| 500 | サーバーエラー |

### 4.2 APIエンドポイント詳細

#### 4.2.1 献立（Dishes）

**GET /api/dishes**
- **説明:** 献立一覧取得
- **クエリパラメータ:**
  - `type` (optional): `main` | `side` | `soup`
  - `good_for_brain_health` (optional): `true` | `false`
  - `limit` (optional): デフォルト50
  - `offset` (optional): デフォルト0
- **レスポンス:**
```json
{
    "success": true,
    "data": {
        "total": 10,
        "items": [
            {
                "id": 1,
                "name": "サバ缶ツナサラダ",
                "type": "side",
                "description": "キャベツとサバ缶で簡単サラダ",
                "difficulty": "easy",
                "prep_time": 10,
                "calories": 180.0,
                "protein": 12.0,
                "fat": 8.5,
                "sodium": 0.8,
                "good_for_brain_health": true,
                "tags": ["魚介類", "簡単"],
                "ingredients": [
                    {"name": "キャベツ", "amount": "1/4玉"},
                    {"name": "サバの水煮缶", "amount": "1/2缶"}
                ]
            }
        ]
    }
}
```

**GET /api/dishes/{id}**
- **説明:** 献立詳細取得
- **パスパラメータ:**
  - `id`: 献立ID
- **レスポンス:** 上記の単一オブジェクト

**POST /api/dishes**
- **説明:** 献立登録
- **リクエストボディ:**
```json
{
    "name": "サバ缶ツナサラダ",
    "type": "side",
    "description": "キャベツとサバ缶で簡単サラダ",
    "difficulty": "easy",
    "prep_time": 10,
    "calories": 180.0,
    "protein": 12.0,
    "fat": 8.5,
    "sodium": 0.8,
    "good_for_brain_health": true,
    "recipe": {
        "steps": [
            "キャベツを千切りにする",
            "サバ缶をほぐして混ぜる",
            "マヨネーズをかける"
        ],
        "tips": "マヨネーズはかけすぎないように"
    },
    "ingredients": [
        {"name": "キャベツ", "amount": "1/4玉"},
        {"name": "サバの水煮缶", "amount": "1/2缶"}
    ],
    "tags": ["魚介類", "簡単"]
}
```
- **処理:** 
  1. 献立データをDBに保存
  2. レシピを保存
  3. 食材をDBに登録/紐付け
  4. タグをDBに登録/紐付け
  5. ChromaDBに同期

**PUT /api/dishes/{id}**
- **説明:** 献立更新
- **リクエストボディ:** POSTと同じ（部分更新可能）
- **処理:** 更新後、ChromaDBに再同期

**DELETE /api/dishes/{id}**
- **説明:** 献立削除
- **処理:**
  1. 関連レシピを削除
  2. 関連食材紐付けを削除
  3. 関連タグ紐付けを削除
  4. ChromaDBから削除

#### 4.2.2 検索（Search）

**GET /api/search/dishes**
- **説明:** 献立名検索
- **クエリパラメータ:**
  - `q`: 検索クエリ
  - `type` (optional): フィルタ
- **処理:** SQLiteのLIKE検索

**GET /api/search/ingredients**
- **説明:** 食材から献立検索（ChromaDB）
- **クエリパラメータ:**
  - `q`: 食材クエリ（例: "キャベツ 卵"）
  - `n` (optional): 返却数、デフォルト5
- **処理:** ChromaDBでセマンティック検索
- **レスポンス:**
```json
{
    "success": true,
    "data": {
        "query": "キャベツ 卵",
        "results": [
            {
                "dish": {...},
                "similarity": 0.89
            }
        ]
    }
}
```

**GET /api/search/similar**
- **説明:** 類似献立検索
- **クエリパラメータ:**
  - `id`: 基準献立ID
  - `n` (optional): 返却数、デフォルト5
- **処理:** 指定献立のドキュメントでChromaDB検索

#### 4.2.3 提案（Suggest）

**GET /api/suggest**
- **説明:** 献立提案
- **クエリパラメータ:**
  - `prefer` (optional): `fish` | `meat` | `vegetable`
  - `max_sodium` (optional): 塩分上限、デフォルト3.0
- **処理:**
  1. 条件に合う献立を抽出
  2. 栄養バランスを考慮して組み合わせを生成
  3. ランダムに選択
- **レスポンス:**
```json
{
    "success": true,
    "data": {
        "main": {...},
        "side1": {...},
        "side2": {...},
        "soup": {...},
        "total_nutrition": {
            "calories": 850,
            "protein": 35,
            "sodium": 2.8
        }
    }
}
```

#### 4.2.4 カレンダー（Calendar）

**GET /api/calendar**
- **説明:** カレンダー取得
- **クエリパラメータ:**
  - `start` (optional): 開始日、デフォルト今日
  - `end` (optional): 終了日、デフォルト7日後
- **レスポンス:**
```json
{
    "success": true,
    "data": [
        {
            "date": "2025-01-23",
            "main": {...},
            "side1": {...},
            "side2": {...},
            "soup": {...}
        }
    ]
}
```

**POST /api/calendar/{date}**
- **説明:** カレンダー登録
- **リクエストボディ:**
```json
{
    "main_dish_id": 1,
    "side1_dish_id": 5,
    "side2_dish_id": 8,
    "soup_dish_id": 3
}
```

**PUT /api/calendar/{date}**
- **説明:** カレンダー更新

**DELETE /api/calendar/{date}**
- **説明:** カレンダー削除

---

## 5. OpenClawスキル設計

### 5.1 スキル構造

```
skills/kondate/
├── SKILL.md                 # スキルドキュメント
└── scripts/
    ├── __init__.py
    ├── client.py            # Pythonクライアント
    └── config.py            # 設定ファイル
```

### 5.2 Pythonクライアント設計

#### 5.2.1 クラス構造

```python
class KondateClient:
    """Kondate APIクライアント"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = httpx.AsyncClient()
    
    async def add_dish(self, dish_data: dict) -> dict:
        """献立登録"""
        ...
    
    async def search_dishes(self, query: str, **filters) -> list[dict]:
        """献立検索"""
        ...
    
    async def search_by_ingredients(self, query: str, n: int = 5) -> list[dict]:
        """食材から検索"""
        ...
    
    async def suggest(self, prefer: str = None, **options) -> dict:
        """献立提案"""
        ...
    
    async def update_dish(self, dish_id: int, **fields) -> dict:
        """献立更新"""
        ...
    
    async def get_dish(self, dish_id: int) -> dict:
        """献立詳細取得"""
        ...
```

#### 5.2.2 コマンドラインインターフェース

```bash
# 献立登録
uv run scripts/client.py add dish \
  --name "サバ缶ツナサラダ" \
  --type side \
  --description "キャベツとサバ缶で簡単サラダ" \
  --calories 180 \
  --protein 12 \
  --sodium 0.8 \
  --good-for-brain-health \
  --ingredients "キャベツ:1/4玉" "サバの水煮缶:1/2缶" \
  --steps "キャベツを千切りにする" "サバ缶をほぐして混ぜる" "マヨネーズをかける"

# 献立検索
uv run scripts/client.py search dish "サバ"

# 食材から検索
uv run scripts/client.py search ingredients "キャベツ 卵"

# 献立提案
uv run scripts/client.py suggest --prefer fish

# 献立更新
uv run scripts/client.py update dish --id 1 --calories 200
```

---

## 6. Web UI設計

### 6.1 ページ構成

#### 6.1.0 ナビゲーション設計

**共通ヘッダー（すべてのページ）:**
```
┌────────────────────────────────────────────────────────┐
│  Kondate                    🔍 [検索]  📅 カレンダー  │
│  ─────────────────────────────────────────────────────│
│  🏠 献立一覧  📅 カレンダー  ⚙️ 管理  ➕ 新規作成      │
└────────────────────────────────────────────────────────┘
```

**リンク先:**
- **🏠 献立一覧** → `/` （トップページ）
- **📅 カレンダー** → `/calendar`
- **⚙️ 管理** → `/admin`
- **➕ 新規作成** → `/dishes/new`
- **🔍 [検索]** → `/search` （検索結果ページ）

**パンくずリスト（詳細・編集ページ）:**
- 献立詳細: `🏠 献立一覧 > サバ缶ツナサラダ`
- 献立編集: `🏠 献立一覧 > サバ缶ツナサラダ > 編集`
- カレンダー: `🏠 献立一覧 > 📅 カレンダー`
- 管理: `🏠 献立一覧 > ⚙️ 管理`

**画面遷移図:**
```
/ (トップ)
  ├─→ /dishes/{id} (献立詳細)
  │     ├─→ /dishes/{id}/edit (編集)
  │     └─→ /dishes/new (新規作成)
  ├─→ /calendar (カレンダー)
  ├─→ /admin (管理トップ)
  │     ├─→ /admin/ingredients (食材管理)
  │     └─→ /admin/tags (タグ管理)
  └─→ /search (検索結果)
```

#### 6.1.1 トップページ（/）

**構成要素:**
- ヘッダー（タイトル + ナビゲーション）
- 検索バー
- タブ（主菜 | 副菜 | 汁物 | すべて）
- 献立カード一覧
- フッター

**献立カード:**
```
┌─────────────────────────────┐
│ サバ缶ツナサラダ             │
│ 副菜 | 簡単 | 10分           │
│ 180kcal | タンパク質 12g     │
│ ✓ 血栓の病気に良い          │
│ タグ: 魚介類, 簡単          │
└─────────────────────────────┘
```

#### 6.1.2 献立詳細ページ（/dishes/{id}）

**構成要素:**
- 献立情報（名前、説明、栄養、タグ）
- レシピ（材料、調理手順）
- 関連献立（類似料理）
- 編集ボタン（Web UIのみ）

#### 6.1.3 献立編集ページ（/dishes/{id}/edit）

**構成要素:**
- 献立情報入力フォーム
- レシピ入力フォーム（動的ステップ追加）
- 食材選択・追加（オートコンプリート）
- タグ選択・追加
- 保存ボタン

#### 6.1.4 カレンダーページ（/calendar）

**構成要素:**
- 週間カレンダー表示
- 日付クリックで献立登録モーダル
- 献立ドロップダウン選択
- 保存ボタン

#### 6.1.5 管理ページ（/admin）

**構成要素:**
- 食材マスター管理（一覧、追加、編集、削除）
- タグ管理（一覧、追加、編集、削除）
- データエクスポート/インポート（将来的な拡張）

### 6.2 デザイン原則

#### 6.2.1 カラースキーム

- メインカラー: `#FF6B6B`（温かみのある赤）
- サブカラー: `#4ECDC4`（爽やかな青緑）
- 背景色: `#F7F7F7`
- テキストカラー: `#333`

#### 6.2.2 レスポンシブデザイン

- モバイルファースト
- ブレークポイント: 768px
- カードグリッド: モバイル1列、タブレット2列、デスクトップ3列

#### 6.2.3 アクセシビリティ

- 適切なコントラスト比
- キーボードナビゲーション対応
- スクリーンリーダー対応（ARIAラベル）

---

## 7. インフラ設計

### 7.1 Docker構成

#### 7.1.1 Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# uvをインストール
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# 依存関係をコピー
COPY pyproject.toml ./

# 依存関係をインストール
RUN uv sync --frozen

# ソースコードをコピー
COPY ./src ./src

# データディレクトリを作成
RUN mkdir -p /app/src/datas

# ポートを公開
EXPOSE 8000

# コマンドを実行
CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 7.1.2 docker-compose.yml

```yaml
version: '3.8'

services:
  kondate:
    build: .
    ports:
      - "10141:8000"
    volumes:
      - ./datas:/app/src/datas
    environment:
      - DATABASE_URL=sqlite:///./src/datas/database.db
      - CHROMA_PERSIST_DIRECTORY=/app/src/datas/chroma
    restart: unless-stopped
```

### 7.2 ボリュームマウント設計

| パス | 用途 |
|------|------|
| `./src/datas` | SQLiteデータ + ChromaDB永続化データ |

**ボリューム内構造:**
```
src/datas/
├── database.db         # SQLiteデータベース（自動生成）
└── chroma/             # ChromaDB永続化データ（自動生成）
    ├── chroma.sqlite3  # ChromaDB内部DB
    └── ...             # その他ChromaDBファイル
```

---

## 8. セキュリティ設計

### 8.1 入力バリデーション

- Pydanticスキーマによるバリデーション
- SQLインジェクション対策（SQLAlchemyパラメータ化クエリ）
- XSS対策（Jinja2自動エスケープ）

### 8.2 エラーハンドリング

- 例外情報の露出を回避
- 適切なHTTPステータスコード返却
- エラーログの記録

---

## 9. パフォーマンス設計

### 9.1 データベース

- 適切なインデックス設計
- N+1クエリ回避（eager loading）
- コネクションプール（SQLAlchemyデフォルト）

### 9.2 ChromaDB

- ベクトル検索の結果キャッシュ（将来的な拡張）
- バッチ処理による同期最適化

### 9.3 API

- レスポンスのページネーション
- 圧縮（gzip）有効化

---

## 10. テスト設計

### 10.1 テスト戦略

- 単体テスト: サービス層
- 統合テスト: APIエンドポイント
- E2Eテスト: 将来的な拡張

### 10.2 テストツール

- pytest
- httpx（非同期HTTPクライアント）
- pytest-asyncio

---

## 11. デプロイ設計

### 11.1 ローカル開発

```bash
# 開発サーバー起動
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### 11.2 Dockerデプロイ

```bash
# ビルド＆起動
docker-compose up --build

# バックグラウンド起動
docker-compose up -d
```

### 11.3 本番環境（将来的な拡張）

- Gunicorn + Uvicorn workers
- Nginxリバースプロキシ
- Let's Encrypt HTTPS

---

## 12. ログ設計

### 12.1 ログレベル

| レベル | 用途 |
|--------|------|
| DEBUG | 開発時の詳細情報 |
| INFO | 通常の操作ログ |
| WARNING | 警告 |
| ERROR | エラー |

### 12.2 ログ出力先

- 標準出力（Dockerログドライバ）
- 将来的にはファイルローテーション

---

**文書終了**
