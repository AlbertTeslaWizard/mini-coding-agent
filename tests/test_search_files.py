from tools.file_ops import search_files


def test_search_files_in_subdirectory(tmp_path, monkeypatch):
    folder = tmp_path / "src"
    folder.mkdir()

    # 创建测试文件
    target = folder / "example.py"
    target.write_text(
        "HELLO_AGENT = True\n",
        encoding="utf-8"
    )

    # 将工作目录切换到临时目录
    monkeypatch.chdir(tmp_path)

    # 执行搜索
    result = search_files("hello_agent")

    # 验证结果
    assert "src/example.py:1" in result
