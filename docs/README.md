# Docs

本目录用于沉淀 AI Knowledge Copilot 每周迭代资料。为了便于后续 Week 02、Week 03 继续追加，文档按“周”分组，并在每周目录里区分输入给 AI 编程工具的 prompt、工具执行总结、设计说明和验收记录。

## 目录结构

```text
docs/
├─ README.md
├─ conventions.md
└─ weeks/
   ├─ README.md
   ├─ week-01/
   │  ├─ prompt.md                # 喂给 Claude Code 的原始任务/需求
   │  └─ claude-code-summary.md   # Claude Code 执行过程总结
   ├─ week-02/
   │  ├─ prompt.md
   │  ├─ claude-code-summary.md
   │  ├─ design.md                # 可选：方案、架构、接口设计
   │  └─ acceptance.md            # 可选：验收结果、测试记录
   └─ week-03/
      └─ ...
```

## 当前文档

| 周次 | 文档 | 说明 |
|---|---|---|
| Week 01 | `weeks/week-01/prompt.md` | 第 1 周喂给 Claude Code 的 prompt，目标是搭建 FastAPI 基础服务。 |
| Week 01 | `weeks/week-01/claude-code-summary.md` | Claude Code 对第 1 周执行过程、关键决策和验证结果的总结。 |

## 推荐新增文档规则

新增一周时，优先创建：

```text
docs/weeks/week-02/prompt.md
docs/weeks/week-02/claude-code-summary.md
```

如果该周内容较复杂，再按需增加：

- `design.md`：技术方案、接口设计、数据结构、架构图说明。
- `acceptance.md`：验收清单、测试命令、运行截图/结果摘要。
- `notes.md`：临时笔记、排障过程、未决问题。

文件命名统一使用小写英文和连字符，避免 `week1.md`、`WEEK1_EXECUTION_NOTES.md` 这类难以扩展和排序的命名。
