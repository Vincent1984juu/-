#!/usr/bin/env python3
"""
查看所有记录的月份分布
"""
import json
import requests
import time
from datetime import datetime

DINGTALK_CLIENT_ID = "dinggm4kobbiopvvruq2"
DINGTALK_CLIENT_SECRET = "MEJt_n2jP3bKn30j9HF0nbL_XcFmx1zFTsIlEF6H1SHv_-DKtnytchuQmfzldZbR"
DINGTALK_API = "https://api.dingtalk.com"

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

def get_all_records():
    token = get_access_token()
    if not token:
        return []
    
    all_records = []
    next_token = ""
    
    while True:
        url = f"{DINGTALK_API}/v1.0/notable/bases/{BASE_ID}/sheets/{SHEET_ID}/records"
        params = {"operatorId": OPERATOR_ID, "maxResults": 100}
        if next_token:
            params["nextToken"] = next_token
        
        try:
            resp = requests.get(url, headers={
                "x-acs-dingtalk-access-token": token,
                "Content-Type": "application/json"
            }, params=params, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                records = data.get("records", [])
                all_records.extend(records)
                if not data.get("hasMore", False):
                    break
                next_token = data.get("nextToken", "")
            else:
                break
        except Exception as e:
            print(f"异常: {e}")
            break
    
    return all_records

def main():
    records = get_all_records()
    print(f"共 {len(records)} 条记录\n")
    
    month_counts = {}
    store_counts = {}
    
    for r in records:
        fields = r.get("fields", {})
        date_ts = fields.get("抽检日期")
        
        if date_ts:
            dt = datetime.fromtimestamp(date_ts / 1000)
            month_str = dt.strftime("%Y-%m")
            month_counts[month_str] = month_counts.get(month_str, 0) + 1
            
            store_objs = fields.get("门店", [])
            store_name = store_objs[0].get("name", "未知") if store_objs else "未知"
            
            if month_str not in store_counts:
                store_counts[month_str] = {}
            store_counts[month_str][store_name] = store_counts[month_str].get(store_name, 0) + 1
        else:
            month_counts["无日期"] = month_counts.get("无日期", 0) + 1
    
    print("月份分布:")
    for m, c in sorted(month_counts.items()):
        print(f"  {m}: {c}条")
    
    print("\n各月门店分布（前5）:")
    for m, stores in sorted(store_counts.items()):
        print(f"\n{m}:")
        for s, c in sorted(stores.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  {s}: {c}次")

if __name__ == "__main__":
    main()
