# インストールガイド: Kondate - 献立管理システム

**バージョン:** 1.0  
**作成日:** 2026-03-08  
**作成者:** Amaterasu(OpenClaw) & Tane Channel Technology

---

## 1. Dockerで実行（推奨）

### 1.1 前提条件

- Docker 20.10+
- Docker Compose 2.0+

### 1.2 クイックスタート

```bash
# 1. リポジトリのクローン
git clone https://github.com/tanep3/kondate.git
cd kondate

# 2. ビルド＆起動
docker compose up --build

# 3. ブラウザでアクセス
open http://localhost:10141
```

### 1.3 初回起動の確認

初回起動時、以下が自動的に作成されます:

- `datas/database.db` - SQLiteデータベース
- `datas/chroma/` - ChromaDBベクトルデータ

### 1.4 再ビルドの高速化

2回目以降のビルドは高速です:

```bash
# ソースコードのみ変更
docker compose up --build

# 依存関係変更時のみフルビルド
docker compose build --no-cache
```

**高速化の理由:**
- `pyproject.toml`、`uv.lock`変更時のみ依存関係再インストール
- uvキャッシュがボリュームマウントで永続化
- レイヤーキャッシュが効いている

---

## 2. ローカル開発（uv）

### 2.1 前提条件

- Python 3.11+
- uv（Pythonパッケージマネージャー）

### 2.2 uvのインストール

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2.3 依存関係のインストール

```bash
# リポジトリのクローン
git clone https://github.com/tanep3/kondate.git
cd kondate

# 依存関係のインストール
uv sync

# ChromaDBベクトルの生成（必要に応じて）
uv run python scripts/regenerate_chroma.py
```

### 2.4 サーバー起動

```bash
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 10141
```

### 2.5 ブラウザでアクセス

```
http://localhost:10141
```

---

## 3. 初期データの登録

### 3.1 サンプル献立の登録

```bash
# Pythonクライアントを使用
cd skills/public/kondate
uv run python3 scripts/test_client.py --test all
```

### 3.2 ChromaDBベクトルの再生成

```bash
uv run python3 scripts/regenerate_chroma.py
```

---

## 4. Docker運用

### 4.1 コンテナ管理

```bash
# 起動
docker compose up -d

# 停止
docker compose stop

# 再起動
docker compose restart

# ログ確認
docker compose logs -f

# コンテナ削除
docker compose down

# データも含めて完全削除
docker compose down -v
```

### 4.2 データバックアップ

```bash
# データディレクトリのバックアップ
tar -czf kondate-backup-$(date +%Y%m%d).tar.gz datas/
```

### 4.3 データリストア

```bash
# バックアップのリストア
tar -xzf kondate-backup-20260308.tar.gz
```

---

## 5. 環境変数

### 5.1 環境変数一覧

| 変数名 | デフォルト値 | 説明 |
|--------|-------------|------|
| `TZ` | `Asia/Tokyo` | タイムゾーン |
| `PYTHONUNBUFFERED` | `1` | Pythonログバッファ無効化 |
| `API_PORT` | `10141` | APIポート |

### 5.2 環境変数の設定

**Dockerの場合:**
```yaml
# docker-compose.yml
environment:
  - TZ=Asia/Tokyo
  - API_PORT=10141
```

**ローカルの場合:**
```bash
export TZ=Asia/Tokyo
export API_PORT=10141
uv run uvicorn src.main:app --port $API_PORT
```

---

## 6. トラブルシューティング

### 6.1 ポート競合

**エラー:** `Address already in use`

**解決策:**
```bash
# ポート10141を使用しているプロセスを確認
lsof -i :10141

# ポートを変更
export API_PORT=10142
uv run uvicorn src.main:app --port $API_PORT
```

### 6.2 ChromaDBエラー

**エラー:** `ChromaDB connection failed`

**解決策:**
```bash
# ChromaDBデータを削除して再生成
rm -rf datas/chroma/
uv run python3 scripts/regenerate_chroma.py
```

### 6.3 依存関係エラー

**エラー:** `Module not found`

**解決策:**
```bash
# 依存関係を再インストール
uv sync --reinstall
```

### 6.4 Dockerビルドが遅い

**解決策:**
```bash
# キャッシュをクリアして再ビルド
docker compose build --no-cache

# uvキャッシュボリュームを確認
docker volume ls | grep uv
```

---

## 7. ヘルスチェック

### 7.1 APIエンドポイント

```bash
# APIドキュメント（Swagger UI）
curl http://localhost:10141/docs

# 献立一覧
curl http://localhost:10141/api/dishes

# カレンダー
curl http://localhost:10141/api/calendar?year=2026&month=3
```

### 7.2 ヘルスチェック

```bash
# Dockerヘルスチェック
docker compose ps

# 手動チェック
curl -f http://localhost:10141/docs || exit 1
```

---

## 8. 本番環境へのデプロイ

### 8.1 推奨構成

- **リバースプロキシ:** Nginx
- **HTTPS:** Let's Encrypt
- **ファイアウォール:** UFW
- **バックアップ:** cron + rsync

### 8.2 Nginx設定例

```nginx
server {
    listen 80;
    server_name kondate.example.com;

    location / {
        proxy_pass http://localhost:10141;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 8.3 サービス登録（systemd）

```ini
[Unit]
Description=Kondate Meal Planning System
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/home/your-user/kondate
Environment="PATH=/home/your-user/.local/bin:/usr/bin"
Environment="TZ=Asia/Tokyo"
ExecStart=/home/your-user/.local/bin/uv run uvicorn src.main:app --host 0.0.0.0 --port 10141
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

---

## 9. アンインストール

### 9.1 Docker環境

```bash
# コンテナとボリュームの削除
docker compose down -v

# イメージの削除
docker rmi kondate-kondate

# データの削除
rm -rf datas/
```

### 9.2 ローカル環境

```bash
# 仮想環境の削除
rm -rf .venv/

# データの削除
rm -rf datas/
```

---

**インストール完了後は:**
- [APIリファレンス](./api.md) を参照
- [要件定義書](./requirements.md) を確認
- [システム設計書](./design.md) を理解

---

**文書終了**
