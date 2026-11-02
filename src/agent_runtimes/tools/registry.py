import inspect
from collections.abc import Callable


class ToolRegistry:
    def __init__(self):
        self.tools: dict[str, Callable] = {}

    def register(self, func: Callable) -> None:
        tool_name = func.__name__

        if tool_name in self.tools:
            raise ValueError(f"Tool: '{tool_name}'already registered")

        self.tools[tool_name] = func

    def get(self, func_name: str) -> Callable:
        if func_name not in self.tools:
            raise KeyError(f"Tool: '{func_name}' not found")

        return self.tools[func_name]

    def has(self, func_name: str) -> bool:
        return func_name in self.tools

    def list_tools(self) -> list[str]:
        return list(self.tools.keys())

    # 生成给模型使用的工具描述
    def get_tool_schema(self, func_name: str) -> dict:
        func = self.get(func_name)
        signature = inspect.signature(func)  # 获取函数签名
        properties = {}
        required = []

        for param_name, param in signature.parameters.items():
            if param_name == "self":
                continue

            mapping = {
                str: "string",
                bool: "boolean",
                int: "integer",
                float: "number",
                str | None: ["string", "null"],
            }

            properties[param_name] = {"type": mapping.get(param.annotation, "string")}

            if param.default == inspect.Parameter.empty:
                required.append(param_name)

        return {
            "type": "function",
            "name": func_name,
            "description": inspect.getdoc(func) or "",
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
                "additionalProperties": False,
            },
            "strict": False,
        }

    def get_all_schemas(self) -> list[dict]:
        return [self.get_tool_schema(func_name) for func_name in self.tools]
