from tools.shell_ops import run_shell


def test_run_shell_pwd(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "builtins.input",
        lambda _: "y"
    )

    result = run_shell("pwd")

    assert "Exit code: 0" in result
    assert str(tmp_path) in result

def test_run_shell_rejects_unknown_command():
    result = run_shell("rm -rf .")
    assert "Error: Command not allowed" in result

def test_run_shell_rejects_injection(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    target = tmp_path / "injected.txt"

    result = run_shell(
        "pwd; touch injected.txt"
    )

    assert "Error: Command not allowed" in result
    assert not target.exists()

def test_run_shell_user_rejection(monkeypatch):
    monkeypatch.setattr(
        "builtins.input",
        lambda _: "n"
    )

    result = run_shell("pwd")
    assert result == "Error: Command execution rejected" in result

def test_run_shell_invalid_quotes():
    result = run_shell('ls "unfinished')
    assert "Error: Invalid command" in result
