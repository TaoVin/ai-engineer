# 全局异常处理
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.responses import JSONResponse


# 自定义业务异常类
class BusinessError(Exception):
    def __init__(
        self,
        code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        message: str = "系统异常",
        data: any = None,
    ):
        self.code = code
        self.message = message
        self.data = data


# 注册全局异常处理
def setup_exception_handlers(app: FastAPI):

    @app.exception_handler(StarletteHTTPException)
    async def http_exception(request: Request, exception: StarletteHTTPException):
        return JSONResponse(
            status_code=exception.status_code,
            content={
                "code": exception.status_code,
                "message": exception.detail,
                "data": None,
            },
        )

    # 2. 处理请求参数验证异常（Pydantic 校验失败）
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        # 提取详细的字段错误信息
        errors = []
        for err in exc.errors():
            field = ".".join(str(loc) for loc in err["loc"])
            errors.append({"field": field, "message": err["msg"]})

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "code": 422,
                "message": "Request validation failed",
                "data": errors,
            },
        )

    # 3. 处理自定义业务异常
    @app.exception_handler(BusinessError)
    async def business_exception_handler(request: Request, exc: BusinessError):
        return JSONResponse(
            status_code=exc.code,  # 可设为 400 或更合适的状态码
            content={"code": exc.code, "message": exc.message, "data": None},
        )

    # 4. 兜底：捕获所有未预期的异常（可选，放在最后）
    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        # 实际生产环境中建议记录日志
        # logger.error(f"Unhandled exception: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"code": 500, "message": "Internal server error", "data": None},
        )
