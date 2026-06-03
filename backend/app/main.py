import sys
from pathlib import Path

# 将项目根目录加入 sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from fastapi import FastAPI
from app.config.settings import setting


def create_app() -> FastAPI:
    app = FastAPI(
        title=setting.TITLE,
        version=setting.VERSION,
        summary=setting.SUMMARY,
        description=setting.DESCRIPTION,
        docs_url=setting.DOCS_URL,
        redoc_url=setting.REDOC_URL,
        root_path=setting.ROOT_PATH,
        debug=setting.DEBUG,
    )
    return app
