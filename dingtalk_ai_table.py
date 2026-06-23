#!/usr/bin/env python3
"""
钉钉AI表格同步工具
同步营业额分析报告到钉钉AI表格
"""

import sys
import json
import requests
import time
import os
import re

# 导入门店映射（如果存在）
try:
    from dingtalk_store_map import get_store_dept_id
except ImportError:
    def get_store_dept_id(store_name):
        return None

# 钉钉配置
DINGTALK_CLIENT_ID = "dinggm4kobbiopvvruq2"
DINGTALK_CLIENT_SECRET = "MEJt_n2jP3bKn30j9HF0nbL_XcFmx1zFTsIlEF6H1SHv_-DKtnytchuQmfzldZbR"
DINGTALK_API = "https://api.dingtalk.com"
DINGTALK_OAPI = "https://oapi.dingtalk.com"

# 钉钉AI表格配置
BASE_ID = "Y1OQX0akWm6nkvZquvN2ABAjVGlDd3mE"
SHEET_ID = "hERWDMS"

# 操作人unionId（陈晓腾）
OPERATOR_ID = "HFG333ePznAwB7gbeY5iS4wiEiE"

# 区域ID映射（从表格已有数据提取）
REGION_MAP = {
    "孙红梅区": "kVrSqxosrE",
    "陈超平区": "dNFdDkNbm3",
}

# Token缓存
_token_cache = {
    "token": None,
    "expiry": 0
}

def format_report_for_dingtalk(report_content):
    """
    钉钉AI表格的 markdown 字段实际上当作纯文本处理，
    不解析 **加粗**、<br> 等格式，且会把连续空白压缩。
    
    策略：
    1. 去掉所有 markdown 加粗 **xxx**
    2. 保留 \n 换行（钉钉可能保留）
    3. 每行之间加空行（\n\n），增加分隔感
    4. 用 【】和 ● 作为视觉锚点
    """
    if not report_content:
        return report_content
    
    text = report_content.strip()
    
    # 1. 去掉 markdown 加粗 **xxx**
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    
    # 2. 清理多余空行
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # 3. 去掉行尾空白
    lines = text.split('\n')
    lines = [line.rstrip() for line in lines]
    text = '\n'.join(lines)
    
    return text


def get_access_token():
    """获取钉钉Access Token（带缓存）"""
    now = time.time()
    if _token_cache["token"] and _token_cache["expiry"] > now + 60:
        return _token_cache["token"]
    
    try:
        # 新版API获取token
        resp = requests.post(
            f"{DINGTALK_API}/v1.0/oauth2/accessToken",
            json={
                "appKey": DINGTALK_CLIENT_ID,
                "appSecret": DINGTALK_CLIENT_SECRET
            },
            timeout=10
        )
        data = resp.json()
        if "accessToken" in data:
            token = data["accessToken"]
            expire_in = data.get("expireIn", 7200)
            _token_cache["token"] = token
            _token_cache["expiry"] = now + expire_in
            return token
        
        # 旧版API获取token
        resp2 = requests.get(
            f"{DINGTALK_OAPI}/gettoken",
            params={
                "appkey": DINGTALK_CLIENT_ID,
                "appsecret": DINGTALK_CLIENT_SECRET
            },
            timeout=10
        )
        data2 = resp2.json()
        if data2.get("errcode") == 0 and data2.get("access_token"):
            token = data2["access_token"]
            expire_in = data2.get("expires_in", 7200)
            _token_cache["token"] = token
            _token_cache["expiry"] = now + expire_in
            return token
        
        print(f"获取token失败: {data}")
        return None
    except Exception as e:
        print(f"获取token异常: {e}")
        return None

def month_to_timestamp(month_str):
    """将月份字符串转换为时间戳（毫秒）"""
    from datetime import datetime
    try:
        dt = datetime.strptime(month_str, "%Y-%m-%d")
        return int(dt.timestamp() * 1000)
    except:
        try:
            dt = datetime.strptime(month_str, "%Y-%m")
            return int(dt.timestamp() * 1000)
        except:
            return None

def sync_report_to_dingtalk_ai_table(report_data):
    """同步报告到钉钉AI表格"""
    token = get_access_token()
    if not token:
        print("❌ 获取钉钉Access Token失败")
        return False
    
    store_name = report_data.get('store_name', '')
    region = report_data.get('region', '')
    month = report_data.get('month', '')
    report_content = report_data.get('report_content', '')
    
    # 格式化报告内容，使钉钉显示更友好
    formatted_report = format_report_for_dingtalk(report_content)
    
def sync_report_to_dingtalk_ai_table(report_data):
    """同步报告到钉钉AI表格"""
    token = get_access_token()
    if not token:
        print("❌ 获取钉钉Access Token失败")
        return False
    
    store_name = report_data.get('store_name', '')
    region = report_data.get('region', '')
    month = report_data.get('month', '')
    report_url = report_data.get('report_url', '')
    
    print(f"同步报告到钉钉AI表格:")
    print(f"  门店: {store_name}")
    print(f"  区域: {region}")
    print(f"  月份: {month}")
    print(f"  链接: {report_url}")
    
    # 钉钉AI表格超链接字段：需要 {"link": "URL"} 格式
    fields = {}
    if report_url:
        fields["报告原文"] = {
            "link": report_url,
            "text": f"{store_name} {month} 报告"
        }
    
    # 经营月份（时间戳）
    month_ts = month_to_timestamp(month)
    if month_ts:
        fields["经营月份"] = month_ts
    
    # 区域（字符串格式）
    region_id = REGION_MAP.get(region)
    if region_id:
        fields["区域"] = region
    else:
        fields["区域"] = region
    
    # 门店（普通文本格式，直接填写门店名称）
    fields["门店"] = store_name
    
    # 构造请求体
    payload = {
        "records": [
            {
                "fields": fields
            }
        ]
    }
    
    # 调用钉钉AI表格API创建记录
    try:
        api_url = f"{DINGTALK_API}/v1.0/notable/bases/{BASE_ID}/sheets/{SHEET_ID}/records?operatorId={OPERATOR_ID}"
        resp = requests.post(
            api_url,
            headers={
                "x-acs-dingtalk-access-token": token,
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=10
        )
        print(f"  API响应: {resp.status_code}")
        if resp.status_code in [200, 201]:
            result = resp.json()
            print(f"  ✅ 同步成功！")
            if result.get('value'):
                for r in result['value']:
                    print(f"     记录ID: {r.get('id')}")
            return True
        else:
            print(f"  ❌ 同步失败: {resp.text}")
            return False
    except Exception as e:
        print(f"  ❌ 同步异常: {e}")
        return False

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 dingtalk_ai_table.py sync '<json_data>'")
        sys.exit(1)
    
    action = sys.argv[1]
    if action == "sync":
        data = json.loads(sys.argv[2])
        success = sync_report_to_dingtalk_ai_table(data)
        sys.exit(0 if success else 1)
    else:
        print(f"Unknown action: {action}")
        sys.exit(1)

if __name__ == "__main__":
    main()
