import asyncio
import inspect
import json

from openai.types.responses import ResponseFunctionToolCall

from agent_runtimes.tools.registry import ToolRegistry


class ToolRunner:
    def __init__(
        self, registry: ToolRegistry, timeout: float = 10.0, max_Retries: int = 2
    ):
        self.registry = registry
        self.timeout = timeout
        self.max_Retries = max_Retries

    # 执行一个任务, 返回封装过的工具执行结果
    async def run(self, tool_name: str, arg: dict) -> dict:
        for attempt in range(self.max_Retries + 1):  # attempt是重试次数而不是执行次数
            try:
                tool = self.registry.get(tool_name)

                result = tool(**arg)

                if inspect.isawaitable(result):
                    # 先设置coroutine函数的限制，再awiat它
                    result = await asyncio.wait_for(result, timeout=self.timeout)
                # 工具执行成功，直接返回
                return {
                    "success": True,
                    "result": json.dumps(result),
                }
            # 执行超时，直接返回错误信息
            except TimeoutError:
                return self._error_result(
                    f"Tool {tool_name} excution timeout. Timeout time limit: {self.timeout}"
                )
            # 因为其他原因抛异常，提供自动重试，先不返回
            except Exception as e:
                error = str(e)

            # 达到重试次数上限
            if attempt >= self.max_Retries:
                return {
                    "success": False,
                    "error": error,
                    "attempts": attempt + 1,
                }

            print(f"Tool {tool_name} retrying...")
            await asyncio.sleep(1)

    # 运行工具，得到tool_call和result绑定的元组
    async def _excute(self, tool_call: ResponseFunctionToolCall):
        tool_name = tool_call.name

        try:
            arguments = json.loads(tool_call.arguments)
            result = await self.run(tool_name, arguments)
            return tool_call, result
        except json.JSONDecodeError as e:
            return tool_call, self._error_result(f"Invalid JSON arguments: {e}")
        except Exception as e:
            return tool_call, self._error_result(str(e))

    # 并发执行多个任务
    async def run_many(
        self, tool_calls: list[ResponseFunctionToolCall]
    ) -> list[tuple[ResponseFunctionToolCall, dict]]:
        tasks = [self._excute(tool_call) for tool_call in tool_calls]

        results = []
        for completed_task in asyncio.as_completed(
            tasks
        ):  # 这一步中 as_completed 已经将 A、B、C 安排给事件循环。
            (
                tool_call,
                result,
            ) = await completed_task
            # completed_task 表示的是一个等待入口：哪个任务最先完成，它就返回哪个任务的结果
            # 在这个过程中某个任务抛异常时，整个程序中断

            # 用as_completed能提前处理已完成的工具
            print(f"已完成: {tool_call.name}")
            results.append((tool_call, result))

        return results

    def _error_result(self, error: str) -> dict:
        return {
            "success": False,
            "error": error,
        }
