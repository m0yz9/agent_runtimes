import json

from agent_runtimes.agent.llm import LLM
from agent_runtimes.tools.runner import ToolRegistry, ToolRunner


class ModelToolLoop:
    def __init__(
        self,
        llm: LLM,
        registry: ToolRegistry,
        tool_runner: ToolRunner,
        max_iteration: int = 10,
    ):
        self.llm = llm
        self.registry = registry
        self.tool_runner = tool_runner
        self.max_iteration = max_iteration

    async def run(self, input_items: list):
        # 获取所有工具的整合schemas
        tool_schemas = self.registry.get_all_schemas()

        # 开始agent loop
        for _ in range(self.max_iteration):
            # 得到response
            response = await self.llm.chat(input_items, tool_schemas)

            # 收集所有tool_call
            calls = [item for item in response.output if item.type == "function_call"]

            # 若有工具调用，打印一下他们的信息，如果没有，就直接返回内容
            if calls:
                print(
                    json.dumps(
                        [call.model_dump() for call in calls],
                        ensure_ascii=False,
                        indent=2,
                    )
                )
            else:
                return response.output_text

            # 将本次模型返回的所有Output挂到input上，增加短期记忆
            input_items.extend(response.output)

            # 并发执行工具
            results = await self.tool_runner.run_many(calls)

            print("工具结果：")
            # 告诉模型工具调用结果
            for tool_call, result in results:
                input_items.append(
                    {
                        "type": "function_call_output",
                        "call_id": tool_call.call_id,
                        "output": json.dumps(result, ensure_ascii=False),
                    }
                )
                print(
                    f"{tool_call.name}result: {json.dumps(result, ensure_ascii=False)}"
                )

            print("\n本轮结束\n")

        raise RuntimeError(
            f"Tool loop exceeded maximum iterations: {self.max_iteration}"
        )
