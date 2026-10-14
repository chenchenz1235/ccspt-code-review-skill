# CCSpt Code Review Skill

版本 **0.2.0**：一个审核入口，多个按需加载模块。当前包含电机参数模块，不包含空模块或旧字符串复制演示规则。

- 保留使用前GitHub版本检查：有新版询问是否更新；检测不可用记录状态并继续，不静默安装。
- 参数模块：项目输入、规则/字典、间接解码、RX13T共同计算及保护关联。
- 单文件HTML：按优先级排序、搜索筛选、点击展开；范围冲突合并表格。

入口：`plugins/ccspt-code-review-skill/skills/ccspt-code-review/SKILL.md`。
模块：入口目录的 `modules/motor-parameters/MODULE.md`。

安装仍使用现有Codex/Claude插件marketplace；直接安装时只安装 `ccspt-code-review`，不另装模块。

调用：使用 `$ccspt-code-review` 审核指定项目的 `matlab_variable.c`。正式审核先提供立项单及必要电机/硬件资料。

计算：`python modules/motor-parameters/scripts/calculate.py <参数文件> --output <计算结果.json>`，仅计算准备，不代表正式审核。
报告：`python scripts/render_report.py <报告.json> --output <报告.html>`。
验证：在仓库根运行 `python -m unittest discover -s tests -p "test_*.py"`；模块计算测试可单独运行其 `test_calculate.py`。

不会自动上传公司代码、资料或反馈。参数字典和基准只作为审核参考，不代表所有项目相同配置。更新按实际反馈迭代。
