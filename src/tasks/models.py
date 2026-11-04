from __future__ import annotations

import asyncio
import enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agent_runtimes.tools.runner import ToolRunner


class TaskState(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    BLOCKED = "blocked"


# 将一次任务调用封装为Task
# 能够追踪任务的生命周期，配上状态机
class Task:
    def __init__(
        self, task_id: str, tool_name: str, arguments: dict, dependencies=None
    ):
        self.task_id = task_id
        self.tool_name = tool_name
        self.arguments = arguments

        self.state: str = TaskState.PENDING
        self.result = None
        self.error = None

        self.dependencies: list[str] = dependencies or []

    def mark_running(self):
        self.state = TaskState.RUNNING

    def mark_success(self, result):
        self.state = TaskState.SUCCESS
        self.result = result

    def mark_failed(self, error):
        self.state = TaskState.FAILED
        self.error = error

    def mark_blocked(self, error=None):
        self.state = TaskState.BLOCKED
        self.error = error

    # 判断当前任务能否执行
    # param {tasks}：所有待执行任务
    def can_run(self, tasks: dict[str, Task]) -> bool:
        return all(
            tasks[dependencies_id].state == TaskState.SUCCESS
            for dependencies_id in self.dependencies
        )

    # 此任务是否有依赖任务已经失败
    def has_failed_dependency(self, tasks: dict[str, Task]) -> bool:
        return any(
            tasks[dependence_id].state in (TaskState.FAILED, TaskState.BLOCKED)
            for dependence_id in self.dependencies
        )


# 任务调度器
# 分批执行任务
class TaskScheduler:
    def __init__(self, tool_runner: ToolRunner):
        self.tool_runner = tool_runner

    async def run(self, tasks: dict[str, Task]) -> list:
        pending = list(tasks.values())
        # 成功完成的任务
        completed = []

        while pending:
            for task in pending:
                # 失败传播机制，如果本轮有任务的依赖任务失败了，直接标记并从pending remove掉
                if task.has_failed_dependency(tasks):
                    task.mark_blocked("Dependencies cannot be satisfied")
                    pending.remove(task)
                    print(f"{task.task_id}: BLOCKED: {task.error}")

            if not pending:
                break

            # 可运行的Task
            runnable = [task for task in pending if task.can_run(tasks)]

            # 若pending中没有可执行的任务
            if not runnable:
                break
            print("本轮执行：", [task.task_id for task in runnable])

            results = await asyncio.gather(
                *[self.tool_runner.run_task(task) for task in runnable]
            )

            for task in results:
                pending.remove(task)
                if task.state == TaskState.SUCCESS:
                    completed.append(task)

        return completed
