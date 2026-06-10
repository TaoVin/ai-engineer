# AI 应用工程学习计划

> 以项目为主导，技术栈：**Python FastAPI + LangChain + React + TypeScript + Next.js**
> 
> 非固定时间表，根据实际工作灵活调整进度。

---

## 技术栈说明

| 层级 | 技术 | 用途 |
|------|------|------|
| 后端 | Python + FastAPI | AI 服务、API 接口 |
| AI 框架 | LangChain + LangGraph | RAG、Agent 编排 |
| 前端 | React + TypeScript + Next.js | Web UI |
| 数据库 | PostgreSQL + pgvector | 向量存储 |
| 缓存 | Redis | 会话、缓存 |
| 部署 | Docker + Docker Compose | 容器化 |

---

## 项目驱动学习路线

### 项目总览

```
Phase 1: AI Chat 应用          → 掌握 LLM 调用基础
Phase 2: RAG 知识库系统        → 掌握检索增强生成
Phase 3: Agent 智能助手        → 掌握工具调用与编排
Phase 4: AI 平台（可选）       → 掌握多模型管理与成本控制
```

---

## Phase 1：AI Chat 应用

**目标**：构建一个支持流式输出、多轮对话的 AI 聊天应用

### 1.1 后端基础

#### 学习内容
- Python 异步编程（asyncio）
- FastAPI 框架基础
- Pydantic 数据模型
- OpenAI API 调用

#### 实现功能
```python
# 核心 API
POST /api/chat          # 普通对话
POST /api/chat/stream   # 流式对话
GET  /api/conversations # 对话列表
GET  /api/conversations/{id}/messages  # 历史消息
```

#### 项目结构
```
ai-chat-app/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── chat.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── llm.py
│   │   ├── models/
│   │   │   └── conversation.py
│   │   ├── services/
│   │   │   └── chat_service.py
│   │   └── main.py
│   ├── requirements.txt
│   └── Dockerfile
└── frontend/
    └── ... (下一步)
```

#### 关键代码点
- 流式输出（SSE）
- 会话历史管理
- 错误处理与重试
- API Key 安全存储

#### 交付物
- [x] FastAPI 项目骨架
- [x] 流式对话 API
- [x] 多轮对话支持
- [x] API 文档（自动生成）

---

### 1.2 前端基础

#### 学习内容
- Next.js App Router
- TypeScript 基础
- React Server Components
- Tailwind CSS

#### 实现功能
```tsx
// 页面结构
/                    → 首页
/chat                → 对话页面
/chat/[id]           → 具体对话
```

#### 核心组件
```tsx
// 关键组件
ChatInput         // 输入框
MessageList       // 消息列表
MessageBubble     // 消息气泡
StreamingText     // 流式文本渲染
MarkdownRenderer  // Markdown 渲染
CodeBlock         // 代码高亮
```

#### 项目结构
```
frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   └── chat/
│   │       └── page.tsx
│   ├── components/
│   │   ├── chat/
│   │   │   ├── ChatInput.tsx
│   │   │   ├── MessageList.tsx
│   │   │   └── StreamingText.tsx
│   │   └── ui/
│   ├── hooks/
│   │   └── useChat.ts
│   ├── lib/
│   │   └── api.ts
│   └── types/
│       └── chat.ts
├── package.json
└── tailwind.config.ts
```

#### 关键代码点
- SSE 客户端处理
- 流式文本逐字渲染
- 消息状态管理
- 响应式布局

#### 交付物
- [ ] Next.js 项目骨架
- [ ] 对话页面 UI
- [ ] 流式消息渲染
- [ ] Markdown + 代码高亮

---

### 1.3 功能完善

#### 增强功能
- [ ] 对话历史持久化（SQLite/PostgreSQL）
- [ ] 对话重命名、删除
- [ ] System Prompt 自定义
- [ ] Temperature 参数调节
- [ ] 消息复制、重新生成
- [ ] 暗色模式

#### 部署
- [ ] Docker Compose 编排
- [ ] 环境变量配置
- [ ] 基础监控

---

## Phase 2：RAG 知识库系统

**目标**：在 Chat 基础上增加文档问答能力

### 2.1 文档处理

#### 学习内容
- 文档加载（PDF、Word、Markdown）
- 文本分块策略
- Embedding 原理与调用

#### 实现功能
```python
# 文档 API
POST /api/documents/upload    # 上传文档
GET  /api/documents           # 文档列表
DELETE /api/documents/{id}    # 删除文档
POST /api/documents/{id}/reprocess  # 重新处理
```

