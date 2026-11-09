import os
from pathlib import Path


# 实现文件读取工具
def read_file(path: str) -> str:
    root = Path.cwd().resolve()
    target = (root / path).resolve()

    if not target.is_relative_to(root):
        return "Error: Access outside project is denied"

    if target.suffix.lower() not in [".md", ".txt", ".py"]:
        return "Error: Unsupported file type"

    if not target.is_file():
        return "Error: File does not exist"

    with target.open("r", encoding="utf-8") as file:
        return file.read(10000)

# 实现目录列举工具
def list_dir(path: str) -> str:
    root = Path.cwd().resolve()
    target = (root / path).resolve()

    if not target.is_relative_to(root):
        return "Error: Access outside project is denied"

    if not target.is_dir():
        return "Error: Directory does not exist"

    entries = sorted(
        target.iterdir(),
        key=lambda entry: entry.name.lower()
    )

    if not entries:
        return "(empty directory)"

    output: list[str] = []
    for entry in entries[:100]:
        if entry.is_dir():
            output.append(f"[DIR] {entry.name}/")
        else:
            output.append(f"[FILE] {entry.name}")

    if len(entries) > 100:
        output.append("... more entries omitted")

    return "\n".join(output)

def search_files(query: str) -> str:
    if not query:
        return "Error: Empty search query"

    root = Path.cwd().resolve()
    query = query.lower()
    matches: list[str] = []

    for folder, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = [
            d for d in dirs
            if d not in {".git", ".venv", "__pycache__", "node_modules"}
            and not (Path(folder) / d).is_symlink()
        ]

        for name in sorted(files):
            path = Path(folder) / name
            if path.suffix.lower() not in {".py", ".md", ".txt"} or path.is_symlink():
                continue

            try:
                if not path.resolve().is_relative_to(root) or path.stat().st_size > 1024 * 1024:
                    continue
                lines = path.read_text(encoding="utf-8").splitlines()
            except (OSError, UnicodeError):
                continue

            for i, line in enumerate(lines, 1):
                if query in line.lower():
                    text = line.strip()
                    if len(text) > 200:
                        text = text[:200] + "..."

                    matches.append(f"{path.relative_to(root)}:{i}: {text}")

                    if len(matches) == 20:
                        return "\n".join(matches) + "\n[Match limit reached]"

    return "\n".join(matches) if matches else "No matches found"


def edit_file(path: str, old_string: str, new_string: str) -> str:
    root = Path.cwd().resolve()
    target = (root / path).resolve()

    if not target.is_relative_to(root):
        return "Error: Access outside project is denied"

    if target.suffix.lower() not in {".md", ".txt", ".py"}:
        return "Error: Unsupported file type"

    if not target.is_file():
        return "Error: File does not exist"

    if not old_string:
        return "Error: old_string cannot be empty"

    if old_string == new_string:
        return "Error: No changes requested"

    if target.stat().st_size > 1_000_000:
        return "Error: File is too large to edit"

    content = target.read_text(encoding="utf-8")

    count = content.count(old_string)
    if count == 0:
        return "Error: old_string not found"
    if count > 1:
        return f"Error: old_string occurs {count} times"

    new_content = content.replace(
        old_string,
        new_string,
        1
    )

    print(f"\nFile: {target.relative_to(root)}")
    print(f"Old:\n{old_string}")
    print(f"New:\n{new_string}")

    confirmation = input("\nApply this edit? [y/N]: ")

    if confirmation.strip().lower() != "y":
        return "Error: Edit rejected by user"

    target.write_text(new_content, encoding="utf-8")

    return f"OK: Updated {target.relative_to(root)}"

def write_file(path: str, content: str) -> str:
    root = Path.cwd().resolve()
    target = (root / path).resolve()

    if not target.is_relative_to(root):
        return "Error: Access outside project is denied"

    if target.suffix.lower() not in {".md", ".py", ".txt"}:
        return "Error: Unsupported file types"

    if target.exists():
        return "Error: File already exists"

    if not target.parent.is_dir():
        return "Error: Parent directory does not exist"

    if len(content.encode("utf-8")) > 100_000:
        return "Error: Content is too large"

    print(f"\nNew file: {target.relative_to(root)}")
    print(f"Content preview:\n{content[:500]}")

    if len(content) > 500:
        print("... (preview truncated)")

    confirmation = input("\nCreate this file? [y/N]: ")
    if confirmation.strip().lower() != "y":
        return "Error: File creation rejected by user"

    with target.open("x", encoding="utf-8") as file:
        file.write(content)

    return f"OK: Created {target.relative_to(root)}"

def delete_file(path: str) -> str:
    root = Path.cwd().resolve()
    requested = root / path

    if requested.is_symlink():
        return "Error: Symbolic links cannot be deleted"

    target = requested.resolve()

    if not target.is_relative_to(root):
        return "Error: Access outside project is denied"

    if target.suffix.lower() not in {".py", ".md", ".txt"}:
        return "Error: Unsupported file type"

    if not target.is_file():
        return "Error: File does not exist or is not a regular file"

    relative_path = target.relative_to(root)

    confirm = input(f"Confirm deletion of {relative_path}? [y/N]: ").strip().lower()
    if confirm not in {"y", "yes"}:
        return "Deletion cancelled by user"

    # 删除文件
    try:
        target.unlink()
    except OSError as e:
        return f"Error: Failed to delete file: {e}"

    return f"Successfully deleted {relative_path}"