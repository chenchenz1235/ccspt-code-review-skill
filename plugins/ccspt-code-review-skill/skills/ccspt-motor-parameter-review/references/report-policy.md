# 报告规范

功能和保护风险优先核实；元数据冲突低优先级。高/中/低是处理顺序，confirmed、needs-confirmation、advisory、missing-evidence是独立证据状态。经验范围偏离不等于确认故障。

每项包含稳定id、priority（high/medium/low）、status、category、title、parameter（可读名/真实变量）、current、recommendation、evidence（字符串数组）。可选 details_table={columns:[],rows:[[]]} 用于合并范围冲突和多参数建议。关闭功能的范围冲突仍保留，不能把错误备注强行当作工程正确值。

顶层JSON：title、project、skill_version、update_check、scope、findings、checks（字符串数组）、limitations（字符串数组）。不公开当前项目原始源码和敏感资料。所有动态文本HTML转义；单文件离线，无网络请求。

停机建议给出推荐值和原因；参数模块示例为顺风能力30%，stop_wr=0.3speed_max，忽略代码偏移。产测特殊覆盖和允许的MTPA覆盖不提示。间接参数单位不提示，但实际解码关系保留。

普通代码专项模块尚未建立，不自动沿用演示strcpy规则。优先级政策不代替模块具体判断。
