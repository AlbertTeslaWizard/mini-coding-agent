import os

from openai import OpenAI

from agent import run_agent


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

        answer = run_agent(
            client = client,
            task = task,
            history = history 
        )

        print(f"\nAgent > {answer}")

if __name__ == '__main__':
    main()
