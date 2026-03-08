# Kondate - 献立管理システム

料理初心者向けの献立管理・提案システム。栄養バランスを考慮しつつ、簡単に献立を考えられます。

**バージョン:** 1.0  
**リリース日:** 2026-03-08  
**ライセンス:** MIT

---

## 🌟 特徴

- **1日3食対応**: 朝食・昼食・夕食を管理
- **5献立タイプ**: 主菜、副菜、汁物、主食、デザート
- **栄養計算**: 年代・性別別の推奨値との比較
- **人数考慮**: レシピの人数で自動的に1人前に換算
- **セマンティック検索**: ChromaDBによるあいまい検索
- **AI提案**: 栄養バランスを考慮した献立提案
- **WebUI**: レスポンシブデザイン、ダークテーマ対応
- **OpenClaw Skill**: AIから献立管理・提案が可能

---

## 🎯 ターゲット

- 料理が苦手な人
- 家族の健康管理をしたい人
- 療養中の家族がいる人（塩分・栄養管理）

---

## 🚀 クイックスタート

### Dockerで実行（推奨）

```bash
git clone https://github.com/tanep3/kondate.git
cd kondate
docker-compose up --build
```

ブラウザで `http://localhost:10141` にアクセス。

### ローカルで実行

```bash
git clone https://github.com/tanep3/kondate.git
cd kondate
uv sync
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 10141
```

---

## 📖 ドキュメント

- [インストールガイド](./docs/installation.md) - Docker・ローカル開発環境
- [APIリファレンス](./docs/api.md) - REST API仕様
- [要件定義書](./docs/requirements.md) - システム要件
- [システム設計書](./docs/design.md) - アーキテクチャ

---

## 🤖 OpenClaw Skill

**このシステムはOpenClaw Skillとして機能します。**

### Skillのインストール

**重要:** 以下のコマンドでSkillをOpenClaw workspaceにコピーしてください。

```bash
# OpenClaw workspaceのパス（例）
OPENCLAW_SKILLS="/home/<user>/clawd/skills/public"

# Skillをコピー
cp -r skills/public/kondate "$OPENCLAW_SKILLS/"

# 確認
ls "$OPENCLAW_SKILLS/kondate/"
```

### Skillの使用例

```bash
# 献立一覧取得
cd /home/<user>/clawd/skills/public/kondate
uv run python3 scripts/client.py get-dishes

# 献立作成
uv run python3 scripts/client.py create-dish \
  --name "焼き魚" \
  --type main

# カレンダー登録
uv run python3 scripts/client.py register-calendar \
  --date 2026-03-15 \
  --meal-type dinner \
  --dish-ids 3 5 7

# 栄養計算
uv run python3 scripts/client.py calculate-nutrition \
  --date 2026-03-15 \
  --target "50代男性"
```

詳細は [SKILL.md](./skills/public/kondate/SKILL.md) を参照してください。

---

## 🎨 WebUI機能

- 献立一覧・詳細・作成・編集・削除
- カレンダー（月間表示、日付選択）
- タブフィルタリング（主菜、副菜、汁物、主食、デザート）
- セマンティック検索
- タグ検索
- 栄養計算
- レシピ表示（材料、調理手順、コツ・ヒント）

---

## 🔧 APIエンドポイント

| エンドポイント | 説明 |
|---------------|------|
| `GET /api/dishes` | 献立一覧取得 |
| `POST /api/dishes` | 献立作成 |
| `PUT /api/dishes/{id}` | 献立更新 |
| `DELETE /api/dishes/{id}` | 献立削除 |
| `GET /api/search/dishes` | 献立検索（セマンティック） |
| `GET /api/suggest` | 献立提案 |
| `GET /api/calendar` | カレンダー取得 |
| `POST /api/calendar` | カレンダー登録 |
| `PUT /api/calendar/{date}` | カレンダー更新 |
| `DELETE /api/calendar/{date}` | カレンダー削除 |
| `GET /api/nutrition/calculate` | 栄養計算 |

詳細は [APIリファレンス](./docs/api.md) を参照してください。

---

## 🧪 テスト

```bash
# Skillテスト
cd skills/public/kondate
uv run python3 scripts/test_client.py --test all
```

---

## 📊 技術スタック

- **バックエンド**: Python 3.11+, FastAPI, SQLAlchemy
- **データベース**: SQLite
- **ベクトルDB**: ChromaDB
- **エンベディング**: `cl-nagoya/ruri-small-v2`
- **フロントエンド**: Jinja2, Vanilla JavaScript
- **パッケージ管理**: uv
- **コンテナ**: Docker, Docker Compose

---

## 📝 データ構造

### 献立タイプ

- `main` - 主菜（肉・魚・卵・大豆製品）
- `side` - 副菜（野菜・海藻・きのこ）
- `soup` - 汁物（味噌汁・スープ）
- `staple` - 主食（ごはん・パン・麺）
- `dessert` - デザート（果物・ヨーグルト）

### 食事タイプ

- `breakfast` - 朝食
- `lunch` - 昼食
- `dinner` - 夕食

---

## 🍽️ 栄養考慮

- **血栓の病気に良い**: 低塩分、高タンパク質、EPA/DHA豊富
- **人数考慮**: レシピの人数で自動的に1人前に換算
- **推奨値との比較**: 30代〜80代の男女別に対応

---

## 🔄 バージョン履歴

### v2.0 (2026-03-08)

- ✅ 1日3食対応
- ✅ 5献立タイプ追加（主食、デザート）
- ✅ 人数考慮機能
- ✅ 栄養情報総量化
- ✅ 409エラーハンドリング強化
- ✅ Skillイテレーション方式
- ✅ Docker最適化

### v1.0 (2025-01-23)

- 初版リリース

---

## 👥 貢献

バグ報告・機能リクエストは [GitHub Issues](https://github.com/your-org/kondate/issues) まで。

---

## 📄 ライセンス

MIT License

---

## 🙏謝辞

- **OpenClaw**: AIフレームワーク
- **ChromaDB**: ベクトルデータベース
- **FastAPI**: Webフレームワーク
- **cl-nagoya**: 日本語エンベディングモデル `cl-nagoya/ruri-small-v2`

---

**Made with ❤️ by Tane Channel Technology**
