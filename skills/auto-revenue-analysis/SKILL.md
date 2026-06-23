---
name: auto-revenue-analysis
description: |
  营业额自动分析工具。店长发送营业额数据后,自动生成预填充HTML分析页面。
  第一部分:AI自动分析数据(表格+核心差距)
  第二部分:店长填写根源分析、行动计划、下月目标
  触发词:"营业额分析"、"月度复盘"、"营业额复盘"、"做营业额分析"、"自动分析营业额"、"营业额自动分析"、"AI分析营业额"、"智能分析营业额"
---

**!RECHECK: 每次触发前必须重新读取本文件**

# 营业额自动分析工具

## 核心流程（六步法）

```
店长说"营业额分析" → 我发指引 → 店长给数据 → 我生成HTML → 店长填写 → 回复"已完成" → 我同步到钉钉AI表格
```

**关键原则：**
- 每次营业额分析 = 生成一份新的HTML（新URL，带时间戳）
- 同一次分析过程中修改 = URL自动更新（`#data=`参数保存最新数据）
- 跨设备访问 = 复制完整链接（含`#data=`）到任何设备都能打开
- 店长只需回复"已完成"，无需手动复制报告内容

---

## 第一步：触发技能

当店长说以下任一词时触发：
- 营业额分析
- 月度复盘
- 营业额复盘
- 做营业额分析
- 自动分析营业额
- 营业额自动分析
- AI分析营业额
- 智能分析营业额

**回复指引（纯文本，不要markdown引用块）：**

📊 月度营业额分析请提供以下数据：

**【基础信息】**

● 门店：

● 月份：

● 区域：（孙红梅区 / 陈桂莲区 / 陈超平区）

**【核心数据】**

● 营业额

● 来客数

● 客单价

● 充值金额

● 品类营业额和占比

**【提交方式】**

● 截图 / 拍照 / 文字 / 文件 均可

⚠️ 注意：数据必须有对比基准（目标/同比/环比至少其一），否则无法分析差距。

---

## 第二步：接收数据并生成HTML

店长发送数据后，解析数据，生成预填充HTML文件。

**数据解析规则：**

| 字段 | 解析方式 | 示例 |
|------|----------|------|
| 门店名称 | 提取"门店"后内容 | 万民城店 |
| 区域 | 提取"区域"后内容 | 孙红梅区 |
| 月份 | 提取"月份"后内容 | 2026-05 |
| 营业额-实际 | 提取"营业额"后的第一个数字 | 470148 |
| 营业额-目标 | 括号内"目标"后数字 | 500000 |
| 营业额-上月 | 括号内"上月"后数字 | 450000 |
| 营业额-去年 | 括号内"去年/同期"后数字 | 420000 |
| 来客数-实际 | 提取"来客数"后第一个数字 | 18421 |
| 客单价-实际 | 提取"客单价"后第一个数字 | 25.52 |
| 品类 | "品类"后按名称+金额解析 | 现烤131342 |

**生成HTML文件：**

基于模板文件：`/root/.openclaw/workspace/skills/auto-revenue-analysis/template.html`

复制模板，将 `window.__AI_DATA__ = null` 替换为解析后的JSON数据。

**文件名格式：** `{拼音}-{年月}-{时间戳}.html`

**示例注入数据：**
```javascript
window.__AI_DATA__ = {
    "storeName": "万民城店",
    "region": "孙红梅区",
    "month": "2026-05",
    "targetSales": 500000,
    "actualSales": 470148,
    "lastMonthSales": 450000,
    "lastYearSales": 420000,
    "targetCustomers": 20000,
    "actualCustomers": 18421,
    "lastMonthCustomers": 18000,
    "actualAvgPrice": 25.52,
    "targetAvgPrice": 26,
    "lastMonthAvgPrice": 25,
    "categories": [
        {"name": "现烤", "actual": 131342, "target": 0, "lastMonth": 0},
        {"name": "包装", "actual": 85076, "target": 0, "lastMonth": 0},
        {"name": "热酥", "actual": 33763, "target": 0, "lastMonth": 0},
        {"name": "蛋糕", "actual": 86758, "target": 0, "lastMonth": 0},
        {"name": "甜品", "actual": 86059, "target": 0, "lastMonth": 0}
    ]
};
```

