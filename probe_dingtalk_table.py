#!/usr/bin/env python3
"""
探测钉钉AI表格/文档表格，获取数据
"""
import sys
import json
import requests
import time

# 钉钉配置（复用现有配置）
DINGTALK_CLIENT_ID = "dinggm4kobbiopvvruq2"
DINGTALK_CLIENT_SECRET = "MEJt_n2jP3bKn30j9HF0nbL_XcFmx1zFTsIlEF6H1SHv_-DKtnytchuQmfzldZbR"
DINGTALK_API = "https://api.dingtalk.com"
DINGTALK_OAPI = "https://oapi.dingtalk.com"

# 从链接中解析的参数
WORKBOOK_ID = "P7QG4Yx2Jp602geAu4rELDgPW9dEq3XD"  # 节点ID
SHEET_ID = "qa8gG1o"
VIEW_ID = "exy4mB3"

# 操作人unionId（陈晓腾）
OPERATOR_ID = "HFG333ePznAwB7gbeY5iS4wiEiE"

_token_cache = {"token": None, "expiry": 0}

def get_access_token():
    """获取钉钉Access Token"""
    now = time.time()
    if _token_cache["token"] and _token_cache["expiry"] > now + 60:
        return _token_cache["token"]
    
    try:
        resp = requests.post(
            f"{DINGTALK_API}/v1.0/oauth2/accessToken",
            json={"appKey": DINGTALK_CLIENT_ID, "appSecret": DINGTALK_CLIENT_SECRET},
            timeout=10
        )
        data = resp.json()
        if "accessToken" in data:
            token = data["accessToken"]
            expire_in = data.get("expireIn", 7200)
            _token_cache["token"] = token
            _token_cache["expiry"] = now + expire_in
            return token
        
        resp2 = requests.get(
            f"{DINGTALK_OAPI}/gettoken",
            params={"appkey": DINGTALK_CLIENT_ID, "appsecret": DINGTALK_CLIENT_SECRET},
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

def test_ai_table_api():
    """尝试用AI表格(Notable) API读取"""
    token = get_access_token()
    if not token:
        print("❌ 无法获取token")
        return False
    
    # 尝试列出数据表（把workbookId当baseId）
    print(f"\n=== 尝试AI表格API: baseId={WORKBOOK_ID}, sheetId={SHEET_ID} ===")
    
    # 1. 先获取所有数据表
    url1 = f"{DINGTALK_API}/v1.0/notable/bases/{WORKBOOK_ID}/sheets"
    try:
        resp = requests.get(url1, headers={
            "x-acs-dingtalk-access-token": token,
            "Content-Type": "application/json"
        }, params={"operatorId": OPERATOR_ID}, timeout=10)
        print(f"  获取数据表列表: {resp.status_code}")
        print(f"  响应: {resp.text[:500]}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"  ✅ 成功获取数据表列表: {data}")
    except Exception as e:
        print(f"  异常: {e}")
    
    # 2. 尝试获取记录
    url2 = f"{DINGTALK_API}/v1.0/notable/bases/{WORKBOOK_ID}/sheets/{SHEET_ID}/records"
    try:
        resp = requests.get(url2, headers={
            "x-acs-dingtalk-access-token": token,
            "Content-Type": "application/json"
        }, params={"operatorId": OPERATOR_ID, "maxResults": 10}, timeout=10)
        print(f"\n  获取记录: {resp.status_code}")
        print(f"  响应: {resp.text[:500]}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"  ✅ 成功获取记录: {json.dumps(data, ensure_ascii=False, indent=2)[:1000]}")
            return True
    except Exception as e:
        print(f"  异常: {e}")
    
    return False

def test_doc_api():
    """尝试用文档API读取"""
    token = get_access_token()
    if not token:
        return False
    
    print(f"\n=== 尝试文档API: nodeId={WORKBOOK_ID} ===")
    
    # 1. 获取节点信息
    # 需要先获取workspaceId，尝试通过知识库搜索
    # 或者用文档下载接口
    
    # 尝试文档内容获取
    # 钉钉文档API: /v1.0/documents/workspaces/{workspaceId}/nodes/{nodeId}
    # 但我们需要workspaceId
    
    # 尝试用旧版API获取文档信息
    url = f"{DINGTALK_OAPI}/topapi/doc/v3/get"
    try:
        resp = requests.post(url, headers={
            "x-acs-dingtalk-access-token": token,
            "Content-Type": "application/json"
        }, json={"docId": WORKBOOK_ID}, timeout=10)
        print(f"  文档获取: {resp.status_code}")
        print(f"  响应: {resp.text[:500]}")
    except Exception as e:
        print(f"  异常: {e}")
    
    # 尝试表格API（电子表格）
    # 获取单元格区域
    url2 = f"{DINGTALK_API}/v1.0/doc/workbooks/{WORKBOOK_ID}/sheets/{SHEET_ID}/cells"
    try:
        resp = requests.get(url2, headers={
            "x-acs-dingtalk-access-token": token,
            "Content-Type": "application/json"
        }, params={"operatorId": OPERATOR_ID, "rangeAddress": "A1:Z100"}, timeout=10)
        print(f"\n  电子表格单元格: {resp.status_code}")
        print(f"  响应: {resp.text[:500]}")
    except Exception as e:
        print(f"  异常: {e}")
    
    return False

def main():
    print("=" * 60)
    print("钉钉表格探测工具")
    print("=" * 60)
    print(f"Workbook/Node ID: {WORKBOOK_ID}")
    print(f"Sheet ID: {SHEET_ID}")
    print(f"View ID: {VIEW_ID}")
    print()
    
    # 先尝试AI表格
    ai_ok = test_ai_table_api()
    
    # 再尝试文档API
    doc_ok = test_doc_api()
    
    print("\n" + "=" * 60)
    print("探测结果:")
    print(f"  AI表格API: {'✅ 可用' if ai_ok else '❌ 不可用'}")
    print(f"  文档API: {'✅ 可用' if doc_ok else '❌ 不可用'}")
    print("=" * 60)

if __name__ == "__main__":
    main()
