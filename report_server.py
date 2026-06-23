#!/usr/bin/env python3
"""
营业额分析报告存储服务
轻量API，用于保存/加载店长填写的报告数据
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import uuid
from datetime import datetime

app = Flask(__name__)
CORS(app)  # 允许跨域

# 数据存储目录
DATA_DIR = "/root/.openclaw/workspace/reports-data"
os.makedirs(DATA_DIR, exist_ok=True)

def get_report_path(report_id):
    return os.path.join(DATA_DIR, f"{report_id}.json")

@app.route('/save-report', methods=['POST'])
def save_report():
    """保存报告数据"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
        
        # 生成或获取报告ID
        report_id = data.get('report_id') or str(uuid.uuid4())[:12]
        
        # 添加元数据
        report_data = {
            "report_id": report_id,
            "store_name": data.get('store_name', ''),
            "region": data.get('region', ''),
            "month": data.get('month', ''),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "report_content": data.get('report_content', {})
        }
        
        # 保存到文件
        filepath = get_report_path(report_id)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        return jsonify({
            "success": True,
            "report_id": report_id,
            "message": "Report saved successfully"
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/get-report/<report_id>', methods=['GET'])
def get_report(report_id):
    """获取报告数据"""
    try:
        filepath = get_report_path(report_id)
        
        if not os.path.exists(filepath):
            return jsonify({"success": False, "error": "Report not found"}), 404
        
        with open(filepath, 'r', encoding='utf-8') as f:
            report_data = json.load(f)
        
        return jsonify({
            "success": True,
            "data": report_data
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """健康检查"""
    return jsonify({"status": "ok", "timestamp": datetime.now().isoformat()})

if __name__ == '__main__':
    # 生产环境用gunicorn，开发环境直接运行
    app.run(host='0.0.0.0', port=5001, debug=False)
