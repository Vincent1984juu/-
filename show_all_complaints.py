#!/usr/bin/env python3
"""
孙红梅区差评全记录 - 逐条呈现
"""
import requests
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
            break
    return all_records

tok=get_token()

# 获取门店信息
store_records=get_all_records(tok, 'UJ2aPH3')
store_map={}
for rec in store_records:
    rid=rec.get('id')
    fields=rec.get('fields',{})
    full_name=fields.get('门店全称','')
    short_name=fields.get('门店','')
    store_map[rid]=full_name if full_name else short_name

# 获取5月+6月
records_5=get_all_records(tok, 'IzzHXbd')
records_6=get_all_records(tok, 'Wlo2hWP')

months=[('5月',records_5),('6月',records_6)]

for month_name, records in months:
    # 筛选孙红梅区
    sun_records=[]
    for r in records:
        fields=r.get('fields',{})
        mgr=fields.get('区域经理',{})
        mgr_name=mgr.get('name','') if isinstance(mgr,dict) else ''
        if mgr_name=='孙红梅':
            sun_records.append(r)
    
    print(f'\n{"="*70}')
    print(f'【{month_name}差评 · 孙红梅区】共{len(sun_records)}条')
    print(f'{"="*70}')
    
    # 按门店分组
    store_map_data={}
    for r in sun_records:
        fields=r.get('fields',{})
        linked=fields.get('门店',{})
        store_ids=linked.get('linkedRecordIds',[]) if isinstance(linked,dict) else []
        store_id=store_ids[0] if store_ids else ''
        store_name=store_map.get(store_id, f'未知({store_id})')
        
        if store_name not in store_map_data:
            store_map_data[store_name]=[]
        
        date_ts=fields.get('反馈日期')
        date_str=datetime.fromtimestamp(date_ts/1000).strftime('%Y-%m-%d') if date_ts else ''
        product=fields.get('产品','')
        content=fields.get('顾客反馈内容','')
        store_reply=fields.get('门店反馈意见',{})
        reply=store_reply.get('markdown','') if isinstance(store_reply,dict) else str(store_reply)
        responsible=fields.get('责任',{})
        resp_name=responsible.get('name','') if isinstance(responsible,dict) else ''
        channel=fields.get('渠道',{})
        ch_name=channel.get('name','') if isinstance(channel,dict) else ''
        ctype=fields.get('类型',{})
        ct_name=ctype.get('name','') if isinstance(ctype,dict) else ''
        stars=fields.get('星级','')
        
        store_map_data[store_name].append({
            'date':date_str,'product':product,'content':content,'reply':reply,
            'responsible':resp_name,'channel':ch_name,'type':ct_name,'stars':stars
        })
    
    # 逐门店输出
    for store_name, complaints in sorted(store_map_data.items(), key=lambda x: len(x[1]), reverse=True):
        print(f'\n┌────────────────────────────────────────────────────────────┐')
        print(f'│ {store_name}  ·  {len(complaints)}条差评')
        print(f'└────────────────────────────────────────────────────────────┘')
        
        for i, c in enumerate(complaints, 1):
            print(f'\n  【{i}】{c["date"]} | {c["stars"]} | {c["channel"]} | 类型:{c["type"]} | 责任:{c["responsible"]}')
            print(f'  产品：{c["product"]}')
            print(f'  顾客：{c["content"]}')
            if c['reply']:
                # 清理换行
                reply_clean=c['reply'].replace('\n',' ')
                print(f'  门店：{reply_clean}')
            print(f'  ──')

print(f'\n{"="*70}')
print('全部呈现完毕')
print(f'{"="*70}')
