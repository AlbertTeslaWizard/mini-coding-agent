import os

from openai import OpenAI

from agent import run_agent

from workflows.plan import plan_workflow
from workflows.repair import repair_workflow


def main():
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
        else: 
            answer = run_agent(
                client = client,
                task = task,
                history = history 
            )

        print(f"\nAgent > {answer}")

if __name__ == '__main__':
    main()
