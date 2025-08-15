import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import random
import time

# 初始化配置
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'  # 禁用GPU
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'   # 减少日志输出

app = Flask(__name__, 
           static_folder='../frontend/dist',  # 指向构建后的前端文件
           template_folder='../frontend/dist')  # Vue/React构建后的目录

CORS(app)  # 允许跨域

# 模拟AI系统
class HomeAI:
    def __init__(self):
        self.model_status = "ready"
    
    def detect_person(self):
        return random.choice(["家人", "陌生人"])

ai_system = HomeAI()

# 系统状态
system_state = {
    "security": {
        "door": "locked",
        "camera": "active"
    },
    "stats": {
        "attacks": 0,
        "blocked": 0
    }
}

# ======================
# 中间件配置
# ======================
@app.after_request
def add_headers(response):
    """统一设置响应头"""
    if request.path.startswith('/api'):
        response.headers['Content-Type'] = 'application/json'
    elif response.mimetype == 'text/html':
        response.headers['Cache-Control'] = 'no-cache, no-store'
    return response

# ======================
# 前端路由处理
# ======================
@app.route('/')
@app.route('/<path:subpath>')
def serve_frontend(subpath=None):
    """处理所有前端路由"""
    return send_from_directory(app.static_folder, 'index.html')

# ======================
# API路由
# ======================
@app.route('/api/health')
def health_check():
    """健康检查端点（Render必需）"""
    return jsonify({
        "status": "online",
        "timestamp": int(time.time())
    })

@app.route('/api/status')
def get_status():
    """获取系统状态"""
    return jsonify({
        "system": system_state,
        "ai": ai_system.model_status
    })

@app.route('/api/attack', methods=['POST'])
def handle_attack():
    """处理攻击请求"""
    data = request.json
    attack_type = data.get('type')
    
    system_state["stats"]["attacks"] += 1
    
    if attack_type == "door_force":
        system_state["security"]["door"] = "breached"
        return jsonify({
            "success": True,
            "message": "门锁已被攻破"
        })
    
    elif attack_type == "camera_spoof":
        system_state["security"]["camera"] = "spoofed"
        return jsonify({
            "success": True,
            "message": f"摄像头被欺骗，识别为: {ai_system.detect_person()}"
        })
    
    return jsonify({"success": False}), 400

@app.route('/api/defense', methods=['POST'])
def toggle_defense():
    """切换防御状态"""
    defense_type = request.json.get('type')
    # 实现防御切换逻辑
    return jsonify({"success": True})

# ======================
# 错误处理
# ======================
@app.errorhandler(404)
def not_found(e):
    """处理404错误"""
    if request.path.startswith('/api'):
        return jsonify({"error": "Not found"}), 404
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False,
        threaded=True
    )