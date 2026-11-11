import shlex
import subprocess
from pathlib import Path

ALLOWED_COMMANDS = {
    ("pwd",),
    ("ls",),
    ("ls", "-la"),
    ("git", "status", "--short"),
}

def run_shell(command: str) -> str:
    root = Path.cwd().resolve()

    # 1. 解析命令
    try:
        args = shlex.split(command)
    except ValueError as e:
        return f"Error: Invalid command: {e}"

    if not args:
        return "Error: Empty command"

    # 2. 验证命令白名单
    if tuple(args) not in ALLOWED_COMMANDS:
        return F"Error: Command not allowed: {command}"

    # 3. 用户确认
    print(f"\nWorking directory: {root}")
    print(f"Command: {command}")

    try:
        confirmation = input(
            "Execute this command? [y/N]:"
        ).strip().lower()
    except EOFError:
        return "Error: Command execution rejected"

    if confirmation != "y":
        return "Error: Command execution rejected"

    try:
        result = subprocess.run(
            args,
            cwd=root,
            shell=False,
            capture_output=True,
            text=True,
            errors="replace",
            timeout=15,
            check=False
        )
    except subprocess.TimeoutExpired:
        return "Error: Command timed out after 15 seconds"

    except OSError as e:
        return f"Error: Failed to execute command: {e}"

    stdout = result.stdout.rstrip("\r\n")
    stderr = result.stderr.rstrip("\r\n")

    output = "\n".join(
        part for part in (stdout, stderr) if part
    )

    output = output[-10000:]

    return (
        f"Exit code: {result.returncode}\n"
        f"{output}"
    )
