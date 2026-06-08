from pydantic import BaseModel, Field


class LoginDto(BaseModel):
    """登陆参数"""
    
    user_name: str = Field(..., description="登录账号")
    user_pwd: str = Field(..., description="密码")
    code: str = Field(..., description="认证码")
    
    
class LoginResponse(BaseModel):
    access_token: str = Field(..., description="访问token")
    refresh_token: str = Field(..., description="访问token")
    
    
    
class RefreshTokenRequest(BaseModel):
    """刷新 Token 请求"""
    refresh_token: str