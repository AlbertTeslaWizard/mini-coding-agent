import json
from types import SimpleNamespace as NS

import workflows.repair as repair_module


def test_repair_rejects_editing_test_files(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    target = tmp_path / "tests" / "test_calculator.py"
    target.parent.mkdir()
    original = b"def test_calculator():\n    assert 1 + 1 == 2\n"
    target.write_bytes(original)

    # 让 /repair 进入修复分支，不在这条测试里再启动一轮 pytest。
    monkeypatch.setattr(
        repair_module,
        "run_tests",
        lambda: "Exit code: 1\nSimulated test failure",
    )

    def unexpected_confirmation(*args, **kwargs):
        raise AssertionError("A blocked edit should not ask for confirmation")

    monkeypatch.setattr("builtins.input", unexpected_confirmation)

    edit_call = NS(
        type="function_call",
        name="edit_file",
        call_id="check_edit_guard",
        arguments=json.dumps(
            {
                "path": "tests/test_calculator.py",
                "old_string": "assert 1 + 1 == 2",
                "new_string": "assert True",
            }
        ),
    )

    tool_results = []

    def fake_create(**kwargs):
        for item in kwargs["input"]:
            if (
                isinstance(item, dict)
                and item.get("type") == "function_call_output"
                and item.get("call_id") == edit_call.call_id
            ):
                tool_results.append(item["output"])

        if tool_results:
            return NS(output=[], output_text="Directory guard checked.")

        return NS(output=[edit_call], output_text="")

    client = NS(responses=NS(create=fake_create))

    repair_module.repair_workflow(
        client,
        "Try editing tests/test_calculator.py",
        max_attempts=1,
    )

    assert tool_results == [
        (
            "Error: Editing files in this directory is not allowed: "
            "tests/test_calculator.py"
        )
    ]
    assert target.read_bytes() == original