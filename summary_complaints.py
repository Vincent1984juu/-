#!/usr/bin/env python3
"""
5月+6月孙红梅区差评汇总
"""
import json
import requests
import time
from datetime import datetime

CID='dinggm4kobbiopvvruq2'
CS='MEJt_n2jP3bKn30j9HF0nbL_XcFmx1zFTsIlEF6H1SHv_-DKtnytchuQmfzldZbR'
API='https://api.dingtalk.com'
OID='HFG333ePznAwB7gbeY5iS4wiEiE'
BID='r1R7q3QmWe6k4GO3uznXx3RmVxkXOEP2'

def get_token():
    r=requests.post(f'{API}/v1.0/oauth2/accessToken', json={'appKey':CID,'appSecret':CS}, timeout=10)
    return r.json().get('accessToken','')

def get_all_records(tok, sheet_id):
    """分页获取所有记录"""
    all_records=[]
    next_token=''
    while True:
        url=f'{API}/v1.0/notable/bases/{BID}/sheets/{sheet_id}/records'
        params={'operatorId':OID,'maxResults':100}
        if next_token:
            params['nextToken']=next_token
        r=requests.get(url, headers={'x-acs-dingtalk-access-token':tok,'Content-Type':'application/json'}, params=params, timeout=10)
        if r.status_code==200:
            data=r.json()
            records=data.get('records',[])
            all_records.extend(records)
            if not data.get('hasMore',False):
                break
            next_token=data.get('nextToken','')
        else:
            print(f'获取失败: {r.status_code} {r.text[:200]}')
            break
    return all_records

# 获取token
tok=get_token()

# 1. 获取门店信息表
print('获取门店信息...')
store_records=get_all_records(tok, 'UJ2aPH3')
store_map={}
for rec in store_records:
    rid=rec.get('id')
    fields=rec.get('fields',{})
    full_name=fields.get('门店全称','')
    short_name=fields.get('门店','')
    store_map[rid]=full_name if full_name else short_name

print(f'门店映射完成：{len(store_map)}家')

# 2. 获取5月+6月全部记录
print('\n获取5月全部记录...')
records_5 = get_all_records(tok, 'IzzHXbd')
print(f'5月总记录数：{len(records_5)}')

print('获取6月全部记录...')
records_6 = get_all_records(tok, 'Wlo2hWP')
print(f'6月总记录数：{len(records_6)}')

# 3. 处理并输出
months = [('5月', records_5), ('6月', records_6)]

for month_name, records in months:
    print(f'\n{"="*60}')
    print(f'【{month_name}差评 · 孙红梅区】')
    print(f'{"="*60}')
    
    # 筛选孙红梅区
    filtered = []
    for r in records:
        fields = r.get('fields',{})
        mgr = fields.get('区域经理',{})
        mgr_name = mgr.get('name','') if isinstance(mgr,dict) else ''
        if mgr_name == '孙红梅':
            filtered.append(r)
    
    # 按门店分组
    store_complaints = {}
    for r in filtered:
        fields = r.get('fields',{})
        linked = fields.get('门店',{})
        store_ids = linked.get('linkedRecordIds',[]) if isinstance(linked,dict) else []
        store_id = store_ids[0] if store_ids else ''
        store_name = store_map.get(store_id, f'未知({store_id})')
        
        date_ts = fields.get('反馈日期')
        date_str = datetime.fromtimestamp(date_ts/1000).strftime('%Y-%m-%d') if date_ts else ''
        product = fields.get('产品','')
        content = fields.get('顾客反馈内容','')
        store_reply = fields.get('门店反馈意见',{})
        reply = store_reply.get('markdown','') if isinstance(store_reply,dict) else str(store_reply)
        responsible = fields.get('责任',{})
        resp_name = responsible.get('name','') if isinstance(responsible,dict) else ''
        channel = fields.get('渠道',{})
        ch_name = channel.get('name','') if isinstance(channel,dict) else ''
        ctype = fields.get('类型',{})
        ct_name = ctype.get('name','') if isinstance(ctype,dict) else ''
        stars = fields.get('星级','')
        
        if store_name not in store_complaints:
            store_complaints[store_name] = []
        
        store_complaints[store_name].append({
            'date': date_str,
            'product': product,
            'content': content,
            'reply': reply,
            'responsible': resp_name,
            'channel': ch_name,
            'type': ct_name,
            'stars': stars
        })
    
    # 输出汇总
    total = sum(len(v) for v in store_complaints.values())
    print(f'孙红梅区共 {len(store_complaints)} 家门店，{total} 条差评\n')
    
    for store_name, complaints in sorted(store_complaints.items(), key=lambda x: len(x[1]), reverse=True):
        print(f'【{store_name}】{len(complaints)}条')
        
        types = {}
        channels = {}
        resp_yes = 0
        resp_no = 0
        for c in complaints:
            types[c['type']] = types.get(c['type'],0)+1
            channels[c['channel']] = channels.get(c['channel'],0)+1
            if c['responsible'] == '是':
                resp_yes += 1
            elif c['responsible'] == '否':
                resp_no += 1
        
        print(f'  类型分布: {types}')
        print(f'  渠道分布: {channels}')
        print(f'  责任判定: 是{resp_yes} / 否{resp_no}')
        
        print(f'  详情：')
        for i, c in enumerate(complaints):
            print(f'    {i+1}. [{c["date"]}] {c["stars"]} {c["channel"]} | {c["product"]} | {c["content"][:60]}')
            if c['reply']:
                print(f'       门店回复: {c["reply"][:60]}')
        print()

print(f'\n{"="*60}')
print('汇总完成')
print(f'{"="*60}')
