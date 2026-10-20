# agent（占位）

Python + FastAPI + LangGraph + SQLGlot 的 Agent 服务，实现意图识别、Schema 检索、查询规划、SQL 生成与校验、结论生成。属第三、四阶段，当前仅占位。

任何 Text-to-SQL 执行必须遵守 PRD 的只读权限与校验规则：受限查询计划 → AST 校验 → 表白名单 → 只读账号，禁止运行未经验证的 SQL。
