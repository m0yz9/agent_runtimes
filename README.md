# Agent Runtimes

学习中的轻量 Python Agent Runtime，基于 OpenAI Responses API，实现“模型请求 → 工具执行 → 结果回传 → 模型回答”的循环。

## 当前功能

- **工具注册**：按函数名管理工具，根据类型标注、默认参数和文档字符串生成工具 Schema。
- **工具执行**：支持同步与异步函数；多个工具并发调度，按完成顺序收集结果。
- **失败处理**：支持异步工具超时、普通异常重试，以及 JSON 参数解析错误回传。
- **多轮循环**：保留工具调用相关上下文，通过 `call_id` 匹配结果，限制最大模型调用轮数。
- **执行日志**：在终端输出工具调用、完成情况、重试和执行结果。

## 示例与运行

`main.py` 注册天气、新闻和当前时间三个工具，演示模型调用与失败重试。天气、新闻使用模拟数据；时间取自本机。

需要 Python 3.13+、uv，以及环境变量 `OPENAI_API_KEY`（也可通过本地 `.env` 加载）。在项目根目录运行：

```bash
uv sync
uv run python main.py
```

模型在 `main.py` 中配置，需具备对应模型的 API 访问权限。

## 代码结构

```text
main.py                         # Agent 运行示例
test.py                         # 手动验证对话上下文的脚本
src/agent_runtimes/
├── agent/llm.py                 # 异步模型调用
├── agent/model_tool_loop.py     # 模型与工具循环
└── tools/
    ├── registry.py              # 工具注册与 Schema 生成
    └── runner.py                # 工具执行、并发、超时与重试
```

当前为学习原型：尚无持久化会话、流式输出或自动化测试；同步工具直接执行，不受异步超时控制。`test.py` 是手动调用脚本。
