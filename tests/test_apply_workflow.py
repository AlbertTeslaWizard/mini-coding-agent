import json
from types import SimpleNamespace as NS

import pytest

from workflows.apply import PendingPlan, apply_workflow


@pytest.mark.parametrize(
    ("answers", "expected_values"),
    [
        (["n"], [1, 1, 1]),
        (["y", "n"], [2, 1, 1]),
    ],
)
def test_apply_stops_after_rejected_edit(
    tmp_path, monkeypatch, answers, expected_values
):
    monkeypatch.chdir(tmp_path)

    paths = [tmp_path / f"{name}.py" for name in ("first", "second", "third")]
    calls = []

    for index, path in enumerate(paths):
        path.write_text("value = 1\n", encoding="utf-8")
        calls.append(
            NS(
                type="function_call",
                name="edit_file",
                call_id=f"edit_{index}",
                arguments=json.dumps(
                    {
                        "path": path.name,
                        "old_string": "value = 1",
                        "new_string": "value = 2",
                    }
                ),
            )
        )

    remaining_answers = iter(answers)
    prompts = []
    model_calls = []

    def fake_input(prompt):
        prompts.append(prompt)
        return next(remaining_answers, "n")

    def fake_create(**kwargs):
        model_calls.append(1)
        if len(model_calls) == 1:
            return NS(output=calls, output_text="")
        return NS(output=[], output_text="Done")

    monkeypatch.setattr("builtins.input", fake_input)
    client = NS(responses=NS(create=fake_create))

    result = apply_workflow(
        client,
        PendingPlan(task="Update values", text="Edit all three files"),
    )

    assert "Edit rejected by user" in result
    assert len(prompts) == len(answers)
    assert len(model_calls) == 1
    assert [path.read_text(encoding="utf-8") for path in paths] == [
        f"value = {value}\n" for value in expected_values
    ]

@pytest.mark.parametrize(
    ("answers", "created"),
    [
        (["n"], False),
        (["y", "y"], True),
    ],
)
def test_apply_create_file_then_edit(tmp_path, monkeypatch, answers, created):
    monkeypatch.chdir(tmp_path)
    main_file = tmp_path / "main.py"
    main_file.write_text("print(1)\n", encoding="utf-8")
    utils_file = tmp_path / "utils.py"

    def make_call(name, **arguments):
        return NS(
            type="function_call",
            name=name,
            call_id=f"call_{name}",
            arguments=json.dumps(arguments),
        )

    calls = [
        make_call("write_file", path="utils.py", content="VALUE = 42\n"),
        make_call(
            "edit_file",
            path="main.py",
            old_string="print(1)",
            new_string="from utils import VALUE\n\nprint(VALUE)",
        ),
    ]

    remaining = iter(answers)
    prompts = []
    model_calls = []

    def fake_input(prompt):
        prompts.append(prompt)
        return next(remaining, "n")

    def fake_create(**kwargs):
        model_calls.append(1)
        offered_tools = {tool["name"] for tool in kwargs["tools"]}
        assert "write_file" in offered_tools
        assert "delete_file" not in offered_tools

        if len(model_calls) == 1:
            return NS(output=calls, output_text="")
        return NS(output=[], output_text="Done")

    monkeypatch.setattr("builtins.input", fake_input)
    client = NS(responses=NS(create=fake_create))

    result = apply_workflow(
        client,
        PendingPlan(
            task="Move the value to utils.py",
            text="Create utils.py, then import VALUE in main.py",
        ),
    )

    assert len(prompts) == len(answers)

    if created:
        assert utils_file.read_text(encoding="utf-8") == "VALUE = 42\n"
        assert main_file.read_text(encoding="utf-8") == (
            "from utils import VALUE\n\nprint(VALUE)\n"
        )
        assert result == "Done"
    else:
        assert not utils_file.exists()
        assert main_file.read_text(encoding="utf-8") == "print(1)\n"
        assert "File creation rejected by user" in result
        assert len(model_calls) == 1
