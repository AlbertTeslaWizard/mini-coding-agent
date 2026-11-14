import subprocess

def get_git_diff() -> str:
    def git(*args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["git", "--no-pager", *args],
            capture_output = True,
            text = True,
            encoding = "utf-8",
            errors = "replace",
            timeout = 5 
        )

    try:
        status = git("status", "--short", "--untracked-files=all")
        if status.returncode != 0:
            return f"Error: git status failed: {status.stderr.strip()}"
        if not status.stdout:
            return "Working tree is clean."

        patch = git(
            "diff", "--no-color", "--no-ext-diff", "--no-textconv",
            "HEAD", "--",
        )

    except FileNotFoundError:
        return "Error: Git is not installed or not on PATH."
    except subprocess.TimeoutExpired:
        return "Error: Git command timed out."

    status_text = status.stdout.rstrip("\n")

    if patch.returncode != 0:
        return f"{status_text}\n\nPatch unavailable: {patch.stderr.strip()}"

    if not patch.stdout:
        return f"{status_text}\n\nNo tracked-file patch against HEAD."

    patch_text = patch.stdout.rstrip("\n")
    return f"{status_text}\n\n{patch_text}"