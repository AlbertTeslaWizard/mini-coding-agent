import os
import subprocess
import sys
from pathlib import Path


def run_tests() -> str:
    root = Path().cwd().resolve()
    tests_dir = root / "tests"

    if (
        tests_dir.is_symlink()
        or not tests_dir.resolve().is_relative_to(root)
        or not tests_dir.is_dir()
    ):
        return "Error: Valid tests directory does not exist"

    confirmation = input("Run pytest? This will execute project test code. [y/N]:").strip().lower()
    if confirmation != "y":
        return "Error: Test execution rejected by user"

    test_env = {
        "PATH": os.environ.get("PATH", ""),
        "PYTHONNOUSERSITE": "1",
        "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"
    }

    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "tests"],
            cwd = root,
            capture_output = True,
            text = True,
            errors = "replace",
            timeout = 30,
            env = test_env,
            check = False
        )
    except subprocess.TimeoutExpired:
        return "Error: Test execution timed out after 30 seconds"
    except OSError as e:
        return f"Error: Failed to run tests: {e}"

    output = (result.stdout + "\n" + result.stderr).strip()
    output = output[-10000:]

    return f"Exit code: {result.returncode}\n{output}"
