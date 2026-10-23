# CCSpt Code Review Skill

版本 **0.3.1**：同一插件集中管理独立 skill。现含电机参数审核与温控逻辑工具。

- 保留使用前GitHub版本检查：有新版询问是否更新；检测不可用记录状态并继续，不静默安装。
- 参数模块：项目输入、规则/字典、间接解码、RX13T共同计算及保护关联。
- 单文件HTML：按优先级排序、搜索筛选、点击展开；范围冲突合并表格。

入口：`plugins/ccspt-code-review-skill/skills/ccspt-motor-parameter-review/SKILL.md`。
模块：入口目录的 `modules/motor-parameters/MODULE.md`。

安装使用现有 Codex/Claude 插件 marketplace，插件名保持 `ccspt-code-review-skill`。安装插件可发现两个 skill；直接安装时按需选择对应 skill 目录，不另装电机参数模块。

调用：使用 `$ccspt-motor-parameter-review` 审核指定项目的 `matlab_variable.c`。正式审核先提供立项单及必要电机/硬件资料。

计算：`python modules/motor-parameters/scripts/calculate.py <参数文件> --output <计算结果.json>`，仅计算准备，不代表正式审核。
报告：`python scripts/render_report.py <报告.json> --output <报告.html>`。
验证：在仓库根运行 `python -m unittest discover -s tests -p "test_*.py"`；模块计算测试可单独运行其 `test_calculate.py`。

不会自动上传公司代码、资料或反馈。参数字典和基准只作为审核参考，不代表所有项目相同配置。更新按实际反馈迭代。

## Skill 命名与调用

统一使用 `ccspt-<领域或功能>`，目录名与 SKILL.md 中的 name 一致，后续新增能力按职责独立命名。

| Skill | 用途 | 版本 |
|---|---|---|
| `ccspt-motor-parameter-review` | 电机参数及派生计算审核 | 0.2.1 |
| `ccspt-thermostat-logic` | 温控文档、客户要求核对、实现自检 | 0.1.0 |

温控入口：[SKILL.md](plugins/ccspt-code-review-skill/skills/ccspt-thermostat-logic/SKILL.md)。

调用示例：

- `使用 $ccspt-thermostat-logic，根据 <模型路径> 生成温控逻辑文档。`
- `使用 $ccspt-thermostat-logic，对照 <客户需求路径及版本> 核对 <模型或代码路径>，范围为全部条款。`
- `使用 $ccspt-thermostat-logic，自检 <项目路径> 的温控计数器、状态机与故障恢复逻辑。`

温控工具默认只读实现；需求核对需可追溯的客户要求。示例中的数字、时间和状态码仅用于演示，不能替代当前项目证据。本次发布完成结构与引用验证，未执行实际模型仿真或实机验证。

电机参数 skill 从 `ccspt-code-review` 更名为 `ccspt-motor-parameter-review`，后续使用新名称调用。已直接安装旧 skill 的用户需安装新目录并移除旧安装，避免重复发现；插件及仓库名称保持不变。
