import json
from types import SimpleNamespace as NS

import pytest

from workflows.apply import PendingPlan, apply_workflow

from tools.change_log import undo_last_change
from tools.file_ops import delete_file

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
    original = b"old file\r\n"
    obsolete.write_bytes(original)

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

    changes = []
    result = apply_workflow(
        client,
        PendingPlan(
            task="Remove an obsolete file and update notes",
            text="Delete obsolete.txt, then edit notes.txt",
        ),
        changes=changes,
    )

    assert prompts[0] == "Confirm deletion of obsolete.txt? [y/N]: "
    assert len(prompts) == len(answers)

    if deleted:
        assert result == "Done"
        assert not obsolete.exists()
        assert notes.read_text(encoding="utf-8") == "after\n"
        assert len(changes) == 2

        # 第一次撤销只恢复 notes.txt。
        assert undo_last_change(changes).startswith("Undid")
        assert notes.read_text(encoding="utf-8") == "before\n"
        assert not obsolete.exists()

        # 第二次撤销才恢复 obsolete.txt，包括原始的 CRLF 换行。
        assert undo_last_change(changes).startswith("Undid")
        assert obsolete.read_bytes() == original
        assert changes == []
    else:
        # 拒绝删除后，不执行后续编辑，也不留下撤销记录。
        assert result.startswith("Apply stopped: Deletion rejected by user")
        assert obsolete.read_bytes() == original
        assert notes.read_text(encoding="utf-8") == "before\n"
        assert len(model_calls) == 1
        assert changes == []


def test_undo_delete_does_not_overwrite_new_file(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("builtins.input", lambda _: "yes")

    path = tmp_path / "obsolete.txt"
    path.write_bytes(b"")
    changes = []

    assert delete_file(path.name, changes=changes).startswith("Successfully deleted")
    assert not path.exists()

    # 用户在同一路径新建了文件，撤销不能覆盖它。
    path.write_bytes(b"new content")
    assert "already exists" in undo_last_change(changes)
    assert path.read_bytes() == b"new content"
    assert len(changes) == 1

    # 移走冲突后，可以用保留的撤销记录恢复原来的空文件。
    path.unlink()
    assert undo_last_change(changes).startswith("Undid")
    assert path.read_bytes() == b""
    assert changes == []