**生成并推送：**
```bash
cd /root/.openclaw/workspace/gitee-pages-repo
TIMESTAMP=$(date +%Y%m%d%H%M)
FILENAME="{拼音}-{年月}-${TIMESTAMP}.html"
node -e "
const fs = require('fs');
let html = fs.readFileSync('/root/.openclaw/workspace/skills/auto-revenue-analysis/template.html', 'utf-8');
const data = { /* 解析后的数据 */ };
const injection = 'window.__AI_DATA__ = ' + JSON.stringify(data) + ';';
html = html.replace(/window\.__AI_DATA__\s*=\s*null;/, injection);
fs.writeFileSync('./' + '${FILENAME}', html);
console.log('✅ 生成: ' + '${FILENAME}');
"
git add "$FILENAME"
git commit -m "add: {门店名} {年月} 营业额分析"
git push -u github master --force
```

> **关键：每次生成都是新文件（带时间戳），不会覆盖旧文件**

---

## 第三步：发送链接给店长

📊 **{门店名} · {月份} 营业额分析**

**第一步：数据已分析，点击链接继续完成报告。**

点击链接：👉 https://vincent1984juu.github.io/-/{拼音}-{年月}-{时间戳}.html

**提示1：**

打开链接后，点右上角**【…】**，选择浏览器打开。

**提示2：**

如遇页面显示错误或"等待数据"，请关闭后稍等30秒重新打开。

---

## 第四步：记录待同步链接

生成HTML后，将链接信息写入临时记录文件。

**记录文件：** `/root/.openclaw/workspace/memory/revenue-pending.json`

**写入命令：**
```bash
python3 -c "
import json, os, datetime

pending_file = '/root/.openclaw/workspace/memory/revenue-pending.json'
records = []
if os.path.exists(pending_file):
    with open(pending_file, 'r') as f:
        records = json.load(f)

records.append({
    'store_name': '{门店名}',
    'region': '{区域}',
    'month': '{月份}',
    'url': 'https://vincent1984juu.github.io/-/{拼音}-{年月}-{时间戳}.html',
    'created_at': datetime.datetime.now().isoformat()
})

with open(pending_file, 'w') as f:
    json.dump(records, f, ensure_ascii=False, indent=2)

print('✅ 已记录待同步链接')
"
```

---

## 第五步：店长填写并粘贴链接

店长点击链接后：
1. 查看第一部分AI分析结果
2. 选择诊断类型、勾选根源、添加行动计划、设定目标
3. 点击**【生成完整分析报告】**
4. **报告内容可点击直接修改**
5. **同一次分析，修改后再次点击【生成完整分析报告】，URL会自动更新**
6. 复制浏览器地址栏的完整链接（含 `#data=...`），可跨设备访问
7. 修改满意后，**点【📤 同步到钉钉表格】按钮复制链接，粘贴发送给【满分学院AI助教】**

> **数据保存机制：** 点击「生成完整分析报告」后，所有填写内容自动编码保存到URL的 `#data=` 参数中。复制完整链接到任何设备打开，都能看到最新保存的内容。

---

## 第六步：自动同步到钉钉AI表格

当店长**粘贴了含 `#data=` 的完整报告链接**时，触发自动同步。

**重要：优先使用店长粘贴的链接（含 `#data=`），而非待同步记录。**

**执行流程：**
1. 检查店长消息中是否包含 `https://vincent1984juu.github.io` 链接
2. 如果包含，提取该链接作为 `report_url`
3. 如果不包含，读取 `memory/revenue-pending.json`，取最近记录作为 `report_url`
4. 调用 `sync_report_to_dingtalk_ai_table` 同步链接
5. 同步成功后，从记录中删除该条目

