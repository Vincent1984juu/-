---
name: holiday-plan-generator
description: |
  聚满分门店节假日业绩提升行动计划生成器。
  当用户（店长/同事）提到以下关键词时触发：母亲节计划、儿童节计划、520计划、情人节计划、圣诞节计划、父亲节计划、元旦计划，或任何"【节日名称】计划/作战计划/行动计划/业绩计划"的请求。
  通过5个填空问题收集门店信息，生成交互式HTML作战计划页面，店长填写后点击【生成完整作战计划】→【同步到钉钉表格】，复制链接粘贴给AI助教即可自动同步到钉钉AI表格。
---

# 节假日作战计划生成器

## 工作流程（5步）

### 步骤1：触发识别
用户说节日关键词时触发：母亲节计划、儿童节计划、520计划、情人节计划、圣诞节计划、父亲节计划、元旦计划等。

### 步骤2：发出指引（立即执行）
向用户发送2个填空问题。

发送时附带说明：
> 请回复门店和区域，我会为你生成交互式作战计划页面。其余信息（目标、产品、排班、活动内容等）在页面中填写即可。

**指引格式见：** `references/questions.md`

### 步骤3：收集回答 → 生成交互式HTML页面
用户回复门店和区域后，解析数据，生成交互式HTML文件。

**HTML模板：** `/root/.openclaw/workspace/skills/holiday-plan-generator/references/template-interactive.html`

**数据注入方式：**
```javascript
window.__HOLIDAY_DATA__ = {
    storeName: "南村店",
    region: "孙红梅区"
};
```

**生成命令：**
```bash
cd /root/.openclaw/workspace/gitee-pages-repo
TIMESTAMP=$(date +%Y%m%d%H%M)
FILENAME="{拼音}-{节日}-{区域}-{时间戳}.html"
node -e "
const fs = require('fs');
let html = fs.readFileSync('/root/.openclaw/workspace/skills/holiday-plan-generator/references/template-interactive.html', 'utf-8');
const data = {
    storeName: "{门店名}",
    region: "{区域}"
};
const injection = 'window.__HOLIDAY_DATA__ = ' + JSON.stringify(data) + ';';
html = html.replace(/window\.__HOLIDAY_DATA__\s*=\s*null;/, injection);
fs.writeFileSync('./' + '${FILENAME}', html);
console.log('✅ 生成: ' + '${FILENAME}');
"
git add "$FILENAME"
git commit -m "add: {门店} {节日} 作战计划"
git push -u github master --force
```

**文件名格式：** `{拼音}-{节日}-{区域}-{时间戳}.html`

### 步骤4：发送链接给店长

🎯 **{门店名} · {节日} 作战计划**

AI已完成基础框架，点击链接继续完善计划。

👉 **点击填写：**
https://vincent1984juu.github.io/-/{拼音}-{节日}-{区域}-{时间戳}.html

**操作指引：**

**提示1：**
打开链接后，点右上角**【…】**，选择浏览器打开。

**提示2：**
如遇页面显示错误或"等待数据"，请关闭后稍等30秒重新打开。

**提示3：**
填完后，点击【生成完整作战计划】，再点【📤 同步到钉钉表格】，把链接发给我即可。

---

### 步骤5：记录待同步链接

生成HTML后，将链接信息写入临时记录文件。

**记录文件：** `/root/.openclaw/workspace/memory/holiday-pending.json`

**写入命令：**
```bash
python3 -c "
import json, os, datetime

pending_file = '/root/.openclaw/workspace/memory/holiday-pending.json'
records = []
if os.path.exists(pending_file):
    with open(pending_file, 'r') as f:
        records = json.load(f)

records.append({
    'store_name': '{门店名}',
    'region': '{区域}',
    'holiday': '{节日}',
    'url': 'https://vincent1984juu.github.io/-/{拼音}-{节日}-{区域}-{时间戳}.html',
    'created_at': datetime.datetime.now().isoformat()
})

with open(pending_file, 'w') as f:
    json.dump(records, f, ensure_ascii=False, indent=2)

print('✅ 已记录待同步链接')
"
```

---

### 步骤6：店长填写并粘贴链接

店长点击链接后：
1. 查看预填充的基础信息（门店、目标、产品）
2. 填写/修改人员排班、活动内容、往年踩坑
3. 点击**【生成完整作战计划】**
4. 报告内容可点击直接修改
5. 同一次修改后再次点击【生成完整作战计划】，URL自动更新
6. 复制浏览器地址栏的完整链接（含 `#data=...`），可跨设备访问
7. 修改满意后，**点【📤 同步到钉钉表格】按钮复制链接，粘贴发送给【满分学院AI助教】**

