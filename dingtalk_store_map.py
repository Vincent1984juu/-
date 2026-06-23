# 门店 deptId 映射表
# 由于应用缺少通讯录权限，无法自动获取部门列表
# 请手动补充门店的 deptId（从钉钉管理后台获取）

STORE_DEPT_MAP = {
    "J030广州小北店": "861638740",
    "黄圃店": None,  # 待补充，需从钉钉后台获取
    "蓝天金地店": None,  # 待补充
    # 添加更多门店...
}

def get_store_dept_id(store_name):
    """根据门店名称获取deptId"""
    return STORE_DEPT_MAP.get(store_name)

def add_store(store_name, dept_id):
    """添加门店映射"""
    STORE_DEPT_MAP[store_name] = dept_id
