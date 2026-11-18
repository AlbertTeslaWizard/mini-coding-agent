from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class FileChange:
    path: Path
    before: bytes | None
    after: bytes | None

def undo_last_change(changes: list[FileChange]) -> str:
    if not changes:
        return "No file changes to undo."

    change = changes[-1]
    root = Path.cwd().resolve()
    target = change.path

    try:
        if not target.is_relative_to(root) or target.resolve() != target:
            return "Error: Undo target is no longer a safe project path"

        relative_path = target.relative_to(root)

        if change.after is None:
            # 撤销删除: 在原路径重新创建文件
            if change.before is None:
                return "Error: Invalid deletion record"

            try:
                with target.open("xb") as file:
                    file.write(change.before)
            except FileExistsError:
                return f"Error: {relative_path} already exists. Nothing undone."
        else:
            if not target.is_file() or target.read_bytes() != change.after:
                return f"Error: {relative_path} changed since /apply. Nothing undone."

            if change.before is None:
                target.unlink()
            else:
                target.write_bytes(change.before)

    except (OSError, RuntimeError) as exc: 
        return f"Error: Undo failed: {exc}"

    changes.pop()
    return f"Undid last change to {relative_path}"