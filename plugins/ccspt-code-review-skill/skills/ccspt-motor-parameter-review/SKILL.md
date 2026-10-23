---
name: ccspt-motor-parameter-review
description: 审核CCSpt电机控制参数及派生计算，结合项目资料输出按优先级排序、可展开的HTML报告；也用于维护审核规则。
license: UNLICENSED
compatibility: Requires repository read access. Network access is optional and used only to check for a newer skill version.
---

# CCSpt 电机参数审核

审核电机控制参数、派生计算及相关保护设置，按需加载电机参数审核流程。通用代码审查和温控逻辑不属于本 skill 的专项范围。默认只读审核，不修改固件。

## Pre-review update gate


Complete this gate before opening, reading, or analyzing any requested source file, diff, or review target.

1. Read `VERSION` and record it as `skill_version`.
2. Check the latest `plugins/ccspt-code-review-skill/skills/ccspt-motor-parameter-review/VERSION` on the GitHub repository. Prefer an authenticated GitHub connector when the harness provides one; otherwise run `scripts/check_version.py`.
3. If the installed version is current, continue directly to the review.
4. If a newer version exists, stop before processing the review target and tell the user both versions: `发现新版本：当前 <installed>，最新 <latest>。是否先更新？` Wait for the user's choice.
5. If the user chooses to update, use the harness's supported Skill or plugin update mechanism, verify the installed version, and only then begin processing the review target. If updating fails or no updater is available, explain the problem and ask whether to continue with the installed version.
6. If the user declines or postpones the update, continue with the installed version.
7. Never install an update without the user's choice. If the update check is unavailable, do not block the review; record the unavailable status and continue.


## 范围与依据

先确认目标文件、工程版本、用户约束和已有证据。执行上述更新检测后再读取审核目标。

| 用户任务 | 按需加载 |
|---|---|
| matlab_variable.c、motor参数、派生计算、硬件系数、周期及参数字典 | [电机参数审核流程](references/review-workflow.md) |
| 更新规则或复核反馈 | 加载审核流程及[报告规范](references/report-policy.md) |
| 尚无模块的代码功能 | 明确专项规则尚未建立，依据用户提供的规则处理，不套用已移除的演示规则 |

立项单、电机/硬件资料和缺失信息处理由审核流程定义；项目公共信息共用，不能从文件名推断电压/功率等级。同一问题的交叉证据合并呈现。

## 统一输出

读取[报告与优先级规范](references/report-policy.md)。默认交付离线HTML，问题概览表按高/中/低排序；点击展开证据、计算和建议，支持搜索筛选。优先级与确认状态独立。

报告记录skill版本、更新检测状态、规则来源、目标版本/文件范围、项目依据、检查及未检查内容。真实参数名/含义优先，内部编码只用于计算追溯；范围冲突合并明细表。功能/保护风险优先于元数据。

使用 `scripts/render_report.py <结构化报告.json> --output <报告.html>`。结构见[报告数据格式](references/report-policy.md)。计算JSON不是完整报告输入，必须由审核者根据证据整理 findings。

## 规则维护

用户确认覆盖旧规则。新增例外注明项目与适用条件，不能推广为所有项目都通过。项目资料留在用户工程，本 skill 不包含示例工程源代码、原理图或客户立项资料。

如请求反馈，按[反馈格式](references/feedback-schema.md)生成本地脱敏包；不自动上传。维护本 skill 的入口、流程、脚本和版本后，运行离线测试，再发布。
