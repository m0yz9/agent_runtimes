import asyncio
from datetime import datetime

from agent_runtimes.agent.llm import LLM
from agent_runtimes.agent.model_tool_loop import ModelToolLoop
from agent_runtimes.tools.runner import ToolRegistry, ToolRunner


async def get_weather(city: str) -> str:
    """获取城市天气信息"""
    await asyncio.sleep(3)
    return f"当前{city}温度为25摄氏度。"


async def get_current_time() -> str:
    """获取当前时间"""
    await asyncio.sleep(4)
    return f"当前时间：{datetime.now()}。"


async def get_today_news(city: str, prefer: str | None = None) -> str:
    """获取城市今日新闻（提供偏好领域筛选选项）"""
    await asyncio.sleep(2)
    if prefer is not None:
        return f"根据筛选参数：{prefer}, 提供今日{city}新闻：..."
    return f"今日{city}新闻..."


async def main():
    registry = ToolRegistry()
    toolRunner = ToolRunner(registry, timeout=8.0)

    registry.register(get_weather)
    registry.register(get_today_news)
    registry.register(get_current_time)

    llm = LLM(model="gpt-6-luna")
    input = [
        {
            "role": "user",
            "content": "现在时几点？今天上海天气咋样呢？",
        }
    ]

    loop = ModelToolLoop(llm, registry, toolRunner, max_iteration=2)
    result = await loop.run(input)

    print(result)


if __name__ == "__main__":
    asyncio.run(main())
