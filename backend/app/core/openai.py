# ai 相关
from app.config.settings import setting
from openai import AsyncOpenAI
import json
from typing import AsyncIterable, List
from openai.types.chat import ChatCompletionMessageParam

# 定义client

async def get_client() -> AsyncOpenAI:
    return  AsyncOpenAI(base_url=setting.OPENAI_BASE_URL, api_key=setting.OPENAI_API_KEY)
    
    
async def stream_ai_response(
    messages: List[ChatCompletionMessageParam],
    client: AsyncOpenAI,
    model: str = setting.OPENAI_MODEL,
) -> AsyncIterable[str]:
    """
    通用的 AI 流式响应生成器，逐 token 推送 JSON 格式的数据。

    Args:
        messages: 完整的对话历史，格式 [{"role": "user", "content": "..."}, ...]
        client: AsyncOpenAI 客户端实例
        model: 模型名称

    Yields:
        JSON 字符串，格式 {"type": "token", "content": "xxx"} 或 {"type": "error", "content": "..."}
    """
    print(f"message:{messages}")
    try:
        stream = await client.chat.completions.create(model=model, messages= messages, stream=True,)
        async for chunk in stream:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta
            if delta.content:
                yield json.dumps({"type": "token", "content": delta.content})

        # 发送完成信号
        yield json.dumps({"type": "done", "content": ""})

    except Exception as e:
        # 将错误也以流的形式发送给客户端（前端可据此处理）
        yield json.dumps({"type": "error", "content": str(e)})
