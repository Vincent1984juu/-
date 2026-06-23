---
name: training-summary-notice
description: "Generate training summary notification documents (.docx) for 聚满分. Use when: (1) user asks to write a training summary notice/培训总结通知, (2) user needs to create a post-training summary document with participant list, module review, awards, and reminders, (3) user mentions 培训总结、培训通知、培训收官、培训回顾等关键词. Generates a formatted Word document following the standard 聚满分 training summary template with: title, participant table, training module table, team/individual awards, and mentor reminders."
---

# 培训总结通知生成器

根据培训信息自动生成聚满分标准格式的培训总结通知 Word 文档。

## 工作流程

### 1. 收集信息
向用户确认以下信息（如未提供）：
- **培训名称**：如"储备店长集中培训"
- **培训时间**：如"2026年4月22-23日"
- **参训人员**：姓名 + 门店（列表或表格形式）
- **培训模块**：模块名称 + 核心目标 + 重点内容
- **表彰信息**：精英团队名称、成员；优秀学员名单
- **落款部门**：如"赋能优化部"
- **落款日期**

### 2. 生成文档

使用 `scripts/generate_notice.py` 脚本生成 Word 文档：

```bash
python3 scripts/generate_notice.py --config <json_config_path> --output <output_path>
```

配置 JSON 格式：
```json
{
  "title": "2026年4月储备店长集中培训圆满收官",
  "greeting": "各位储备店长、带训师傅：",
  "overview": "2026年4月22-23日，为期两天的储备店长集中培训已圆满结束。本次培训共有8名储备店长参训，所有学员均顺利通过考核，恭喜大家！",
  "participants": [
    {"序号": "1", "姓名": "张三", "门店": "洛溪店"},
    {"序号": "2", "姓名": "李四", "门店": "平东店"}
  ],
  "modules": [
    {"模块": "店长角色认知", "核心目标": "明确店长职责", "重点内容": "6大角色、4大指标"},
    {"模块": "订货管理", "核心目标": "科学分析数据", "重点内容": "订货方法、工具、应用"}
  ],
  "team_award": {
    "team_name": "冲锋组",
    "members": ["张三（洛溪店）", "李四（平东店）"]
  },
  "individual_awards": ["张三（洛溪店）", "李四（平东店）"],
  "reminders_to_trainees": "课堂上学到的是知识，要转化为技能必须回到门店，在师傅的带训下实践。",
  "reminders_to_mentors": "请按照线上学习地图的指引，帮助徒弟完成相应的学习、考核与作业。",
  "closing": "期待各位储备店长顺利完成全部学习，通过最终考核，早日独当一面！",
  "contact": "如有任何问题或疑问，随时联系赋能优化部 陈晓腾。",
  "department": "赋能优化部",
  "date": "2026年4月24日"
}
```

### 3. 输出文件

生成 `.docx` 文件，命名建议：`{培训名称}_总结通知.docx`

## 文档格式规范

标准培训总结通知包含以下结构：

1. **标题**：居中，大号加粗字体
2. **称呼**：如"各位储备店长、带训师傅："
3. **培训概述**：时间、人数、结果
4. **一、参训人员**：表格（序号 | 姓名 | 门店）
5. **二、培训回顾**：表格（模块 | 核心目标 | 重点内容）
6. **三、表彰**：
   - 精英团队：团队名 + 成员列表
   - 优秀学员：名单
7. **四、重要叮嘱**：
   - 致学员：回店后完成线上学习、考核、实操
   - 致带训师傅：带训质量决定徒弟能否胜任
8. **结尾祝福**
9. **联系方式**
10. **落款**：部门 + 日期

## 自定义选项

如果用户提供的格式与标准模板不同，根据用户要求调整：
- 增减章节（如没有表彰环节则跳过）
- 修改表格列数或列名
- 调整文案风格（正式/活泼）
- 添加或删除特定段落
