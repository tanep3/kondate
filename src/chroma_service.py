"""
ChromaDB接続管理
献立のセマンティック検索用
"""

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import os


class ChromaService:
    """ChromaDBサービスクラス"""

    def __init__(self):
        """ChromaDBクライアントを初期化"""
        # 永続化ディレクトリ
        persist_dir = os.getenv(
            "CHROMA_PERSIST_DIRECTORY",
            "./src/datas/chroma"
        )

        # ディレクトリが存在しない場合は作成
        if not os.path.exists(persist_dir):
            os.makedirs(persist_dir, exist_ok=True)

        # 日本語埋め込みモデルをロード
        embedding_model_name = os.getenv(
            "EMBEDDING_MODEL",
            "cl-nagoya/ruri-small-v2"  # 高性能日本語埋め込みモデル（Apache 2.0ライセンス）
        )
        print(f"Loading embedding model: {embedding_model_name}")
        self.embedding_model = SentenceTransformer(
            embedding_model_name,
            device="cpu",
            trust_remote_code=True  # リモートコードを信頼（tokenizer問題回避）
        )
        print("Embedding model loaded successfully")

        # ChromaDBクライアント作成
        self.client = chromadb.PersistentClient(
            path=persist_dir,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )

        # コレクション名
        self.collection_name = "kondate_dishes"
        self.collection = None

    def _encode(self, texts):
        """テキストをエンコード（正規化付き）"""
        import numpy as np
        embeddings = self.embedding_model.encode(texts, convert_to_numpy=True)
        # L2正規化を適用してコサイン類似度を計算可能にする
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        normalized_embeddings = embeddings / norms
        return normalized_embeddings.tolist()

    def get_collection(self):
        """コレクションを取得または作成"""
        if self.collection is None:
            try:
                # 埋め込み関数なしでコレクションを取得
                self.collection = self.client.get_collection(
                    name=self.collection_name
                )
            except:
                # コレクションが存在しない場合は作成
                self.collection = self.client.create_collection(
                    name=self.collection_name,
                    metadata={"description": "献立のベクトルデータ"}
                )
        return self.collection

    def add_dish(self, dish_id: int, document: str, metadata: dict):
        """
        献立をChromaDBに追加

        Args:
            dish_id: 献立ID
            document: 検索用ドキュメント（献立名 + 説明 + 食材）
            metadata: メタデータ（タイプ、栄養素など）
        """
        collection = self.get_collection()

        # 手動で埋め込みを生成
        embeddings = self._encode([document])

        collection.upsert(
            ids=[f"dish_{dish_id}"],
            embeddings=embeddings,
            documents=[document],
            metadatas=[metadata]
        )

    def update_dish(self, dish_id: int, document: str, metadata: dict):
        """献立を更新（add_dishと同じ、upsertで対応）"""
        self.add_dish(dish_id, document, metadata)

    def delete_dish(self, dish_id: int):
        """献立を削除"""
        collection = self.get_collection()
        collection.delete(ids=[f"dish_{dish_id}"])

    def search(self, query: str, n_results: int = 5, where: dict = None):
        """
        献立を検索

        Args:
            query: 検索クエリ
            n_results: 返却数
            where: メタデータフィルタ

        Returns:
            検索結果
        """
        collection = self.get_collection()

        # 手動でクエリを埋め込み
        query_embeddings = self._encode([query])

        results = collection.query(
            query_embeddings=query_embeddings,
            n_results=n_results,
            where=where
        )
        return results

    def reset(self):
        """データベースをリセット（開発用）"""
        try:
            # コレクションを削除
            self.client.delete_collection(name=self.collection_name)
            self.collection = None
            print("ChromaDB collection reset successfully")
        except Exception as e:
            print(f"Error resetting ChromaDB: {e}")
            # コレクションが存在しない場合は無視
            self.collection = None


# グローバルインスタンス
chroma_service = ChromaService()
