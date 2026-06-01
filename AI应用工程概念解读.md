# AI 应用工程核心概念解读

> 本文档覆盖 AI 应用工程师所需的核心概念，帮助快速建立认知框架。

---

## 一、LLM 基础概念

### 1.1 大语言模型（LLM）

**Large Language Model**，基于 Transformer 架构训练的神经网络，能够理解和生成自然语言文本。

- 代表模型：GPT-4、Claude、Gemini、DeepSeek、Llama
- 核心能力：文本生成、理解、推理、代码生成

### 1.2 Token

LLM 处理文本的最小单位。模型不直接处理字符，而是将文本拆分为 token 后计算。

- 英文：约 1 token ≈ 4 个字符（如 "hello" = 1 token）
- 中文：约 1 token ≈ 1-2 个汉字
- **影响**：token 数量决定 API 调用成本和上下文长度

### 1.3 Context Window（上下文窗口）

模型单次能处理的最大 token 数量。

| 模型 | 上下文窗口 |
|------|-----------|
| GPT-4 | 128K tokens |
| Claude 3 | 200K tokens |
| DeepSeek | 128K tokens |

- 超出窗口会导致截断或报错
- 更大的窗口 = 更高的成本

### 1.4 Temperature（温度）

控制输出随机性的参数，范围 0-2。

- **0**：输出确定性最高，适合代码生成、数据提取
- **1**：平衡创意与确定性
- **2**：输出最随机，适合创意写作

### 1.5 System Prompt / User Prompt

- **System Prompt**：定义 AI 的角色、行为规则、输出格式
- **User Prompt**：用户的实际输入

```
System: 你是一个专业的代码审查助手，只输出 JSON 格式
User: 帮我审查这段代码...
```

### 1.6 Streaming（流式输出）

逐 token 返回结果，而非等待完整生成。用户体验更好，首字响应更快。

- 实现方式：SSE（Server-Sent Events）
- 前端需要处理逐字渲染

---

## 二、Prompt 工程

### 2.1 Prompt Engineering

通过设计和优化提示词来引导模型输出符合预期的结果。

### 2.2 Few-shot Prompting

在提示中提供少量示例，帮助模型理解任务模式。

```
示例：
输入: 苹果 → 输出: 水果
输入: 狗 → 输出: 动物
输入: 玫瑰 → 输出: ?
```

### 2.3 Chain of Thought（思维链）

引导模型逐步推理，提高复杂任务的准确率。

```
请一步步思考：
1. 首先分析问题...
2. 然后考虑...
3. 最后得出结论...
```

### 2.4 Structured Output（结构化输出）

强制模型输出特定格式（JSON、XML 等），便于程序解析。

```json
{
  "sentiment": "positive",
  "score": 0.95,
  "keywords": ["优秀", "推荐"]
}
```

---

## 三、Function Calling / Tool Use

### 3.1 Function Calling

让 LLM 能够调用外部函数/API。模型不直接执行，而是输出结构化的调用指令。

```
用户: 北京今天天气如何？
模型输出: {
  "function": "get_weather",
  "arguments": {"city": "北京"}
}
```

### 3.2 Tool Calling

Function Calling 的扩展概念，支持更丰富的工具类型：

- API 调用
- 数据库查询
- 文件操作
- 代码执行

### 3.3 MCP（Model Context Protocol）

Anthropic 提出的标准化协议，用于 LLM 与外部工具/数据源交互。

- **MCP Server**：提供工具和资源的服务端
- **MCP Client**：调用工具的客户端
- 统一了 Tool Calling 的接口规范

---

## 四、Embedding 与向量检索

### 4.1 Embedding（向量化）

将文本转换为高维数值向量，捕捉语义信息。

- "猫" → [0.2, 0.8, -0.1, ...]
- "小猫" → [0.21, 0.79, -0.09, ...] （相近）
- "汽车" → [0.9, -0.3, 0.5, ...] （较远）

### 4.2 向量数据库

专门存储和检索向量的数据库。

| 数据库 | 特点 |
|--------|------|
| Milvus | 开源，高性能，适合大规模 |
| pgvector | PostgreSQL 扩展，易集成 |
| Pinecone | 云服务，零运维 |
| Weaviate | 开源，支持混合检索 |

### 4.3 余弦相似度

衡量两个向量方向一致性的指标，范围 [-1, 1]。

- 1：完全相同方向（语义一致）
- 0：正交（无关）
- -1：完全相反

### 4.4 Chunk（分块）

将长文档切分为较小片段，便于向量化和检索。

- **chunk_size**：每个块的大小（token 数）
- **chunk_overlap**：相邻块的重叠部分，保持上下文连续性

---

## 五、RAG（检索增强生成）

### 5.1 RAG 是什么

**Retrieval-Augmented Generation**，通过检索外部知识增强 LLM 输出。

```
用户问题 → 检索相关文档 → 拼接上下文 → LLM 生成答案
```

### 5.2 为什么需要 RAG

- **知识时效**：LLM 训练数据有截止日期
- **私有数据**：企业内部文档、数据库
- **减少幻觉**：基于真实文档生成，降低虚构概率

### 5.3 RAG 核心流程

```
1. 文档加载 (Load)
2. 文本分块 (Chunk)
3. 向量化 (Embed)
4. 存储 (Store)
5. 检索 (Retrieve)
6. 重排序 (Rerank)
7. 生成 (Generate)
```

### 5.4 Rerank（重排序）

对初步检索结果进行二次排序，提升相关性。