#### 核心服务
```python
# 文档处理流程
class DocumentProcessor:
    def load(file) -> str           # 加载文档
    def chunk(text) -> List[str]    # 文本分块
    def embed(chunks) -> List[Vec]  # 向量化
    def store(vectors)              # 存储向量
```

#### 分块策略
- **固定大小**：按 token 数切分
- **语义切分**：按段落/章节
- **递归切分**：LangChain RecursiveCharacterTextSplitter

#### 交付物
- [ ] 文档上传 API
- [ ] PDF/Markdown 解析
- [ ] 分块策略实现
- [ ] Embedding 集成

---

### 2.2 向量存储

#### 学习内容
- pgvector 使用
- 向量索引（HNSW、IVFFlat）
- 混合检索（向量 + 关键词）

#### 实现功能
```python
# 向量操作
class VectorStore:
    def add(doc_id, chunks, embeddings)
    def search(query_embedding, top_k) -> List[Result]
    def delete(doc_id)
```

#### 数据库设计
```sql
-- 文档表
CREATE TABLE documents (
    id UUID PRIMARY KEY,
    filename VARCHAR,
    content TEXT,
    created_at TIMESTAMP
);

-- 向量表
CREATE TABLE document_chunks (
    id UUID PRIMARY KEY,
    document_id UUID REFERENCES documents(id),
    content TEXT,
    embedding vector(1536),
    metadata JSONB
);

-- 向量索引
CREATE INDEX ON document_chunks 
USING hnsw (embedding vector_cosine_ops);
```

#### 交付物
- [ ] pgvector 集成
- [ ] 向量存储服务
- [ ] 相似度检索
- [ ] 混合检索（可选）

---

### 2.3 RAG 对话

#### 学习内容
- RAG 流程编排
- Rerank 模型
- 引用来源展示

#### 实现功能
```python
# RAG 对话
POST /api/rag/chat
{
    "message": "什么是向量数据库？",
    "document_ids": ["doc1", "doc2"],  # 可选，指定文档范围
    "top_k": 5
}

# 响应
{
    "answer": "向量数据库是...",
    "sources": [
        {"document": "intro.pdf", "page": 3, "chunk": "..."}
    ]
}
```

#### RAG 流程
```python
class RAGService:
    def chat(message, doc_ids):
        # 1. Query Embedding
        query_embedding = embed(message)
        
        # 2. 向量检索
        chunks = vector_store.search(query_embedding, top_k=5)
        
        # 3. Rerank（可选）
        reranked = reranker.rerank(message, chunks)
        
        # 4. 构建 Prompt
        prompt = build_rag_prompt(message, reranked)
        
        # 5. LLM 生成
        response = llm.generate(prompt)
        
        return response, sources
```

#### 前端增强
- 源文档引用展示
- 文档选择器
- 检索结果预览

#### 交付物
- [ ] RAG 对话 API
- [ ] Rerank 集成（可选）
- [ ] 引用来源展示
- [ ] 前端文档选择 UI

---

### 2.4 知识库管理

#### 增强功能
- [ ] 文档预览
- [ ] 分块预览与编辑
- [ ] 检索测试界面
- [ ] 知识库统计

#### 交付物
- [ ] 知识库管理页面
- [ ] 文档 CRUD
- [ ] 检索质量测试工具

---

## Phase 3：Agent 智能助手

**目标**：让 AI 能够使用工具执行实际任务

### 3.1 工具系统

#### 学习内容
- Function Calling 原理
- Tool 定义规范
- MCP 协议基础

#### 实现工具
```python
# 内置工具
tools = [
    CalculatorTool(),       # 计算器
    WebSearchTool(),        # 网络搜索
    DatabaseQueryTool(),    # 数据库查询
    CodeExecutionTool(),    # 代码执行
    FileReadTool(),         # 文件读取
]
```

#### 工具定义
```python
class Tool:
    name: str
    description: str
    parameters: dict  # JSON Schema
    
    def execute(**kwargs) -> str
```

#### 交付物
- [ ] 工具基类定义
- [ ] 3-5 个内置工具
- [ ] 工具注册机制
- [ ] 工具调用测试

---

### 3.2 Agent 核心

#### 学习内容
- ReAct 模式
- Agent 循环控制
- 错误处理与重试

#### 实现功能
```python
# Agent 对话
POST /api/agent/chat
{
    "message": "查询最近7天的订单统计",
    "tools": ["database_query", "calculator"]
}
```

