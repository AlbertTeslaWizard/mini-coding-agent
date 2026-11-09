import os
from pathlib import Path
from openai import OpenAI
import uuid
import json 

# 一次进程内复用同一个会话 ID，便于网关做路由优化和 prompt cache
SESSION_ID = f"ses_{uuid.uuid4().hex}"

# 定义工具
TOOLS = [
    {
        "type": "function",
        "name": "read_file",
        "description": "Read the contents of a file",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The path to the file"
                }
            },
            "required": ["path"],
            "additionalProperties": False
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "list_dir",
        "description": "List files and subdirectories in a directory",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Directory path relative to the project root. Use '.' for the root directory."
                }
            },
            "required": ["path"],
            "additionalProperties": False
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "edit_file",
        "description": (
            "Replace an exact, unique string in an existing file. "
            "Read the file before editing it."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file to edit"
                },
                "old_string": {
                    "type": "string",
                    "description": "Exact text to replace"
                },
                "new_string": {
                    "type": "string",
                    "description": "Replacement text"
                }
            },
            "required": [
                "path",
                "old_string",
                "new_string"
            ],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "write_file",
        "description": (
            "Create a new file and write text content to it. "
            "Do not overwrite existing files. "
            "Use edit_file to modify existing files."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path of the new file"
                },
                "content": {
                    "type": "string",
                    "description": "Text content to write into new file"
                }
            },
            "required": ["path", "content"],
            "additionalProperties": False 
        },
        "strict": True
    }
]

def call_model(client, history, session_id=SESSION_ID):
    return client.responses.create(
        model="deepseek-v4.1-flash",
        input=history,
        tools=TOOLS,
        tool_choice="auto",
        extra_headers={
            "User-Agent": "mini-coding-agent/0.1",
            "x-opencode-session": session_id
        }
    )

# 实现文件读取工具
def read_file(path: str) -> str:
    root = Path.cwd().resolve()
    target = (root / path).resolve()

    if not target.is_relative_to(root):
        return "Error: Access outside project is denied"

    if target.suffix.lower() not in [".md", ".txt", ".py"]:
        return "Error: Unsupported file type"

    if not target.is_file():
        return "Error: File does not exist"

    with target.open("r", encoding="utf-8") as file:
        return file.read(10000)

# 实现目录列举工具
def list_dir(path: str) -> str:
    root = Path.cwd().resolve()
    target = (root / path).resolve()

    if not target.is_relative_to(root):
        return "Error: Access outside project is denied"

    if not target.is_dir():
        return "Error: Directory does not exist"

    entries = sorted(
        target.iterdir(),
        key=lambda entry: entry.name.lower()
    )

    if not entries:
        return "(empty directory)"

    output = []
    for entry in entries[:100]:
        if entry.is_dir():
            output.append(f"[DIR] {entry.name}/")
        else:
            output.append(f"[FILE] {entry.name}")

    if len(entries) > 100:
        output.append("... more entries omitted")

    return "\n".join(output)

def edit_file(path: str, old_string: str, new_string: str) -> str:
    root = Path.cwd().resolve()
    target = (root / path).resolve()

    if not target.is_relative_to(root):
        return "Error: Access outside project is denied"

    if target.suffix.lower() not in {".md", ".txt", ".py"}:
        return "Error: Unsupported file type"

    if not target.is_file():
        return "Error: File does not exist"

    if not old_string:
        return "Error: old_string cannot be empty"

    if old_string == new_string:
        return "Error: No changes requested"

    if target.stat().st_size > 1_000_000:
        return "Error: File is too large to edit"

    content = target.read_text(encoding="utf-8")

    count = content.count(old_string)
    if count == 0:
        return "Error: old_string not found"
    if count > 1:
        return f"Error: old_string occurs {count} times"

    new_content = content.replace(
        old_string,
        new_string,
        1
    )

    print(f"\nFile: {target.relative_to(root)}")
    print(f"Old:\n{old_string}")
    print(f"New:\n{new_string}")

    confirmation = input("\nApply this edit? [y/N]: ")

    if confirmation.strip().lower() != "y":
        return "Error: Edit rejected by user"

    target.write_text(new_content, encoding="utf-8")

    return f"OK: Updated {target.relative_to(root)}"

def write_file(path: str, content: str) -> str:
    root = Path.cwd().resolve()
    target = (root / path).resolve()

    if not target.is_relative_to(root):
        return "Error: Access outside project is denied"

    if target.suffix.lower() not in {".md", ".py", ".txt"}:
        return "Error: Unsupported file types"

    if target.exists():
        return "Error: File already exists"

    if not target.parent.is_dir():
        return "Error: Parent directory does not exist"

    if len(content.encode("utf-8")) > 100_000:
        return "Error: Content is too large"

    print(f"\nNew file: {target.relative_to(root)}")
    print(f"Content preview:\n{content[:500]}")

    if len(content) > 500:
        print("... (preview truncated)")

    confirmation = input("\nCreate this file? [y/N]: ")
    if confirmation.strip().lower() != "y":
        return "Error: File creation rejected by user"

    with target.open("x", encoding="utf-8") as file:
        file.write(content)

    return f"OK: Created {target.relative_to(root)}"

# 执行模型请求的工具
def execute_tool(item) -> str:
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

        return f"Error: Unknown tool {item.name}"

    except Exception as e:
        return f"Error: Tool execution failed: {e}"

# Agent Loop
def run_agent(client, task: str, history, max_steps: int = 10) -> str:
    history.append({
        "role": "user",
        "content": task 
    })

    session_id = SESSION_ID

    for step in range(max_steps):
        print(f"\n===== Agent Step {step + 1} ======")

        # 请求模型
        response = call_model(client, history, session_id)

        # 保存模型输出
        history.extend(response.output)

        # 提取工具调用
        tool_calls = [
            item for item in response.output if item.type == "function_call"
        ]

        # 没有工具调用，说明可以结束
        if not tool_calls:
            return response.output_text or "No final response"

        # 执行当前轮次中的所有工具调用
        for item in tool_calls:
            print(f"调用工具: {item.name}")
            print(f"工具参数: {item.arguments}")

            result = execute_tool(item)
            print(f"工具结果: {result[:200]}")

            # 将工具执行结果返回给模型
            history.append({
                "type": "function_call_output",
                "call_id": item.call_id,
                "output": result
            })

    return "Error: Maximum agent steps exceeded"

if __name__ == '__main__':
    client = OpenAI(
        api_key = os.environ["OPENCODE_API_KEY"],
        base_url = "https://opencode.ai/inference/go/openai/v1",
        max_retries = 5,
        timeout = 60.0
    )

    history = []
    print("Mini Coding Agent started!")
    print("Type 'exit' to quit.")

    while True:
        task = input("\nYou > ").strip()
        
        if task.strip().lower() in {"exit", "quit"}:
            print("Goodbye!")
            break

        if not task:
            continue 

        answer = run_agent(
            client = client,
            task = task,
            history = history 
        )

        print(f"\nAgent > {answer}")
    