> **数据保存机制：** 点击【生成完整作战计划】后，所有填写内容自动编码保存到URL的 `#data=` 参数中。复制完整链接到任何设备打开，都能看到最新保存的内容。

---

### 步骤7：自动同步到钉钉AI表格

**当店长粘贴了含 `#data=` 的完整报告链接时**，触发自动同步。

**执行流程：**
1. 检查店长消息中是否包含 `https://vincent1984juu.github.io` 链接
2. 如果包含，提取该链接作为 `report_url`
3. 解析URL中的 `#data=` 参数，获取门店名、节日、目标等信息
4. 同步数据到钉钉AI表格（字段：门店、区域、节日、计划制定日期、目标、报告原文）
5. 同步成功后，从 `holiday-pending.json` 中删除该条目

**同步脚本示例：**
```python
import json, base64, urllib.parse, requests, datetime

# 解析URL数据
url = '{店长粘贴的完整链接}'
hash_part = url.split('#data=')[1]
json_bytes = base64.b64decode(hash_part)
json_str = json_bytes.decode('utf-8')
data = json.loads(json_str)

# 节日ID映射（单选字段）
HOLIDAY_MAP = {
    '母亲节': 'tRyPU7H6Wl',
    '父亲节': '4ujjjpqBUG',
    '情人节': 'xpRZEEr66q',
    '520': 'OmDjAmuK2H',
    '儿童节': 'DagwoPOpUS',
    '圣诞节': '2i03zyixgG'
}

# 区域ID映射（单选字段）
REGION_MAP = {
    '孙红梅区': 'kVrSqxosrE',
    '陈桂莲区': 'SN7jULwlgs',
    '陈超平区': 'dNFdDkNbm3'
}

# 构建字段
fields = {
    '门店': data.get('storeName', ''),
    '区域': '{区域名}',  # 或传区域ID
    '节日': HOLIDAY_MAP.get(data.get('holidayName', ''), '其他'),
    '计划制定日期': int(datetime.datetime.now().timestamp() * 1000),  # 今天
    '目标': '¥' + str(data.get('targetAmount', '')),
    '报告原文': {'link': url, 'text': data.get('storeName', '') + ' ' + data.get('holidayName', '') + ' 作战计划'}
}

payload = {'records': [{'fields': fields}]}

# 调用API
api_url = f'https://api.dingtalk.com/v1.0/notable/bases/{BASE_ID}/sheets/{HOLIDAY_SHEET_ID}/records?operatorId={OPERATOR_ID}'
resp = requests.post(api_url, headers={'x-acs-dingtalk-access-token': token, 'Content-Type': 'application/json'}, json=payload, timeout=10)
```

**同步成功后，回复格式：**

```
✅ 同步成功！

**{门店名} · {节日} 作战计划**

● 门店：{门店名}
● 区域：{区域}
● 节日：{节日}
● 目标营业额：¥{目标金额}
● 去年营业额：¥{去年金额}
● 同比增长：{增长率}%
● 计划制定日期：{日期}

记录ID：{record_id}

表格地址：
https://alidocs.dingtalk.com/notable/XNkOM5jN7vj2YOY7?docKey=XNkOM5jN7vj2YOY7&entrance=data&sheetId=kggZCwE&viewId=j32Lj2G

请检查钉钉表格确认数据完整。🔥
```

> 注意：复盘字段（详细作战计划内容）因长度限制无法同步到钉钉表格，完整内容保存在报告链接中，点击"报告原文"可查看。

---

## 钉钉AI表格配置

- **高峰节假日计划表格：**
  - baseId: `Y1OQX0akWm6nkvZquvN2ABAjVGlDd3mE`
  - sheetId: `kggZCwE`（高峰节假日计划专用表）
  - 表格地址：https://alidocs.dingtalk.com/notable/XNkOM5jN7vj2YOY7?docKey=XNkOM5jN7vj2YOY7&entrance=data&sheetId=kggZCwE&viewId=j32Lj2G

- **营业额分析表格：**
  - baseId: `Y1OQX0akWm6nkvZquvN2ABAjVGlDd3mE`
  - sheetId: `hERWDMS`（营业额分析专用表）

> ⚠️ 重要：高峰节假日计划同步到 `kggZCwE`，不要和营业额分析表格 `hERWDMS` 混淆。

---

## 输出格式规则（钉钉适配）

- ❌ 禁止使用 markdown 表格（| 列1 | 列2 |）
- ❌ 禁止使用减号列表（- 项目）
- ✅ 使用 **加粗** 括关键信息
- ✅ 每段之间空一行
- ✅ 使用数字列表
- ✅ 用emoji分隔模块（🎯👥📦⚔️🚨📱✅）

## 参考文件

- 5题指引原文：见 references/questions.md
- 交互式HTML模板：见 references/template-interactive.html
