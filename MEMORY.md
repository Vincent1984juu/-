# MEMORY.md - 核心记忆档案

## 用户
**晓腾**（My lord）
- 聚满分连锁烘焙企业，培训经理兼营运经理
- 中山市，工作时间9:00-21:00
- 爱好：吉他、足球
- 搭建公司培训系统是当前核心任务

## 关系时间线
- **2026-03-12**：首次上线，身份为"毒舌冰原狼"，称呼晓腾为My lord
- **2026-05-28**：Gateway故障后，重新设定为"小满"（当前身份）
- **2026-06-01**：系统故障，重新启动新实例，从备份文件恢复记忆

## 核心工作

### 1. 钉钉培训群管理
- 群：营运经理赋能3期·02阶段(储备后厨主管)等培训管理群
- 晓腾角色：培训经理/营运经理，高标准、强执行、重细节、追结果
- 我的角色：协助点评学员作业、发通知、催交、整理资料
- **点评风格**：严中有温，先肯定再提要求，强调实操和闭环，@师傅跟进
- **禁止**：未经晓腾确认，不以晓腾名义在群里发言

### 2. 营业额分析（HTML工具）
- 技能：`skills/auto-revenue-analysis/SKILL.md`
- 触发词：营业额分析、月度复盘、营业额复盘、自动分析营业额、AI分析营业额、智能分析营业额
- 方式：店长提供数据，自动生成预填充HTML分析页面，店长自行填写根源和行动计划，截图发回
- 对接钉钉AI表格：baseId Y1OQX0akWm6nkvZquvN2ABAjVGlDd3mE，sheetId hERWDMS
- 分析维度：数据总览、品类分析、问题/机会点、行动计划
- 钉钉格式：禁止markdown表格、禁止减号列表、每段空一行、用【】括关键信息
- 原对话式教练流程已归档到知识库：`knowledge-base/营业额分析教练式引导流程.md`

### 3. 损益分析技能
- 异常指标识别清单：收入类、成本类、费用类、利润类
- 动态组合2-3个问题，**不能**因为有预设组合就忽略其他异常指标
- 人工成本是常见异常点（如蓝天金地店1月薪资超预算20.4%）

### 4. 报销单整理技能
- 接收多张报销凭证截图，OCR识别，按7个一级类型+二级关键词分类
- 特殊规则：导航截图无金额→里程×1元/km；过桥费识别"广东联合电子服务"；停车费识别"P"字样
- 按一级类型分组，每组一份Word，非差旅类起点终点留空
- 二级分类小计，费用说明没内容就留空
- 文件位置：`skills/reimbursement-organizer/SKILL.md`

### 5. 知识库
- **本地知识库**：
  - 新增【聚满分知识库】文件夹，包含28个文件（PPT 11个、Excel 10个、PDF 6个、DOCX 1个）
  - 已整理完整索引：knowledge-base/聚满分知识库/INDEX.md
  - 核心内容覆盖：店长/领班角色认知、值班管理（值班前/中/后）、工作流程、检查表与评估表、训练四步骤、班前会、利润管理、人效管理、生产计划、开业流程、挑战日作战、周周PK策略
  - 待补充文件：7个（如何处理客诉、认识毛利、认识损益报表、如何分析损益报表、提升业绩的方法和思路、如何激励团队、值班管理的职责）
  - 原知识库：60个文件，58个已转Markdown（knowledge-base/markdown/）
- **钉钉知识库**：Wiki工作空间列表、节点列表、搜索接口已测试通过。用户staffId: 16927521153891793，unionId: HFG333ePznAwB7gbeY5iS4wiEiE
- 已获取20个知识库，包括：门店营运管理、门店基础岗位、赋能优化部、产品SOP、经营分析、总经办、人事行政、供应链、资材部、产品研发、外卖运营、财务部、工程部、AI应用、市场部、品控、烘焙工艺、现烤生产计划等
- 待处理：Storage.DownloadInfo.Read 权限（获取文件下载URL）
- 已加入openclaw.json extraPaths，memory_search可检索

## 重要技术修改
- **钉钉connector图片识别**：修改了plugin.ts，提取picture/richText消息的downloadCode，两步下载图片到/tmp/dingtalk_xxx.jpg，用markdown图片语法传给LLM
- **钉钉消息格式**：cleanMarkdownForDingTalk函数，AI Card/普通消息发送前自动清理Markdown
- **streamFromGateway SSE修复**：处理reader.done时buffer中剩余数据，解决"✅ 媒体已发送"和空消息问题

## 待处理事项
- 钉钉知识库API权限申请（Wiki.Workspace.Read等）——主人说"等一下再处理"
- 蓝天金地店deptId需补充映射（营业额分析表格）
- 钉钉DING消息接入：无API，需选择替代方案（加群监听或手动转发）

## 关键文件路径
- 营业额分析技能：`skills/auto-revenue-analysis/SKILL.md`
- 损益分析技能：`skills/monthly-profit-loss-analysis/SKILL.md`
- 报销单技能：`skills/reimbursement-organizer/SKILL.md`
- 钉钉AI表格脚本：`dingtalk_ai_table.py`
- 钉钉connector：`/root/.openclaw/extensions/dingtalk-connector/plugin.ts`

## 记忆归档
- 每日日志：memory/2026-03-12.md ~ memory/2026-06-01.md（共17份）
- 从备份恢复时间：2026-06-01 22:02
