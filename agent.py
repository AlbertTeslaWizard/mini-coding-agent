import uuid

from tools.dispatcher import execute_tool
from tools.schemas import TOOLS

# Session ID
SESSION_ID = f"ses_{uuid.uuid4().hex}"

# 调用大模型
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
