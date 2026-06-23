#!/usr/bin/env python3
"""
读取5月抽检数据，按门店汇总
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
    """分页获取所有记录"""
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
                print(f"获取记录失败: {resp.status_code} {resp.text[:200]}")
                break
        except Exception as e:
            print(f"异常: {e}")
            break
    
    return all_records

def ts_to_date(ts_ms):
    """时间戳转日期"""
    if not ts_ms:
        return None, None
    try:
        dt = datetime.fromtimestamp(ts_ms / 1000)
        return dt.strftime("%Y-%m-%d"), dt.strftime("%Y-%m")
    except:
        return None, None

def main():
    print("获取所有记录...")
    records = get_all_records()
    print(f"共获取 {len(records)} 条记录\n")
    
    # 按门店汇总
    store_map = {}
    
    for r in records:
        fields = r.get("fields", {})
        
        # 门店
        store_objs = fields.get("门店", [])
        store_name = store_objs[0].get("name", "未知门店") if store_objs else "未知门店"
        
        # 日期
        date_ts = fields.get("抽检日期")
        date_str, month_str = ts_to_date(date_ts)
        
        # 抽检人
        inspector_objs = fields.get("抽检人", [])
        inspector = inspector_objs[0].get("name", "") if inspector_objs else ""
        
        # 抽检总结
        summary_obj = fields.get("抽检总结", {})
        summary = summary_obj.get("markdown", "") if isinstance(summary_obj, dict) else str(summary_obj)
        
        # 整改状态
        status = fields.get("整改是否完成", "").__str__()
        
        # 整改结果
        result_obj = fields.get("整改结果", {})
        result = result_obj.get("markdown", "") if isinstance(result_obj, dict) else str(result_obj)
        
        # 店长
        manager_objs = fields.get("店长", [])
        manager = manager_objs[0].get("name", "") if manager_objs else ""
        
        # 筛选5月
        if month_str != "2026-05":
            continue
        
        if store_name not in store_map:
            store_map[store_name] = {
                "count": 0,
                "dates": [],
                "inspectors": set(),
                "manager": manager,
                "summaries": [],
                "results": [],
                "statuses": []
            }
        
        store_map[store_name]["count"] += 1
        store_map[store_name]["dates"].append(date_str)
        if inspector:
            store_map[store_name]["inspectors"].add(inspector)
        if summary:
            store_map[store_name]["summaries"].append(summary.strip())
        if result:
            store_map[store_name]["results"].append(result.strip())
        if status:
            store_map[store_name]["statuses"].append(status)
    
    # 输出汇总
    print("=" * 60)
    print(f"5月抽检汇总（共 {sum(s['count'] for s in store_map.values())} 次）")
    print("=" * 60)
    
    for store_name, data in sorted(store_map.items(), key=lambda x: x[1]["count"], reverse=True):
        print(f"\n【{store_name}】")
        print(f"  抽检次数: {data['count']}次")
        print(f"  抽检日期: {', '.join(data['dates'])}")
        print(f"  抽检人: {', '.join(data['inspectors'])}")
        print(f"  店长: {data['manager']}")
        
        # 整改状态统计
        if data['statuses']:
            status_counts = {}
            for s in data['statuses']:
                status_counts[s] = status_counts.get(s, 0) + 1
            print(f"  整改状态: {status_counts}")
        
        print(f"  抽检总结:")
        for s in data['summaries']:
            # 每行缩进
            for line in s.split('\n'):
                line = line.strip()
                if line:
                    print(f"    - {line}")
        
        if data['results']:
            print(f"  整改结果:")
            for r in data['results']:
                for line in r.split('\n'):
                    line = line.strip()
                    if line:
                        print(f"    - {line}")
    
    # 保存JSON
    output = {}
    for store_name, data in store_map.items():
        output[store_name] = {
            "count": data["count"],
            "dates": data["dates"],
            "inspectors": list(data["inspectors"]),
            "manager": data["manager"],
            "summaries": data["summaries"],
            "results": data["results"],
            "statuses": data["statuses"]
        }
    
    with open("/root/.openclaw/workspace/may_inspection_summary.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 汇总已保存到 may_inspection_summary.json")

if __name__ == "__main__":
    main()
