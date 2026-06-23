#!/usr/bin/env python3
"""
精炼汇总每个门店的5月抽检情况
"""
import json
import requests
import time
from datetime import datetime
import re
from collections import Counter

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

def analyze_store(texts):
    """分析一个门店的抽检文本，提炼关键词"""
    
    # 逐条分析
    has_shichi = 0      # 有试吃
    no_shichi = 0       # 无试吃
    morning_fast = 0    # 早高峰快
    morning_slow = 0    # 早高峰慢
    stock_enough = 0    # 货量足
    stock_short = 0     # 货量缺
    rec_active = 0      # 推荐积极
    rec_weak = 0        # 推荐弱
    greet_good = 0      # 招呼好
    greet_weak = 0      # 招呼弱
    
    for text in texts:
        t = text.lower()
        
        # 试吃
        if '有试吃' in t or '有摆盆试吃' in t or '有端盆试吃' in t:
            has_shichi += 1
        elif '无试吃' in t or '没有试吃' in t or '没有端盆试吃' in t:
            no_shichi += 1
        
        # 早高峰
        if '出货快' in t or '出货速度快' in t or '出货效率快' in t or '效率稳定' in t or '效率有进步' in t or '效率高' in t or '速度快' in t:
            morning_fast += 1
        elif '出货慢' in t or '出货速度一般' in t or '出货速度慢' in t or '出货效率慢' in t or '效率慢' in t or '效率偏低' in t or '效率一般' in t:
            morning_slow += 1
        
        # 货量
        if '货量充足' in t or '货源充足' in t or '包柜丰满' in t or '包柜饱满' in t or '货量足' in t:
            stock_enough += 1
        elif '货量不足' in t or '货量偏少' in t or '缺货' in t or '空缺' in t or '空柜' in t or '货量严重不足' in t:
            stock_short += 1
        
        # 推荐
        if '推荐积极' in t or '推包积极' in t or '推蛋糕积极' in t or '推荐还行' in t:
            rec_active += 1
        elif '推荐一般' in t or '推荐较弱' in t or '推荐较差' in t or '积极性一般' in t or '推包较差' in t or '推包一般' in t or '推荐较少' in t or '推包积极性一般' in t:
            rec_weak += 1
        
        # 招呼
        if '招呼声很热情' in t or '招呼声响亮' in t or '进店招呼声' in t and '不足' not in t and '差' not in t:
            greet_good += 1
        elif '招呼声不足' in t or '招呼声差' in t or '招呼声小' in t or '欢迎语声音小' in t or '进店招呼不足' in t:
            greet_weak += 1
    
    total = len(texts)
    
    # 组装特征（简化版，不显示次数）
    features = []
    
    if morning_fast > morning_slow and morning_fast > 0:
        features.append("✅早高峰快")
    elif morning_slow > morning_fast and morning_slow > 0:
        features.append("⚠️早高峰慢")
    else:
        if morning_fast > 0 or morning_slow > 0:
            features.append("➡️早高峰一般")
    
    if has_shichi > no_shichi and has_shichi > 0:
        features.append("✅试吃执行")
    elif no_shichi > has_shichi:
        features.append("⚠️缺试吃")
    else:
        if has_shichi > 0 or no_shichi > 0:
            features.append("➡️试吃一般")
    
    if stock_enough > stock_short and stock_enough > 0:
        features.append("✅货量足")
    elif stock_short > stock_enough and stock_short > 0:
        features.append("⚠️货量缺")
    else:
        if stock_enough > 0 or stock_short > 0:
            features.append("➡️货量一般")
    
    if rec_active > rec_weak and rec_active > 0:
        features.append("✅推荐积极")
    elif rec_weak > rec_active and rec_weak > 0:
        features.append("⚠️推荐弱")
    else:
        if rec_active > 0 or rec_weak > 0:
            features.append("➡️推荐一般")
    
    # 找主要问题（精炼）
    problems = []
    if morning_slow > morning_fast and morning_slow >= 3:
        problems.append("早高峰慢")
    if no_shichi > has_shichi and no_shichi >= 3:
        problems.append("缺试吃")
    if stock_short > stock_enough and stock_short >= 3:
        problems.append("货量不足")
    if rec_weak > rec_active and rec_weak >= 3:
        problems.append("推荐弱")
    if greet_weak >= 3:
        problems.append("招呼弱")
    
    if not problems:
        problems = ["合格"]
    
    return ' | '.join(features), '、'.join(problems[:2])

def main():
    records = get_all_records()
    
    store_map = {}
    
    for r in records:
        fields = r.get("fields", {})
        store_objs = fields.get("门店", [])
        store_name = store_objs[0].get("name", "未知") if store_objs else "未知"
        
        date_ts = fields.get("抽检日期")
        if not date_ts:
            continue
        dt = datetime.fromtimestamp(date_ts / 1000)
        if dt.strftime("%Y-%m") != "2026-05":
            continue
        
        summary_obj = fields.get("抽检总结", {})
        summary = summary_obj.get("markdown", "") if isinstance(summary_obj, dict) else str(summary_obj)
        
        manager_objs = fields.get("店长", [])
        manager = manager_objs[0].get("name", "") if manager_objs else ""
        
        if store_name not in store_map:
            store_map[store_name] = {
                "count": 0,
                "texts": [],
                "manager": manager
            }
        
        store_map[store_name]["count"] += 1
        store_map[store_name]["texts"].append(summary)
    
    # 输出精炼汇总
    print("=" * 70)
    print("5月营运监控抽查 · 门店精炼总结")
    print("=" * 70)
    
    for store_name, data in sorted(store_map.items(), key=lambda x: x[1]["count"], reverse=True):
        features, problems = analyze_store(data["texts"])
        print(f"\n【{store_name}】店长：{data['manager']} | {data['count']}次")
        print(f"  {features}")
        print(f"  核心问题：{problems}")
    
    print("\n" + "=" * 70)
    print(f"合计：{len(store_map)}家门店，{sum(d['count'] for d in store_map.values())}次抽查")
    print("=" * 70)

if __name__ == "__main__":
    main()
