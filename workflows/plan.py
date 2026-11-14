from agent import run_agent

PLAN_TOOLS = {
    "list_dir",
    "search_files",
    "read_file"
}

def plan_workflow(client, task: str) -> str:
    instruction = f"""You are in read-only planning mode for a coding project.

User task:
{task}

Inspect the relevant files before proposing a plan.
Do not edit files, execute shell commands, or run tests.

Reply in the user's language. Include:
1. What you found in the current code.
2. Which files should change and why.
3. The implementation steps in order.
4. How to verify the changes after implementation.

Name the files you actually inspected. If something is unclear,
say what you could not confirm.
"""

    return run_agent(
        client = client,
        task = instruction,
        history = [],
        max_steps = 8,
        allowed_tools = PLAN_TOOLS
    )