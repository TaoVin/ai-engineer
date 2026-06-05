# AI 应用工程学习项目

> 以项目为主导的 AI 应用工程学习平台，涵盖 LLM 应用开发、RAG 知识库、智能 Agent 等核心能力。

## 项目简介

本项目是一个系统化的 AI 应用工程学习计划，通过四个阶段的实践项目，帮助开发者掌握现代 AI 应用开发的核心技术栈：

- **Phase 1**: AI Chat 应用 - 掌握 LLM 调用基础
- **Phase 2**: RAG 知识库系统 - 掌握检索增强生成
- **Phase 3**: Agent 智能助手 - 掌握工具调用与编排
- **Phase 4**: AI 平台（可选） - 掌握多模型管理与成本控制

## 技术栈

| 层级 | 技术 | 用途 |
|------|------|------|
| 后端 | Python + FastAPI | AI 服务、API 接口 |
| AI 框架 | LangChain + LangGraph | RAG、Agent 编排 |
| 前端 | React + TypeScript + Next.js | Web UI |
| 数据库 | PostgreSQL + pgvector | 向量存储 |
| 缓存 | Redis | 会话、缓存 |
| 部署 | Docker + Docker Compose | 容器化 |

## 项目结构

```
ai-engineer/
├── backend/                    # 后端服务
│   ├── app/                    # 应用代码
│   │   ├── api/                # API 路由
│   │   ├── core/               # 核心配置
│   │   ├── models/             # 数据模型
│   │   ├── services/           # 业务逻辑
│   │   └── main.py            # 应用入口
│   ├── requirements.txt        # 依赖管理
│   └── Dockerfile             # 容器配置
├── frontend/                   # 前端应用
├── docs/                       # 项目文档
└── README.md                   # 项目说明
```

## 快速开始

### 环境要求

- Python 3.13+
- Node.js 18+
- MYSQL/MARIADB
- Redis 7+
- Docker & Docker Compose（可选）

### 后端启动

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或 .venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.dev .env
# 编辑 .env 文件，填入必要的配置

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 前端启动

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### Docker 启动（推荐）

```bash
# 使用 Docker Compose 一键启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## 功能特性

### Phase 1: AI Chat 应用

- ✅ 流式对话输出（SSE）
- ✅ 多轮对话支持
- ✅ 对话历史管理
- ✅ Markdown 渲染
- ✅ 代码高亮显示

### Phase 2: RAG 知识库系统

- 📄 文档上传与处理（PDF、Word、Markdown）
- 🔍 向量检索与相似度匹配
- 📚 知识库管理
- 🔗 引用来源展示

### Phase 3: Agent 智能助手

- 🤖 工具调用系统（Calculator、Web Search、Database Query）
- 🔄 ReAct 模式实现
- 📊 LangGraph 工作流编排
- 💾 记忆系统（短期/长期）

### Phase 4: AI 平台（可选）

- ⚙️ 多模型管理
- 💰 成本控制与预算管理
- 📈 可观测性与监控

## API 文档

启动后端服务后，访问以下地址查看 API 文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 学习资源

### 官方文档

- [FastAPI](https://fastapi.tiangolo.com/) - 高性能 Python Web 框架
- [Next.js](https://nextjs.org/docs) - React 全栈框架
- [LangChain Python](https://python.langchain.com/) - LLM 应用开发框架
- [LangGraph](https://langchain-ai.github.io/langgraph/) - 状态图编排框架
- [pgvector](https://github.com/pgvector/pgvector) - PostgreSQL 向量扩展

### 推荐教程

- LangChain 官方 RAG 教程
- Next.js App Router 教程
- FastAPI 官方教程

### 参考项目

- [Chatbot UI](https://github.com/mckaywrigley/chatbot-ui) - 开源 ChatGPT 克隆
- [LangChain RAG 模板](https://github.com/langchain-ai/langchain/tree/master/templates/rag-conversation) - RAG 实现模板

## 开发指南

### 代码规范

- 后端遵循 PEP 8 规范
- 前端使用 ESLint + Prettier
- 提交信息遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范

### 分支管理

- `main` - 生产分支
- `develop` - 开发分支
- `feature/*` - 功能分支
- `hotfix/*` - 紧急修复

### 测试

```bash
# 后端测试
cd backend
pytest

# 前端测试
cd frontend
npm test
```

## 常见问题

### Q: 如何配置 API Key？

在后端目录下创建 `.env` 文件，添加以下配置：

```env
OPENAI_API_KEY=your_openai_api_key
OPENAI_API_BASE=https://api.openai.com/v1
```

### Q: 数据库连接失败？

检查 PostgreSQL 服务是否运行，并确保 `.env` 中的数据库配置正确：

```env
DATABASE_URL=postgresql://user:password@localhost:5432/ai_engineer
```

### Q: 如何部署到生产环境？

1. 使用 Docker Compose 构建镜像
2. 配置 Nginx 反向代理
3. 设置 HTTPS 证书
4. 配置环境变量

## 贡献指南

欢迎贡献代码、报告问题或提出建议！

1. Fork 本仓库
2. 创建功能分支：`git checkout -b feature/your-feature`
3. 提交更改：`git commit -m 'feat: add some feature'`
4. 推送分支：`git push origin feature/your-feature`
5. 提交 Pull Request

## 许可证

本项目采用 [Apache License 2.0](LICENSE) 许可证。

## 联系方式

- 项目地址：https://github.com/your-username/ai-engineer
- 问题反馈：[GitHub Issues](https://github.com/your-username/ai-engineer/issues)

---

> **注意**：
 1. 此计划为弹性时间表，根据实际工作情况灵活调整。每个阶段的任务可并行或串行，重点是理解概念并完成交付物。
 2. 项目才刚刚开始，待完成后续步骤
 3. 项目文档等多为AI生成+修复，可能有遗漏