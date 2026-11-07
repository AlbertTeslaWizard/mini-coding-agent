import os
import time
from pathlib import Path
from openai import OpenAI, RateLimitError
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
    }
]

history = [
    {
        "role": "user",
        "content": "请读取 README.md 并总结这个项目的主要功能。"
    }
]

# 请求模型（对上游 429 过载做指数退避重试）
def call_model(client, history, session_id=SESSION_ID, max_retries=6):
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

# 执行模型请求的工具
def execute_tool(item) -> str:
    try:
        args = json.loads(item.arguments)
        if item.name == "read_file":
            return read_file(args["path"])

        return f"Error: Unknown tool {item.name}"

    except Exception as e:
        return f"Error: Tool execution failed: {e}"

# Agent Loop
def run_agent(client, task: str, max_steps: int = 10) -> str:
    history = [
        {
            "role": "user",
            "content": task 
        }
    ]

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

    task = input("请输入任务: ")
    answer = run_agent(client, task)

    print("\n===== Final Answer =====")
    print(answer)


    