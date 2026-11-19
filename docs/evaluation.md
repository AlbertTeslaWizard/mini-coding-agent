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