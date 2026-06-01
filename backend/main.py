from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from config.exception import setup_exception_handlers

app = FastAPI()

# 全局异常注册
setup_exception_handlers(app)
