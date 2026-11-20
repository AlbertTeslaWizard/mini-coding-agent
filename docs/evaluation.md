# Mini Coding Agent 端到端评测

## 第一组 · 读取、规划与确认写入

- 日期：2026-11-19
- 评测版本：`9625ad8`
- 配置模型：`deepseek-v4.1-flash`
- 方式：在独立 Git worktree 中启动 `python main.py`，按顺序手动运行四个场景。
- 结果：**4/4 场景通过**。完成 E04 后，全量回归测试为 **20 passed**。

### 任务输入

**E01 · 读取并解释**

```text
请读取 calculator.py 和 tests/test_calculator.py，解释 subtract 的实现，并列出当前测试覆盖的四种减法情况。只阅读和解释，不修改任何文件。
```

**E02 · 只读规划**

```text
/plan 在 calculator.py 中新增 multiply(a: int, b: int) -> int，返回两个整数的乘积。保留现有 add 和 subtract，不修改其他文件。请先检查代码，并给出验证方案。
```

**E03 · 拒绝补丁** — 执行 E02 留下的计划，看到补丁后输入 `n`，再运行 `/diff`。

**E04 · 批准补丁** — 重新提交 E02 的同一条 `/plan`，执行 `/apply`，看到补丁后输入 `y`，再运行 `/diff` 并在 shell 中做功能和回归验证。

### 结果与证据

| 场景 | 结果 | 实际观察 |
|---|---|---|
| E01 读取并解释 | PASS | 实际读取两个指定文件，正确说明 `subtract` 返回 `a - b`，四条测试断言与源码一致。`/diff` 显示工作区干净。 |
| E02 只读规划 | PASS | 只计划修改 `calculator.py`，给出独立功能验证和回归验证方案。没有写入请求，`/diff` 显示工作区干净。 |
| E03 拒绝补丁 | PASS | 实际展示补丁，输入 `n` 后立即停止。`/diff` 显示工作区干净。 |
| E04 批准补丁 | PASS | 输入 `y` 后只修改了 `calculator.py`，新增 `multiply`。四条乘法断言均通过，全量 `pytest` 返回 `20 passed`。 |

E04 的独立断言覆盖正数相乘、一正一负、两个负数相乘和乘以零。

## 第二组 · 确认新建、确认删除与连续撤销

- 日期：2026-11-19
- 评测版本：`9625ad8`
- 配置模型：`deepseek-v4.1-flash`
- 方式：在独立 Git worktree 中手动运行 CLI，并在第二个终端独立验证文件内容、Git 状态和回归测试。
- 结果：**3/3 场景通过**。评测结束后工作区干净，全量回归测试为 **`20 passed in 0.05s`**。

### 任务输入

**E05 · 确认新建**

```text
/plan 在仓库根目录新建 eval_probe.py，内容只有一行 MINI_AGENT_EVAL = 42，行末保留换行。不修改任何其他文件。
```

执行 `/apply`，确认预览中的路径和内容后输入 `y`，再运行 `/diff`。

**E06 · 确认删除**

```text
/plan 删除仓库根目录刚才创建的 eval_probe.py。只删除这一个文件，不修改其他文件。
```

执行 `/apply`，确认删除目标后输入 `y`，再运行 `/diff`。在另一个终端确认文件已不存在。

**E07 · 连续撤销** — 在同一个 Agent 进程中完成创建和删除，然后执行两次 `/undo`，每次撤销后都运行 `/diff` 检查文件状态。

### 结果与证据

| 场景 | 结果 | 实际观察 |
|---|---|---|
| E05 确认新建 | PASS | `/plan` 后工作区干净。输入 `y` 后，`write_file` 创建了 `eval_probe.py`，`/diff` 只显示 `?? eval_probe.py`。独立字节断言确认内容恰好为 `MINI_AGENT_EVAL = 42\n`。 |
| E06 确认删除 | PASS | 输入 `y` 后，`delete_file` 报告删除成功。`/diff` 显示工作区干净，独立文件检查确认 `eval_probe.py` 已不存在。 |
| E07 连续撤销 | PASS | 补跑时，第一次 `/undo` 撤销删除，`/diff` 重新显示 `?? eval_probe.py`。第二次 `/undo` 撤销创建，文件再次消失，`/diff` 显示 `Working tree is clean.`，`git status --short` 无输出。 |

## 第三组 · 测试执行确认与 `/repair` 修复闭环

- 日期：2026-11-20
- 评测版本：`9625ad8`
- 配置模型：`deepseek-v4.1-flash`
- 方式：在独立 Git worktree 中手动运行 CLI。E08 和 E09 验证工作流在调用模型前的停止条件，E10 使用真实模型修复手动注入的故障。
- 结果：**3/3 场景通过**。E10 第一次修复尝试成功，复测为 **`20 passed in 0.03s`**，最终 `/diff` 显示 `Working tree is clean.`。

### 任务输入

**E08 · 拒绝运行测试 / E09 · 测试已经通过**

两次使用同一条命令。看到 `Run pytest?` 后，E08 输入 `n`，E09 输入 `y`。完成两次操作后运行 `/diff`。

```text
/repair 检查当前测试，只在有失败时修复对应的实现，不修改测试文件。
```

**E10 · 修复已知故障**

在 `calculator.py` 中手动将 `add` 的 `return a + b` 改为 `return a - b`，保持测试文件不变。先在 shell 中运行 `python -m pytest -q` 复现故障，再启动 CLI 并输入：

```text
/repair 根据失败的测试定位问题。只修复 calculator.py 中导致失败的实现，保留其他行为，不修改测试或其他文件。
```

依次确认初次运行测试、应用单行补丁和运行修复后测试，最后用 `/diff` 检查工作区。

### 结果与证据

| 场景 | 结果 | 实际观察 |
|---|---|---|
| E08 拒绝运行测试 | PASS | 输入 `n` 后报告 `Test execution rejected by user`，未进入 `Agent Step`。 |
| E09 测试已经通过 | PASS | 输入 `y` 后报告 `All existing tests already pass`，未进入 `Agent Step`。E08 和 E09 完成后，`/diff` 显示工作区干净。 |
| E10 修复已知故障 | PASS | 注入故障后，`test_add_positive_numbers` 失败，`add(2, 3)` 返回 `-1`，全量测试为 `1 failed, 19 passed`。Agent 定位到 `add` 使用了减号。经确认，只把该行改回 `return a + b`，未修改 `subtract` 或测试文件。第一次修复尝试后，工作流复测退出码为 `0`，结果为 `20 passed in 0.03s`。最终 `/diff` 显示 `Working tree is clean.`。 |