- 初检：向量相似度（召回率高，精度一般）
- 重排：Cross-encoder 模型（精度高，速度慢）

### 5.5 Hallucination（幻觉）

LLM 生成看似合理但实际错误的内容。

- **原因**：模型基于概率生成，缺乏事实校验
- **缓解**：RAG、限制温度、明确指令

---

## 六、Agent 系统

### 6.1 Agent 是什么

能够自主规划、使用工具、执行任务的 AI 系统。

- **Chatbot**：只能对话
- **Agent**：能对话 + 能行动

### 6.2 Agent 核心组件

```
感知 (Perception) → 规划 (Planning) → 执行 (Action) → 反馈 (Feedback)
      ↑                                                    ↓
      └──────────────── Memory ←──────────────────────────┘
```

- **Planning**：将任务分解为步骤
- **Memory**：短期（对话历史）和长期（持久化存储）
- **Tools**：调用外部能力
- **Reflection**：评估执行结果并调整

### 6.3 ReAct 模式

**Reasoning + Acting**，Agent 的经典执行模式。

```
Thought: 我需要查询用户的订单信息
Action: query_database({"user_id": "123", "type": "orders"})
Observation: 找到 5 条订单
Thought: 用户问的是最近一笔，我需要筛选
Action: filter_latest({"orders": [...]})
```

### 6.4 Multi-Agent

多个 Agent 协作完成复杂任务。

- **分工**：不同 Agent 负责不同领域
- **通信**：消息传递、共享状态
- **编排**：LangGraph、CrewAI

### 6.5 Agent Loop（循环控制）

防止 Agent 陷入无限循环的机制：

- **max_iterations**：最大迭代次数
- **timeout**：超时限制
- **stop_condition**：终止条件判断

---

## 七、LangChain 生态

### 7.1 LangChain

LLM 应用开发框架，提供模块化组件。

核心模块：
- **Models**：模型调用抽象
- **Prompts**：提示词管理
- **Chains**：任务链编排
- **Memory**：对话记忆
- **Agents**：Agent 框架
- **Retrieval**：RAG 组件

### 7.2 LangGraph

基于图的 Agent 编排框架，适合复杂工作流。

```
         ┌─────────┐
         │  Start  │
         └────┬────┘
              ↓
      ┌───────┴───────┐
      ↓               ↓
┌─────┴─────┐   ┌─────┴─────┐
│  Tool A   │   │  Tool B   │
└─────┬─────┘   └─────┬─────┘
      └───────┬───────┘
              ↓
         ┌────┴────┐
         │  Merge  │
         └────┬────┘
              ↓
         ┌────┴────┐
         │   End   │
         └─────────┘
```

### 7.3 LangSmith

LangChain 配套的可观测性平台。

- Trace 追踪
- 评估测试
- 监控告警

---

## 八、AI 平台化概念

### 8.1 AI Gateway（AI 网关）

统一管理 LLM 调用的中间层。

核心功能：
- **多模型路由**：根据策略分发到不同模型
- **负载均衡**：分散请求压力
- **Fallback**：主模型失败时切换备选
- **限流**：控制调用频率
- **成本控制**：Token 用量监控
- **缓存**：相似请求复用结果

### 8.2 Prompt 管理

集中管理、版本控制、A/B 测试提示词。

### 8.3 Observability（可观测性）

AI 系统的监控体系：

- **Logs**：请求/响应日志
- **Metrics**：延迟、吞吐、错误率
- **Traces**：端到端调用链路

---

## 九、前端相关概念

### 9.1 AI 对话 UI 组件

- 消息气泡（用户/AI 区分）
- 流式打字效果
- Markdown 渲染
- 代码高亮
- 思考过程展示

### 9.2 Streaming 前端处理

```typescript
// SSE 处理示例
const response = await fetch('/api/chat', {
  method: 'POST',
  body: JSON.stringify({ message })
});

const reader = response.body.getReader();
while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  // 处理 chunk 并渲染
}
```

### 9.3 RAG 源引用展示

展示答案来源文档，增强可信度。

---

## 十、部署与运维

### 10.1 模型部署

- **云 API**：OpenAI、Anthropic、DeepSeek
- **本地部署**：Ollama、vLLM
- **混合**：云 API + 本地小模型

### 10.2 Ollama

本地运行开源 LLM 的工具。

```bash
ollama pull llama3
ollama run llama3
```

### 10.3 vLLM

高性能 LLM 推理引擎，适合生产环境。

- PagedAttention 显存优化
- Continuous Batching
- OpenAI 兼容 API

---

## 十一、常见术语速查

| 术语 | 全称 | 含义 |
|------|------|------|
| LLM | Large Language Model | 大语言模型 |
| RAG | Retrieval-Augmented Generation | 检索增强生成 |
| MCP | Model Context Protocol | 模型上下文协议 |
| CoT | Chain of Thought | 思维链 |
| ReAct | Reasoning + Acting | 推理与行动 |
| SSE | Server-Sent Events | 服务端推送事件 |
| TPS | Tokens Per Second | 每秒生成 token 数 |
| TTFT | Time to First Token | 首字响应时间 |

---

## 参考资源

- [OpenAI Platform Docs](https://platform.openai.com/docs)
- [LangChain Docs](https://python.langchain.com/)
- [LangGraph Docs](https://langchain-ai.github.io/langgraph/)
- [Ollama](https://ollama.com)
- [Anthropic MCP](https://modelcontextprotocol.io)
