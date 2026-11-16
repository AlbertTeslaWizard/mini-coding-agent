from dataclasses import dataclass

from agent import run_agent

APPLY_TOOLS = {"list_dir", "search_files", "read_file", "edit_file"}

@dataclass(frozen = True)
class PendingPlan:
    task: str
    text: str

def apply_workflow(client, plan: PendingPlan) -> str:
    instruction = f"""
    Execute the reviewed plan below.

    Original task:
    {plan.task}

    Reviewed plan:
    {plan.text}

    Read the relevant files again before editing.
    Use edit_file for changes, and stay within the plan.
    If the user rejects an edit, stop and report what was already changed.
    If the plan no longer fits the files, stop and explain why.
    """

    return run_agent(
        client = client,
        task = instruction,
        history = [],
        max_steps = 8,
        allowed_tools = APPLY_TOOLS,
        stop_on_edit_rejection = True
    )
