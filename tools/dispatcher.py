import json
from typing import Any

from tools.file_ops import (
    delete_file,
    edit_file,
    list_dir,
    read_file,
    search_files,
    write_file,
)


# 执行模型请求的工具
def execute_tool(item: Any) -> str:
    try:
        args = json.loads(item.arguments)
        if item.name == "read_file":
            return read_file(args["path"])

        elif item.name == "list_dir":
            return list_dir(args["path"])

        elif item.name == "edit_file":
            return edit_file(
                args["path"],
                args["old_string"],
                args["new_string"]
            )

        elif item.name == "write_file":
            return write_file(
                args["path"],
                args["content"]
            )

        elif item.name == "delete_file":
            return delete_file(
                args["path"]
            )

        elif item.name == "search_files":
            return search_files(args["query"])

        return f"Error: Unknown tool {item.name}"

    except Exception as e:
        return f"Error: Tool execution failed: {e}"