# ベースイメージ
FROM python:3.11-slim

# 作業ディレクトリ
WORKDIR /app

# システム依存関係のインストール
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# uvのインストール
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# 依存関係ファイルのコピー（キャッシュ最適化）
COPY pyproject.toml ./
COPY uv.lock ./

# 依存関係のインストール（uvキャッシュ効率化）
RUN uv sync --frozen --no-dev

# ソースコードのコピー
COPY . .

# ChromaDBデータディレクトリの作成
RUN mkdir -p datas/chroma && \
    chmod 777 datas/chroma

# 環境変数
ENV PYTHONUNBUFFERED=1
ENV API_PORT=10141

# ヘルスチェック
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:10141/docs || exit 1

# ポート公開
EXPOSE 10141

# 起動コマンド（仮想環境を再作成しない）
CMD [".venv/bin/uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "10141"]
