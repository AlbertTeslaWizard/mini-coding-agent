import os
import readline

from openai import OpenAI
from agent import run_agent
from tools.git_ops import get_git_diff
from workflows.plan import plan_workflow
from workflows.repair import repair_workflow


HELP_TEXT = """Available commands

  /help            Show this help.
  /plan <task>     Inspect the project and propose a plan without editing files.
  /repair <task>   Run tests and try to fix failures without editing tests/.
  exit, quit       Exit the program.

Enter a task in plain text to use the coding agent.
"""

def main():
    client = OpenAI(
        api_key = os.environ["OPENCODE_API_KEY"],
        base_url = "https://opencode.ai/inference/go/openai/v1",
        max_retries = 5,
        timeout = 60.0
    )

    history = []
    print("Mini Coding Agent started!")
    print("Type '/help' for commands or 'exit' to quit.")

    while True:
        try:
            task = input("\nYou > ").strip()
        except UnicodeDecodeError:
            print("输入包含无法识别的字节（中文输入或粘贴被打断），请重新输入。")
            continue
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if task.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break

        if not task:
            continue

        parts = task.split(maxsplit = 1)
        command = parts[0]
        command_task = parts[1] if len(parts) == 2 else ""

        if command == "/repair":
            if not command_task:
                print("Usage: /repair <task>")
                continue
            
            answer = repair_workflow(
                client = client,
                task = command_task 
            )

        elif command == "/plan":
            if not command_task:
                print("Usage: /plan <task>")
                continue

            answer = plan_workflow(
                client = client,
                task = command_task
            )

        elif command == "/help":
            print(HELP_TEXT)
            continue

        elif command == "/diff":
            if command_task:
                print("Usage: /diff")
            else:
                print(get_git_diff())
            continue

        else: 
            answer = run_agent(
                client = client,
                task = task,
                history = history 
            )

        print(f"\nAgent > {answer}")

if __name__ == '__main__':
    main()
