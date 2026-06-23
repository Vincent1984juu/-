# 营业额AI分析工具 - 使用流程

## 工具文件
- `营业额AI预填充分析工具.html` — 主模板（空白，等待数据注入）

## 使用流程

### 第一步：店长发送数据
店长在KIMI中发送营业额数据，格式示例：

```
门店：万民城店
区域：孙红梅区
月份：2026-05

月营业额：470148元（目标500000，上月450000，去年同期420000）
来客数：18421人（目标20000，上月18000）
客单价：25.52元（目标26，上月25）

品类：
- 现烤面包：131342（目标140000，上月125000）
- 包装产品：85076（目标90000，上月82000）
- 热酥：33763（目标35000，上月32000）
- 蛋糕：86758（目标90000，上月85000）
- 甜品：86059（目标90000，上月80000）
```

### 第二步：AI生成预填充HTML
AI解析数据，生成注入脚本，生成完整HTML文件。

### 第三步：店长打开链接
店长打开HTML文件，第一部分已显示AI分析结果（图表+计算），只需填写第二部分：
- 选择问题诊断类型
- 勾选根源
- 填写行动计划
- 设定下月目标

### 第四步：生成报告
点击"生成完整分析报告"，得到最终报告，可截图/打印/复制。

---

## 数据注入格式（JSON）

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
    "lastYearCustomers": 0,
    "targetAvgPrice": 26,
    "actualAvgPrice": 25.52,
    "lastMonthAvgPrice": 25,
    "lastYearAvgPrice": 0,
    "categories": [
        {"name": "现烤面包", "actual": 131342, "target": 140000, "lastMonth": 125000},
        {"name": "包装产品", "actual": 85076, "target": 90000, "lastMonth": 82000},
        {"name": "热酥", "actual": 33763, "target": 35000, "lastMonth": 32000},
        {"name": "蛋糕", "actual": 86758, "target": 90000, "lastMonth": 85000},
        {"name": "甜品", "actual": 86059, "target": 90000, "lastMonth": 80000}
    ]
};
```