**执行命令：**
```bash
cd /root/.openclaw/workspace
python3 -c "
import json, os, re
from dingtalk_ai_table import sync_report_to_dingtalk_ai_table

# 从消息中提取URL（如果有）
message = '{店长消息内容}'
url_match = re.search(r'https://vincent1984juu\.github\.io/[^\\s\"\\'>]+', message)
pasted_url = url_match.group(0) if url_match else None

if pasted_url:
    report_url = pasted_url
    print('✅ 使用店长粘贴的链接:', report_url)
else:
    pending_file = 'memory/revenue-pending.json'
    if not os.path.exists(pending_file):
        print('❌ 没有待同步的记录')
        exit(1)
    with open(pending_file, 'r') as f:
        records = json.load(f)
    if not records:
        print('❌ 没有待同步的记录')
        exit(1)
    record = records[-1]
    report_url = record['url']
    print('✅ 使用待同步记录:', report_url)

report_data = {
    'store_name': '{门店名}',
    'region': '{区域}',
    'month': '{月份}',
    'report_url': report_url
}

result = sync_report_to_dingtalk_ai_table(report_data)
if result:
    if not pasted_url:
        records = [r for r in records if r['url'] != report_url]
        with open(pending_file, 'w') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
    print('✅ 已同步到钉钉AI表格')
else:
    print('❌ 同步失败')
"
```

**同步成功后会回复店长：**

✅ 报告已同步到钉钉AI表格
表格地址：https://alidocs.dingtalk.com/notable/XNkOM5jN7vj2YOY7?docKey=XNkOM5jN7vj2YOY7&entrance=data&newPanel=true&sheetId=hERWDMS&viewId=uSXGFwW

点击表格中"报告原文"列的链接即可查看完整报告

---

## 部署方式（方案B：独立文件）

**选择方案B**：每个门店独立HTML文件，拼音命名。

### 当前门店文件列表

| 门店 | 文件名 | 链接 |
|------|--------|------|
| 小北店 | `xiaobei-202605-202506211030.html` | https://vincent1984juu.github.io/-/xiaobei-202605-202506211030.html |

> 新增门店时，更新上表并追加到下方「批量重新生成」脚本中。
> **每个链接带唯一时间戳，彻底避免缓存问题**

### 命名规则

- 中文门店名 → 拼音（小写，无空格）
- 示例：万民城店 → `wanmincheng`，龙江店 → `longjiang`
- 格式：`{拼音}-{年月}-{时间戳}.html`
- 示例：`xiaobei-202605-202506211030.html`
- **时间戳 = 生成时的年月日时分，确保每次生成都是全新文件，彻底避免缓存问题**

### 批量重新生成（模板更新后）

当模板有优化时，执行以下脚本重新生成所有门店：

```bash
cd /root/.openclaw/workspace/gitee-pages-repo

# 定义门店数据数组（新增门店时追加）
declare -A stores
declare -A storeData

# 小北店 2026-05
stores["xiaobei-202605"]="小北店"
storeData["xiaobei-202605"]='{"storeName":"小北店","region":"孙红梅区","month":"2026-05","actualSales":470148,"targetSales":500000,"lastMonthSales":450000,"lastYearSales":420000,"actualCustomers":18421,"targetCustomers":20000,"lastMonthCustomers":18000,"actualAvgPrice":25.52,"targetAvgPrice":26,"lastMonthAvgPrice":25,"categories":[{"name":"现烤","actual":131342,"target":0,"lastMonth":0},{"name":"包装","actual":85076,"target":0,"lastMonth":0},{"name":"热酥","actual":33763,"target":0,"lastMonth":0},{"name":"蛋糕","actual":86758,"target":0,"lastMonth":0},{"name":"甜品","actual":86059,"target":0,"lastMonth":0}]}'

# 模板文件
TEMPLATE="/root/.openclaw/workspace/skills/auto-revenue-analysis/template.html"

# 重新生成所有门店
for key in "${!stores[@]}"; do
    echo "生成: ${stores[$key]} -> $key.html"
    cp "$TEMPLATE" "./$key.html"
    node -e "
const fs = require('fs');
let html = fs.readFileSync('./$key.html', 'utf-8');
const data = ${storeData[$key]};
const injection = 'window.__AI_DATA__ = ' + JSON.stringify(data) + ';';
html = html.replace(/window\.__AI_DATA__\s*=\s*null;/, injection);
fs.writeFileSync('./$key.html', html);
"
    git add "$key.html"
done

git commit -m "batch: 重新生成所有门店(模板更新)"
git push -u github master --force

echo "✅ 所有门店已重新生成并推送"
```

