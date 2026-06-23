#!/usr/bin/env python3
"""
探测钉钉AI表格 - 营运监控抽查管理
获取字段结构和样本数据
"""
import json
import requests
import time

DINGTALK_CLIENT_ID = "dinggm4kobbiopvvruq2"
DINGTALK_CLIENT_SECRET = "MEJt_n2jP3bKn30j9HF0nbL_XcFmx1zFTsIlEF6H1SHv_-DKtnytchuQmfzldZbR"
DINGTALK_API = "https://api.dingtalk.com"
DINGTALK_OAPI = "https://oapi.dingtalk.com"

BASE_ID = "P7QG4Yx2Jp602geAu4rELDgPW9dEq3XD"
SHEET_ID = "qa8gG1o"
OPERATOR_ID = "HFG333ePznAwB7gbeY5iS4wiEiE"

_token_cache = {"token": None, "expiry": 0}

def get_access_token():
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
        return None
    except Exception as e:
        print(f"获取token异常: {e}")
        return None

def get_sheet_fields():
    """获取数据表字段结构"""
    token = get_access_token()
    if not token:
        return None
    
    url = f"{DINGTALK_API}/v1.0/notable/bases/{BASE_ID}/sheets/{SHEET_ID}/fields"
    try:
        resp = requests.get(url, headers={
            "x-acs-dingtalk-access-token": token,
            "Content-Type": "application/json"
        }, params={"operatorId": OPERATOR_ID}, timeout=10)
        print(f"获取字段: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(json.dumps(data, ensure_ascii=False, indent=2))
            return data
        else:
            print(f"响应: {resp.text[:500]}")
    except Exception as e:
        print(f"异常: {e}")
    return None

def get_records(limit=5):
    """获取记录列表"""
    token = get_access_token()
    if not token:
        return None
    
    url = f"{DINGTALK_API}/v1.0/notable/bases/{BASE_ID}/sheets/{SHEET_ID}/records"
    try:
        resp = requests.get(url, headers={
            "x-acs-dingtalk-access-token": token,
            "Content-Type": "application/json"
        }, params={"operatorId": OPERATOR_ID, "maxResults": limit}, timeout=10)
        print(f"\n获取记录: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            # 简化输出
            records = data.get("records", [])
            print(f"共 {len(records)} 条记录")
            for i, r in enumerate(records[:3]):
                print(f"\n记录 {i+1}:")
                print(f"  ID: {r.get('id')}")
                fields = r.get("fields", {})
                for k, v in fields.items():
                    v_str = str(v)[:100]
                    print(f"  {k}: {v_str}")
            return data
        else:
            print(f"响应: {resp.text[:500]}")
    except Exception as e:
        print(f"异常: {e}")
    return None

def main():
    print("=" * 60)
    print("钉钉AI表格字段探测")
    print(f"Base ID: {BASE_ID}")
    print(f"Sheet ID: {SHEET_ID}")
    print("=" * 60)
    
    print("\n【1/2】获取字段结构...")
    get_sheet_fields()
    
    print("\n【2/2】获取样本记录...")
    get_records(limit=5)

if __name__ == "__main__":
    main()
