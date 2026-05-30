---
name: sci-paper-review
description: AI辅助SCI论文同行评审，严格6状态工作流；上传PDF极速解析，按需加载方法结论；输入最终定稿后AI全面客观审查并展示结果，用户确认后生成地道英文报告；适用于需要客观审查支持、学术规范报告撰写的场景
dependency:
  python:
    - PyMuPDF==1.23.8
---

# SCI Paper Peer Review System

## 任务目标
提供严格的SCI论文同行评审辅助工作流，确保审稿过程客观、规范、可追溯。

## 核心原则

### AI允许操作
- PDF封面+摘要极速解析（延迟加载方法/结论）
- 审稿意见存在性检查
- 数据一致性验证
- 格式规范性检查
- 逻辑自洽性检测
- 全文客观核查（逻辑矛盾、数据自洽性、图表规范、引文规范、实验信息缺失、语言问题）
- 审稿意见结构化存储与整理
- 报告格式生成

### AI禁止操作（严格禁止）
- 捏造论文中不存在的问题
- 臆测作者动机或意图
- 冒充审稿人做出最终学术判断
- 伪造数据、引用或实验结果
- 在不确定情况下做出确定性结论
- 代替人工完成创新性评价

### 信息标注规范
- **[Uncertain]**: AI不确定的内容，必须标注
- **[AI reference comments, only for expert personal reference, not valid for official review]**: AI参考观点，仅供专家个人参考，不作为正式审稿依据

## 状态机工作流

### 状态定义
| State | 名称 | 说明 | 触发 |
|-------|------|------|------|
| 1 | PARSING | PDF封面极速解析 | 用户上传PDF |
| 2 | CONFIRMATION | 元数据确认 | 用户确认 |
| 3 | REVIEWING | 审稿意见收集 | 用户多轮输入 |
| 4 | PARAM_COLLECTION | 参数采集 | 用户发送"最终定稿" |
| 5 | AI_AUDIT | AI客观审查 | 审查完成 |
| 6 | REPORT_READY | 报告生成 | 报告输出 |

### State 1: PARSING (PDF极速解析)
用户上传论文PDF，执行极速解析：
```
python scripts/pdf_parser.py --input <pdf_path> --output metadata.json --mode fast
```
提取内容：标题、期刊、作者、DOI、摘要、关键词（仅封面信息，不解析方法/结论/参考文献）

### State 2: CONFIRMATION (元数据确认)
展示解析结果供用户核对：
- 展示完整元数据清单
- 用户确认无误后回复"确认"或"ok"

### State 3: REVIEWING (审稿意见收集)
用户提供审稿意见，支持多轮输入。展示9维度审稿清单：
```
9维度审稿清单
请按以下维度提供你的审稿意见，可以分批次、随意顺序，想到什么说什么：

研究创新性 — 创新点是否足够？和已有工作区别在哪？
理论机理 — 理论基础是否充分？机理解释是否自洽？
方法学 — 材料/样品制备、表征方法是否合理？可重复性？
实验设计 — 对照组设置、变量控制是否严谨？
数据分析 — 统计方法、误差分析是否充分？
结果解释 — 性能提升归因是否可靠？有无过度解读？
论文写作 — 逻辑、表达、语法有无问题？
图表规范 — 图表是否清晰、信息量是否足够？
参考文献 — 引用是否完整、格式是否统一？
```
回复模板：
```
已收到您的审稿意见，正在保存...
已保存本次审稿意见，您可继续补充内容。全部意见提交完成后，请发送【最终定稿】，我将生成正式英文审稿报告。
```

**意见格式要求**:
```
Severity: Fatal/Major/Minor/Editorial
Category: 维度名称
Location: Section X.X, Page X, Paragraph X
Content: 具体审稿意见内容
Evidence: 引用原文或数据作为证据
```

### State 4: PARAM_COLLECTION (参数采集)
用户发送【最终定稿】后，收集审稿参数：
- 创新性等级: Original/Incremental/Derivative
- 学术影响力: High/Medium/Low
- 英文写作水平: Excellent/Good/Adequate/Poor
- 审稿态度: Constructive/Critical/Neutral
- 目标期刊类型: Nature/Science类/Advanced Materials类/ACS类/IEEE类/Elsevier类/Springer类/Other

### State 5: AI_AUDIT (AI客观审查)
执行全面硬核审查：
```
python scripts/conflict_detector.py --input reviews.json --metadata metadata.json --pdf <pdf_path> --output conflicts.json
```

**展示机制**:
审查完成后，分两个方面展示结果：

**第一部分：AI客观核查结果（格式规范性核查）**
如实展示以下方面的详细核查结果，只客观陈述事实，标注问题位置：
- 全文逻辑一致性（摘要-方法-结论逻辑链）
- 数据自洽性（数字格式、单位一致性）
- 图表/公式/符号规范（引用格式一致性）
- 引文规范（引用格式混用检测）
- 实验信息完整性（样本量、统计方法、controls描述）
- 行文语病（冠词、时态、主谓一致）

展示格式：
```
=== 第一部分：AI客观核查结果 ===

核查项目A
  位置: Section X.X, Page X
  问题: [客观陈述事实]
  证据: [引用原文]

...

请告诉我您认可纳入正式审稿的核查意见编号（如：1,2,3 或 all）
```

**第二部分：AI专业性参考观点（AI独立思考结论）**
针对以下专业领域，出具AI独立思考后的结论，仅供参考：
- 创新性评价
- 是否突破领域瓶颈
- 研究重要性
- 学术路线价值
- 数据深层真伪（需结合领域知识判断）
- 复杂理论机理的自洽性
- 期刊的专业性评判标准匹配度

