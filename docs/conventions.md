# Documentation Conventions

## 命名规范

- 周目录：`week-01`、`week-02`、`week-03`。
- 文件名：小写英文 + 连字符，例如 `summary.md`。
- 不再使用：`week1.md`、`WEEK1_EXECUTION_NOTES.md` 这类大小写混合、周次不可自然排序的命名。

## 推荐 Front Matter

每份周文档建议在顶部保留元信息：

```yaml
---
title: Week 02 Prompt
week: 02
type: prompt
tool: Claude Code
status: draft
---
```

常见 `type`：

- `prompt`：给 AI 编程工具的输入。
- `execution-summary`：AI 编程工具的执行总结。
- `design`：技术设计。
- `acceptance`：验收记录。
- `notes`：普通笔记。

## 内容建议

### prompt.md

建议包含：

1. 背景与目标。
2. 需要修改的目录或文件。
3. 验收标准。
4. 约束条件，例如不能提交密钥、必须保留现有接口兼容性。

### summary.md

建议包含：

1. 实际执行步骤。
2. 关键技术决策。
3. 遇到的问题和解决方式。
4. 验证命令与结果。
5. 后续 TODO。
