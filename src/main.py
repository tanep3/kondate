"""
Kondate - 献立管理システム
FastAPIアプリケーションエントリーポイント
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Request
from sqlalchemy.orm import Session
import os

# データベース接続をインポート
from src.database import engine, Base, get_db

# モデルをインポート（必須：テーブル作成のため）
from src.models import dish, recipe, calendar  # noqa: F401

# APIルーターをインポート
from src.api import dishes, search, suggest, calendar, nutrition

# アプリケーション作成
app = FastAPI(
    title="Kondate - 献立管理システム",
    description="血栓の病気を考慮した献立管理・提案システム",
    version="1.0.0"
)

# テーブル作成（初回起動時のみ）
Base.metadata.create_all(bind=engine)

# テンプレート・静的ファイル設定
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# Jinja2フィルタを追加
def type_label(type_str):
    labels = {
        'main': '主菜',
        'side': '副菜',
        'soup': '汁物',
        'staple': '主食',
        'dessert': 'デザート'
    }
    return labels.get(type_str, type_str)

def difficulty_label(difficulty_str):
    labels = {
        'easy': '簡単',
        'medium': '普通',
        'hard': '難しい'
    }
    return labels.get(difficulty_str, difficulty_str)

templates.env.filters['type_label'] = type_label
templates.env.filters['difficulty_label'] = difficulty_label

# APIルーターを登録
app.include_router(dishes.router)
app.include_router(search.router)
app.include_router(suggest.router)
app.include_router(calendar.router)
app.include_router(nutrition.router)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """トップページ"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/dishes/new", response_class=HTMLResponse)
async def dish_new(request: Request):
    """献立新規作成ページ"""
    return templates.TemplateResponse(
        "dish_form.html",
        {
            "request": request,
            "dish_id": None
        }
    )


@app.get("/dishes/{dish_id}", response_class=HTMLResponse)
async def dish_detail(dish_id: int, request: Request, db: Session = Depends(get_db)):
    """献立詳細ページ"""
    from src.services.dish_service import DishService
    from src.services.search_service import SearchService

    # 献立を取得
    service = DishService(db)
    dish = service.get_by_id(dish_id)

    if not dish:
        raise HTTPException(status_code=404, detail="献立が見つかりません")

    # 関連献立を取得（将来的な拡張）
    search_service = SearchService(db)
    similar_dishes = search_service.search_similar(dish_id, n_results=3)

    # SQLAlchemyオブジェクトを辞書に変換
    dish_dict = dish.to_dict()
    if dish.recipe:
        dish_dict["recipe"] = dish.recipe.to_dict()
    if dish.ingredients:
        dish_dict["ingredients"] = [di.to_dict() for di in dish.ingredients]
    if dish.tags:
        dish_dict["tags"] = [dt.tag.to_dict() for dt in dish.tags]

    return templates.TemplateResponse(
        "dish_detail.html",
        {
            "request": request,
            "dish": dish_dict,
            "similar_dishes": similar_dishes
        }
    )


@app.get("/dishes/{dish_id}/edit", response_class=HTMLResponse)
async def dish_edit(dish_id: int, request: Request, db: Session = Depends(get_db)):
    """献立編集ページ"""
    from src.services.dish_service import DishService

    # 献立が存在するか確認
    service = DishService(db)
    dish = service.get_by_id(dish_id)

    if not dish:
        raise HTTPException(status_code=404, detail="献立が見つかりません")

    return templates.TemplateResponse(
        "dish_form.html",
        {
            "request": request,
            "dish_id": dish_id
        }
    )


@app.get("/calendar", response_class=HTMLResponse)
async def calendar_page(request: Request):
    """カレンダーページ"""
    return templates.TemplateResponse("calendar.html", {"request": request})


@app.get("/health")
async def health_check():
    """ヘルスチェック"""
    return {"status": "ok", "message": "Kondate system is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