展示格式：
```
=== 第二部分：AI专业性参考观点 ===

观点类别: [创新性评价]
观点: [AI独立思考后的结论]
置信度: [High/Medium/Low]
证据: [支撑观点的论文内容]
[AI reference comments, only for expert personal reference, not valid for official review]

...

请告诉我您认可纳入正式审稿的参考观点编号（如：1,2 或 all）
```

**纳入机制**:
- 两个部分的编号独立统计
- 用户确认纳入后，该条目进入正式审稿内容
- 未纳入的内容不进入最终报告

### State 6: REPORT_READY (报告生成)
生成最终审稿报告：
```
python scripts/report_generator.py --input reviews.json --metadata metadata.json --params params.json --journal <type> --ai-issues conflicts.json --ai-opinions opinions.json --output report.txt
```

## 审稿意见管理

### 数据结构
```json
{
  "comment_id": "C001",
  "severity": "Fatal/Major/Minor/Editorial",
  "category": "维度名称",
  "location": "Section X.X, Page X",
  "source": "Manual/AI",
  "type": "formal/reference/internal",
  "content": "审稿意见内容",
  "evidence": "证据引用",
  "ai_reference": false,
  "timestamp": "YYYY-MM-DD HH:MM:SS"
}
```

## 报告输出格式

### 第一段结构（综合评述）
本段包含以下要素，按顺序组合为一段完整段落：
1. 研究领域与论文标题
2. 研究工作概述与核心成果
3. 创新性与学术价值评价
4. 论文现存问题概述（客观陈述）
5. 明确终审结论（Accept/Minor Revision/Major Revision/Reject）

### 第二部分结构（详细意见）
- 逐条编号排列，无二级标题
- 每条包含：编号、严重性、类别、位置、内容
- 证据引用紧随内容之后
- AI核查问题与人工意见合并排列

### AI参考观点（单独标注）
【AI reference comments, only for expert personal reference, not valid for official review】

## 使用示例

### 完整审稿流程
```
用户: 上传 paper.pdf
AI: [State 1] 正在解析论文（仅封面信息，约1-2秒）...
AI: 解析完成，请核对以下元数据:
     标题: xxx
     作者: xxx
     期刊: xxx
     DOI: xxx
     摘要: xxx
     关键词: xxx
用户: 确认
AI: [State 2] 元数据已确认，进入审稿阶段
AI: [State 3] 请提供审稿意见，或发送【最终定稿】
用户: Section 2.1的实验设计存在问题
AI: 请提供完整审稿意见（severity/category/location/content/evidence）
用户: Severity: Major, Category: Methodology, Location: Section 2.1, Content: 样本量不足
AI: 已保存 [C001] Major - Methodology - Section 2.1
AI: 继续补充内容，或发送【最终定稿】
用户: 【最终定稿】
AI: [State 4] 请提供审稿参数
用户: 创新性Original, 学术影响High, 期刊Nature类
AI: [State 5] 正在执行AI客观审查...
AI: [展示审查结果]
     [1.] [Editorial] Figure & Table Format
       Issue: Figure引用格式不一致
     [2.] [Minor] Data Consistency
       Issue: 数字格式混用
     ...
AI: 请输入您认可纳入正式审稿的审查意见编号（如：1,2 或 all）
用户: 1
AI: 已采纳审查意见[1]，正式审稿意见共2条
AI: [State 6] 正在生成审稿报告...
AI: 报告生成完成

=== 审稿报告 ===
The manuscript entitled "xxx" addresses research in xxx. This study demonstrates that... 
The work represents an original contribution that significantly advances current understanding...
Based on the comprehensive evaluation, this reviewer recommends Minor Revision...

1. [Major] (Methodology) - Section 2.1
   样本量不足，未提供功效分析
   Evidence: 作者声明n=5 per group...
2. [Editorial] (Figure & Table Format) - Throughout
   Figure引用格式不一致（Fig./Figure混用）

[AI REFERENCE COMMENTS - 仅供专家参考]
1. [Novelty Assessment]
   Based on the abstract, this work appears to claim significant novelty.
   [AI reference comments, only for expert personal reference, not valid for official review]
```

## 资源索引

### 脚本
- [scripts/state_manager.py](scripts/state_manager.py): 状态机管理
- [scripts/pdf_parser.py](scripts/pdf_parser.py): PDF极速解析（延迟加载）
- [scripts/review_storage.py](scripts/review_storage.py): 审稿意见存储
- [scripts/conflict_detector.py](scripts/conflict_detector.py): AI硬核审查（逻辑/数据/格式核查）
- [scripts/report_generator.py](scripts/report_generator.py): 报告生成（统一SCI英文输出）

### 参考文档
- [references/review_checklist.md](references/review_checklist.md): 9维度审稿清单
- [references/report_template.md](references/report_template.md): 报告模板参考
- [references/journal_styles.md](references/journal_styles.md): 期刊风格指南

### 资产文件
- [assets/review_template.json](assets/review_template.json): 审稿意见JSON模板

## 注意事项

1. **延迟加载原则**: State 1只解析封面，方法和结论在State 5按需解析
2. **token消耗控制**: 不解析参考文献、章节结构列表
3. **严格状态顺序**: 必须按State 1→6顺序执行，禁止跳状态
4. **AI审查结果展示**: 完整展示审查结果，用户确认后才纳入正式意见
5. **AI参考观点标注**: 必须使用规定标注格式，不作为正式审稿依据
6. **输出语言**: 统一输出地道SCI学术英文，复用原文专业词汇
7. **格式要求**: 第一段综合评述 + 逐条编号详细意见，无二级标题
