    # 动态解析参数
    def resolve_arguments(self, tasks: dict[str, Task]) -> dict:
        resolved = {}

        for key, value in self.arguments.items():
            if isinstance(value, dict) and "from_task" in value:
                dependence_id = value["from_task"]
                dependence_task = tasks[dependence_id]
                resolved[key] = dependence_task.result
            else:
                resolved[key] = value
        self.arguments = resolved