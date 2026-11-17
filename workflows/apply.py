from dataclasses import dataclass
from agent import run_agent
from tools.change_log import FileChange

APPLY_TOOLS = {"list_dir", "search_files", "read_file", "edit_file", "write_file", "delete_file"}

@dataclass(frozen = True)
class PendingPlan:
    task: str
    text: str

def apply_workflow(client, plan: PendingPlan, *, changes: list[FileChange] | None = None) -> str:
    instruction = f"""
    Execute the reviewed plan below.

    Original task:
    {plan.task}

    Reviewed plan:
    {plan.text}

    Read the relevant files again before changing them.
    Use write_file to create a new file and edit_file to modify an existing file.
    Stay within the reviewed plan.
    Use delete_file only for a file explicitly named for deletion in the plan.
    If a later step depends on creation or deletion, wait for the tool to report success first.
    If the user rejects a file change, stop.
    If the plan no longer fits the files, stop and explain why.
    """

    return run_agent(
        client = client,
        task = instruction,
        history = [],
        max_steps = 8,
        allowed_tools = APPLY_TOOLS,
        stop_on_file_change_rejection = True,
        changes = changes
    )
