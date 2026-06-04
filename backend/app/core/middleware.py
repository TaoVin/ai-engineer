import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.utils.logger import log_request

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件"""
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """
        处理请求
        
        Args:
            request: 请求对象
            call_next: 下一个中间件
        
        Returns:
            响应对象
        """
        # 记录开始时间
        start_time = time.time()
        
        # 获取客户端 IP
        client_ip = request.client.host if request.client else "unknown"
        
        # 处理请求
        response = await call_next(request)
        
        # 计算耗时
        duration = time.time() - start_time
        
        # 记录请求日志
        log_request({
            "method": request.method,
            "url": str(request.url),
            "client_ip": client_ip,
            "status_code": response.status_code,
            "duration": duration,
        })
        
        return response