#### Agent 循环
```python
class Agent:
    def run(message, tools, max_iterations=10):
        messages = [SystemMessage(self.system_prompt)]
        messages.append(HumanMessage(message))
        
        for i in range(max_iterations):
            # 1. LLM 决策
            response = self.llm.invoke(messages, tools)
            
            # 2. 检查是否有工具调用
            if not response.tool_calls:
                return response.content
            
            # 3. 执行工具
            for tool_call in response.tool_calls:
                result = self.execute_tool(tool_call)
                messages.append(ToolMessage(result))
        
        return "达到最大迭代次数"
```

#### 交付物
- [ ] Agent 核心逻辑
- [ ] ReAct 循环实现
- [ ] 迭代次数限制
- [ ] 错误处理机制

---

### 3.3 LangGraph 编排

#### 学习内容
- LangGraph 状态图
- 节点与边的定义
- 条件路由

#### 实现复杂工作流
```python
from langgraph.graph import StateGraph

# 定义状态
class AgentState(TypedDict):
    messages: list
    next_step: str

# 构建图
graph = StateGraph(AgentState)
graph.add_node("analyze", analyze_node)
graph.add_node("retrieve", retrieve_node)
graph.add_node("generate", generate_node)
graph.add_edge("analyze", "retrieve")
graph.add_conditional_edges("retrieve", route_fn)
```

#### 交付物
- [ ] LangGraph 集成
- [ ] 多步骤工作流
- [ ] 条件路由示例

---

### 3.4 具体 Agent 实现

#### Agent 1：数据分析助手
- 查询数据库
- 生成统计图表
- 输出分析报告

#### Agent 2：代码助手
- 读取代码文件
- 代码审查
- 生成重构建议

#### Agent 3：文档助手
- 搜索知识库
- 总结文档
- 回答问题

#### 交付物
- [ ] 至少 2 个专用 Agent
- [ ] Agent 选择界面
- [ ] 执行过程可视化

---

### 3.5 记忆系统

#### 学习内容
- 短期记忆（对话历史）
- 长期记忆（持久化）
- 工作记忆（当前任务上下文）

#### 实现功能
```python
class MemoryManager:
    # 短期记忆
    def get_conversation_history(session_id) -> List[Message]
    
    # 长期记忆
    def save_to_long_term(key, value)
    def recall_from_long_term(key) -> str
    
    # 语义记忆（RAG 形式）
    def save_memory(content, metadata)
    def search_memory(query, top_k) -> List[str]
```

#### 交付物
- [ ] 对话历史管理
- [ ] 长期记忆存储
- [ ] 记忆检索

---

## Phase 4：AI 平台（可选）

**目标**：多模型管理、成本控制、可观测性

### 4.1 多模型支持

#### 实现功能
- 模型配置管理
- 动态模型切换
- 模型路由策略

```python
# 模型配置
models:
  - name: gpt-4
    provider: openai
    cost_per_1k_tokens: 0.03
    max_tokens: 128000
    
  - name: deepseek-chat
    provider: deepseek
    cost_per_1k_tokens: 0.001
    max_tokens: 128000
```

#### 交付物
- [ ] 模型配置管理
- [ ] 模型切换 API
- [ ] 前端模型选择器

---

### 4.2 成本控制

#### 实现功能
- Token 用量统计
- 费用计算
- 预算告警

```python
# 成本追踪
class CostTracker:
    def track(model, input_tokens, output_tokens)
    def get_daily_cost(date) -> float
    def check_budget(user_id) -> bool
```

#### 交付物
- [ ] Token 统计
- [ ] 费用报表
- [ ] 预算限制

---

### 4.3 可观测性

#### 实现功能
- 请求日志
- 响应时间追踪
- 错误率监控

```python
# 日志结构
{
    "request_id": "xxx",
    "model": "gpt-4",
    "input_tokens": 150,
    "output_tokens": 300,
    "latency_ms": 2500,
    "status": "success",
    "cost": 0.0135
}
```

#### 交付物
- [ ] 请求日志系统
- [ ] 监控仪表盘
- [ ] 异常告警

---

## 项目结构总览

