import json
from types import SimpleNamespace as NS

import pytest

from workflows.apply import PendingPlan, apply_workflow


@pytest.mark.parametrize(
    ("answers", "deleted"),
    [
        (["y", "y"], True),
        (["n"], False),
        ([""], False),
    ],
)
def test_apply_delete_file_requires_confirmation(
    tmp_path, monkeypatch, answers, deleted
):
    monkeypatch.chdir(tmp_path)

    obsolete = tmp_path / "obsolete.txt"
    obsolete.write_text("old file\n", encoding="utf-8")

    notes = tmp_path / "notes.txt"
    notes.write_text("before\n", encoding="utf-8")

    def make_call(name, **args):
        return NS(
            type="function_call",
            name=name,
            call_id=f"call_{name}",
            arguments=json.dumps(args),
        )

    calls = [
        make_call("delete_file", path="obsolete.txt"),
        make_call(
            "edit_file",
            path="notes.txt",
            old_string="before",
            new_string="after",
        ),
    ]

    remaining = iter(answers)
    prompts = []
    model_calls = []

    def fake_input(prompt):
        if not prompts:
            assert obsolete.is_file()
        prompts.append(prompt)
        return next(remaining, "n")

    def fake_create(**kwargs):
        model_calls.append(1)
        assert "delete_file" in {tool["name"] for tool in kwargs["tools"]}
        if len(model_calls) == 1:
            return NS(output=calls, output_text="")
        return NS(output=[], output_text="Done")

    monkeypatch.setattr("builtins.input", fake_input)
    client = NS(responses=NS(create=fake_create))

    result = apply_workflow(
        client,
        PendingPlan(
            task="Remove an obsolete file and update notes",
            text="Delete obsolete.txt, then edit notes.txt",
        ),
    )

    assert prompts[0] == "Confirm deletion of obsolete.txt? [y/N]: "
    assert len(prompts) == len(answers)

    if deleted:
        assert result == "Done"
        assert not obsolete.exists()
        assert notes.read_text(encoding="utf-8") == "after\n"
    else:
        assert result.startswith("Apply stopped: Deletion rejected by user")
        assert obsolete.read_text(encoding="utf-8") == "old file\n"
        assert notes.read_text(encoding="utf-8") == "before\n"
        assert len(model_calls) == 1