            # 动态解析参数
            for task in runnable:
                task.resolve_arguments(tasks)
                print(f"任务 {task.task_id}: {task.tool_name} 参数: {task.arguments}")
