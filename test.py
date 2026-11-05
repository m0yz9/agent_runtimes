import asyncio
from datetime import datetime

from agent_runtimes.tools.runner import ToolRegistry, ToolRunner
from tasks.models import *


async def get_weather(city: str) -> str:
    """获取城市天气信息"""
    await asyncio.sleep(3)
    return f"当前{city}温度为25摄氏度。"


async def get_current_time() -> str:
    """获取当前时间"""
    await asyncio.sleep(2)
    raise RuntimeError("获取系统时间报错")
    return f"当前时间：{datetime.now()}。"


async def get_today_news(city: str, prefer: str | None = None) -> str:
    """获取城市今日新闻（提供偏好领域筛选选项）"""
    await asyncio.sleep(2)
    if prefer is not None:
        return f"根据筛选参数：{prefer}, 提供今日{city}新闻：..."
    return f"今日{city}新闻..."


async def brewing(weather: str, current_time: str):
    """根据时间和温度判断是否适合晒葡萄酒"""
    await asyncio.sleep(0.5)

    return (
        f"综合结果：天气是{weather}, 当前时间是【{current_time}】。非常适合晒葡萄酒。"
    )


async def _test():
    registry = ToolRegistry()
    registry.register(get_weather)
    registry.register(get_today_news)
    registry.register(get_current_time)
    registry.register(brewing)

    task1 = Task(task_id="A", tool_name="get_weather", arguments={"city": "上海"})
    task2 = Task(task_id="B", tool_name="get_current_time", arguments={})
    task3 = Task(
        task_id="C",
        tool_name="brewing",
        arguments={"weather": "晴天", "current_time": "25号"},
        arguments={
            "weather": {"from_task": "A"},
            "current_time": {"from_task": "B"},
        },
        dependencies=["A", "B"],
    )
    tasks = {
        "A": task1,
        "B": task2,
        "C": task3,
    }

    tool_runner = ToolRunner(registry)

    tool_scheduler = TaskScheduler(tool_runner=tool_runner)

    await tool_scheduler.run(tasks)

    for task in tasks.values():
        print(f"{task.task_id}: {task.state}")
        print(task.result, task.error)


if __name__ == "__main__":
    asyncio.run(_test())
