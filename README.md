# CCSpt 审核工具集

面向 CCSpt 嵌入式工程的审核 skills：以 **`ccspt-code-review` 为统一入口**，按目标选择电机参数或温控逻辑专项。也可以直接调用专项。

插件版本：**0.4.0**。当前支持参数审核及温控逻辑，尚未建立覆盖所有代码功能的专项规则。

## 三个入口，各负其责

| Skill | 职责 | 主要产物 | 版本 |
|---|---|---|---|
| [`ccspt-code-review`](plugins/ccspt-code-review-skill/skills/ccspt-code-review/SKILL.md) | 工具集总入口：选择专项、共享项目上下文、汇总结果 | 答复中汇总专项结果 | 0.1.0 |
| [`ccspt-motor-parameter-review`](plugins/ccspt-code-review-skill/skills/ccspt-motor-parameter-review/SKILL.md) | 电机参数、派生公式、硬件系数及保护关联审核 | 单文件离线 HTML | 0.3.0 |
| [`ccspt-thermostat-logic`](plugins/ccspt-code-review-skill/skills/ccspt-thermostat-logic/SKILL.md) | A 温控文档；B 客户要求核对；C 实现自检 | Markdown；A/B 关键规则与结论中英双语 | 0.2.0 |

总入口只加载相关专项。两个专项各自维护规则与输出，不重复存放到总入口，也不强制共用一种报告格式。

## 怎么使用

```text
使用 $ccspt-code-review 审核 <工程路径>，范围包括电机参数和温控逻辑自检。
立项单：<文件路径>；工程版本：<版本>。
```

已明确目标时可直接调用：

```text
使用 $ccspt-motor-parameter-review 审核 <matlab_variable.c 路径>。
立项单：<文件路径>；板卡和电机资料：<文件路径>。

使用 $ccspt-thermostat-logic 根据 <模型或代码路径> 生成温控逻辑文档。

使用 $ccspt-thermostat-logic 对照 <客户需求路径及版本>，逐条核对 <实现路径>。

使用 $ccspt-thermostat-logic 自检 <项目路径> 的温控状态机、计时器、启停统计和故障恢复。
```

- **参数正式审核**需要立项单，必要时还需电机、硬件与原理图资料。缺资料不从参数现值反推需求。确定性计算可独立执行，但不代表已完成审核。
- **温控需求核对**需要可追溯的客户要求；缺需求时可以按用户目标做实现自检，但不能宣称符合客户要求。
- 默认只读源工程。修改代码、模型或上传项目资料须有对应授权；示例中的数值、状态码及历史修复结论不作为项目默认规格。

## 安装与更新

本仓库保留现有发布标识，避免改变 marketplace 来源地址：

| 层级 | 名称 | 含义 |
|---|---|---|
| GitHub 仓库 / 插件包 | `ccspt-code-review-skill` | 发布与安装标识 |
| Marketplace | `ccspt-tools` | 插件集合标识 |
| 工具集调用入口 | `ccspt-code-review` | 选择具体审核专项 |

通过支持本仓库 marketplace 配置的宿主安装插件 `ccspt-code-review-skill`，插件包含以上三个 skill。Codex 和 Claude 的清单分别位于 [Codex marketplace](.agents/plugins/marketplace.json) 与 [Claude marketplace](.claude-plugin/marketplace.json)。本次只核对清单及目录，没有实际执行宿主安装。

手动安装到 Codex 时，将 `plugins/ccspt-code-review-skill/skills/` 下三个目录一起放入 `~/.codex/skills/`，保留相邻关系；Windows 默认位置为 `%USERPROFILE%\.codex\skills\`。仅需一个专项时也可单独安装该项目录；总入口依赖两个相邻专项，不宜单独安装。

已有安装的迁移：

- 旧 `ccspt-code-review` 曾承担电机参数审核；从本版起该名称恢复为工具集入口，原能力由 `ccspt-motor-parameter-review` 承担。更新时替换旧入口目录并安装专项，避免留下旧规则与新入口混用。
- 电机参数脚本从 `modules/motor-parameters/scripts/` 移到本专项 `scripts/`；外部脚本如引用旧路径，需同步调整。
- 电机参数专项保留审核前版本检查：发现新版本先询问是否更新；检测不可用时记录状态并继续。温控专项与总入口当前没有独立的自动版本检测脚本，随插件或手动安装更新。

## 文件结构

```text
ccspt-code-review-skill/
├── .agents/plugins/marketplace.json       # Codex 插件集合
├── .claude-plugin/marketplace.json        # Claude 插件集合
├── plugins/ccspt-code-review-skill/
│   ├── plugin.json                       # 插件元数据
│   ├── VERSION                           # 插件版本
│   ├── scripts/check_version.py          # 插件版本查询工具
│   └── skills/
│       ├── ccspt-code-review/             # 总入口：选择专项
│       │   ├── SKILL.md
│       │   ├── VERSION
│       │   └── agents/openai.yaml
│       ├── ccspt-motor-parameter-review/
│       │   ├── SKILL.md
│       │   ├── VERSION
│       │   ├── agents/openai.yaml
│       │   ├── references/               # 审核流程、规则、字典、基准、报告规范
│       │   └── scripts/                  # 计算、版本检查、HTML 生成及计算测试
│       └── ccspt-thermostat-logic/
│           ├── SKILL.md
│           ├── VERSION
│           ├── agents/openai.yaml
│           └── references/               # 三种模式的模板与示例
├── tests/                                # 发布结构与报告测试
└── adapters/deepseek-harness/             # 手动适配说明，无运行时集成
```

每个 skill 使用 `ccspt-<职责>` 命名，目录名与 frontmatter 的 `name` 一致。`SKILL.md` 放职责、流程与必要约束；规则、模板和案例按需读取；确定性工具放 `scripts/`。单一专项不再嵌套第二层 `modules/`。

## 开发与验证

计算和报告工具使用 Python 标准库。以下命令在**仓库根目录**执行：

```bash
python -m unittest discover -s tests -p "test_*.py"
python -m unittest discover -s plugins/ccspt-code-review-skill/skills/ccspt-motor-parameter-review/scripts -p "test_*.py"

python plugins/ccspt-code-review-skill/skills/ccspt-motor-parameter-review/scripts/calculate.py <参数文件> --output <计算结果.json>
python plugins/ccspt-code-review-skill/skills/ccspt-motor-parameter-review/scripts/render_report.py <报告输入.json> --output <报告.html>
```

计算结果 JSON 与报告输入 JSON 是不同格式；不能把计算结果直接作为正式报告。报告输入格式见 [报告规范](plugins/ccspt-code-review-skill/skills/ccspt-motor-parameter-review/references/report-policy.md)。

发布检查还会读取 Git 暂存区中的实际文本对象，避免工作区可读但提交内容不可解析的情况。发布前先暂存待发布文件，再执行测试。

自动检查覆盖发布目录、版本一致性、总入口引用、专项资源引用、参数版本查询路径、HTML 转义及重复问题 ID；计算测试覆盖安全算术、未解析条件、映射、独立基准和元数据检查。它们不能证明完整项目审核正确，也不等于模型仿真、宿主安装验证或实机验证。

项目原始代码、立项资料及审核产物留在用户工程，不自动上传。仓库中的字典和基准是有适用范围的参考资料，不能把样本值当成所有项目的要求。

许可证状态：`UNLICENSED`，尚未授予开源许可。