```
ai-engineer-project/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── chat.py
│   │   │   ├── documents.py
│   │   │   ├── agent.py
│   │   │   └── admin.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── llm.py
│   │   │   └── security.py
│   │   ├── models/
│   │   │   ├── conversation.py
│   │   │   ├── document.py
│   │   │   └── tool.py
│   │   ├── services/
│   │   │   ├── chat_service.py
│   │   │   ├── rag_service.py
│   │   │   ├── agent_service.py
│   │   │   └── document_service.py
│   │   ├── tools/
│   │   │   ├── base.py
│   │   │   ├── calculator.py
│   │   │   ├── database.py
│   │   │   └── search.py
│   │   └── main.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── tests/
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx
│   │   │   ├── chat/
│   │   │   ├── knowledge/
│   │   │   └── agent/
│   │   ├── components/
│   │   │   ├── chat/
│   │   │   ├── knowledge/
│   │   │   └── ui/
│   │   ├── hooks/
│   │   ├── lib/
│   │   └── types/
│   ├── package.json
│   ├── Dockerfile
│   └── tailwind.config.ts
│
├── infra/
│   ├── docker-compose.yml
│   ├── .env.example
│   └── nginx/
│
├── docs/
│   ├── api.md
│   └── architecture.md
│
└── README.md
```

---

## 学习资源

### 官方文档
- [FastAPI](https://fastapi.tiangolo.com/)
- [Next.js](https://nextjs.org/docs)
- [LangChain Python](https://python.langchain.com/)
- [LangGraph](https://langchain-ai.github.io/langgraph/)
- [pgvector](https://github.com/pgvector/pgvector)

### 推荐教程
- LangChain 官方 RAG 教程
- Next.js App Router 教程
- FastAPI 官方教程

### 参考项目
- [Chatbot UI](https://github.com/mckaywrigley/chatbot-ui)
- [LangChain RAG 模板](https://github.com/langchain-ai/langchain/tree/master/templates/rag-conversation)

---

## 进度追踪

| 阶段 | 状态 | 开始日期 | 完成日期 | 备注 |
|------|------|----------|----------|------|
| Phase 1.1 后端基础 | ⬜ 待开始 | - | - | |
| Phase 1.2 前端基础 | ⬜ 待开始 | - | - | |
| Phase 1.3 功能完善 | ⬜ 待开始 | - | - | |
| Phase 2.1 文档处理 | ⬜ 待开始 | - | - | |
| Phase 2.2 向量存储 | ⬜ 待开始 | - | - | |
| Phase 2.3 RAG 对话 | ⬜ 待开始 | - | - | |
| Phase 2.4 知识库管理 | ⬜ 待开始 | - | - | |
| Phase 3.1 工具系统 | ⬜ 待开始 | - | - | |
| Phase 3.2 Agent 核心 | ⬜ 待开始 | - | - | |
| Phase 3.3 LangGraph | ⬜ 待开始 | - | - | |
| Phase 3.4 Agent 实现 | ⬜ 待开始 | - | - | |
| Phase 3.5 记忆系统 | ⬜ 待开始 | - | - | |
| Phase 4.1 多模型 | ⬜ 待开始 | - | - | |
| Phase 4.2 成本控制 | ⬜ 待开始 | - | - | |
| Phase 4.3 可观测性 | ⬜ 待开始 | - | - | |

---

## 验收标准

每个阶段完成后应达到：

### Phase 1 完成
- [ ] 能独立完成 Chat 应用的前后端开发
- [ ] 理解 LLM API 调用、流式输出原理
- [ ] 项目可本地运行并演示

### Phase 2 完成
- [ ] 能实现完整的 RAG 流程
- [ ] 理解 Embedding、向量检索原理
- [ ] 能基于文档进行问答

### Phase 3 完成
- [ ] 能实现具备工具调用能力的 Agent
- [ ] 理解 ReAct、LangGraph 编排
- [ ] 能设计多步骤工作流

### Phase 4 完成（可选）
- [ ] 能实现多模型管理和路由
- [ ] 理解成本控制和可观测性
- [ ] 具备平台化思维

---

## 简历包装建议

### 项目描述模板

**AI 智能对话平台**
> 设计并实现企业级 AI 对话平台，支持多轮对话、流式输出、知识库问答与智能 Agent。
> - 基于 FastAPI + LangChain 构建后端服务，实现 RAG 检索增强生成
> - 使用 Next.js + TypeScript 开发响应式前端，支持 Markdown 渲染与代码高亮
> - 集成 pgvector 向量数据库，实现文档语义检索
> - 实现 ReAct 模式 Agent，支持数据库查询、代码执行等工具调用

### 技术亮点
- 流式 SSE 实现与前端逐字渲染
- RAG 分块策略优化与 Rerank 集成
- LangGraph 状态图编排复杂工作流
- 多模型路由与成本控制

---

> **注意**：此计划为弹性时间表，根据实际工作情况灵活调整。每个 Phase 内的任务可并行或串行，重点是理解概念并完成交付物。