> 新增门店时，在上方的 `stores` 和 `storeData` 中追加对应条目即可。

### 缓存问题

GitHub Pages 有 **1-3分钟** 缓存，推送后需要稍等刷新。建议加 `?v=随机数` 参数强制刷新：
```
https://vincent1984juu.github.io/-/xiaobei-202605.html?v=2
```

---

## 模板文件位置

- **主模板：** `/root/.openclaw/workspace/skills/auto-revenue-analysis/template.html`
- **示例文件：** `/root/.openclaw/workspace/营业额分析-万民城店-202605.html`

## HTML工具功能说明

### 第一部分：AI自动分析（只读展示）

店长无需填写，数据已预填充：

| 展示项 | 说明 |
|--------|------|
| 基础信息 | 门店、区域、月份 |
| 核心指标 | 达成率、环比、同比、差额（红绿标注） |
| 品类结构 | 各品类金额、占比、达成率（表格） |
| 核心差距 | 黄色提示框，AI自动判断问题类型 |
| 引导行动 | 提示店长开始分析根源 |

### 第二部分：店长填写（交互式）

| 模块 | 交互方式 |
|------|----------|
| 根源分析 | 多选框点击（可多选）、可编辑文字、可新增 |
| 行动计划 | 动态添加/删除，每行5个字段 |
| 下月目标 | 4个默认输入框 + 可添加自定义目标 |

### 报告生成

点击「生成完整分析报告」后：
- 整合AI分析数据 + 店长填写内容
- 数据表格100%复用第一部分样式
- 核心差距引用第一部分AI生成的文字
- **报告内容可直接点击编辑（虚线边框区域）**
- 编辑后点击"🔄 更新报告内容"保存
- 操作按钮（复制/打印/截图）在报告下方
- 支持html2canvas一键截图保存
- **无需复制报告内容，回复"已完成"即可同步**

---

## 数据格式规范

### 店长输入格式（灵活解析）

支持以下格式（自动识别）：

```
// 完整格式
门店:万民城店
区域:孙红梅区
月份:2026-05
营业额:470148(目标500000,上月450000,去年同期420000)
来客数:18421(目标20000,上月18000)
客单价:25.52(目标26,上月25)
品类:现烤131342,包装85076,热酥33763,蛋糕86758,甜品86059

// 简化格式（也支持）
万民城店,孙红梅区,5月
营业额470148,目标50万
来客数18421,客单价25.52
```

### 解析容错规则

- 缺失目标/上月/去年数据 → 填0
- 缺失品类数据 → categories数组留空
- 缺失区域 → 显示"______"
- 数字识别错误 → 尝试用正则二次提取

---

## 技能目录结构

```
skills/auto-revenue-analysis/
├── SKILL.md              # 本文件
├── template.html         # HTML模板
└── example/              # 示例文件
    └── 营业额分析-万民城店-202605.html
```

## 注意事项

1. **每次分析都是新文件**：不同月份、不同门店的分析生成独立HTML，不会互相覆盖
2. **同一次分析可修改**：店长填写过程中可多次修改，每次点击「生成完整分析报告」URL自动更新
3. **跨设备访问**：复制完整链接（含`#data=`）到任何设备都能打开最新内容
4. **模板更新后需重新生成**：我优化模板后，会批量重新生成所有门店文件
5. **缓存问题**：GitHub Pages有缓存，推送后可能需要 **1-3分钟** 才能看到最新内容，建议加 `?v=2` 强制刷新
6. **钉钉兼容性**：如果钉钉内置浏览器显示异常，建议用系统浏览器(Chrome/Safari)打开
7. **Token安全**：Token已配置，不要泄露给其他人
8. **无需复制内容**：店长只需回复"已完成"，AI自动同步链接到表格
9. **中文文件名不支持**：GitHub Pages 404，必须用拼音命名

## 与其他技能的区别

| 技能 | 方式 | 适用场景 |
|------|------|----------|
| **monthly-revenue-analysis** | 对话式引导，一步步问 | 新店店长、需要辅导的情况 |
| **auto-revenue-analysis** | 自动解析数据，生成HTML链接 | 老店店长、数据齐全、追求效率 |
