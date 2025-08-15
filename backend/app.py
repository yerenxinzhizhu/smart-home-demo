import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import random
import time

# 初始化配置
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# 获取项目根目录绝对路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, 'frontend', 'dist')

app = Flask(__name__, 
           static_folder=FRONTEND_DIR,
           static_url_path='')

CORS(app)  # 允许跨域

# 确保前端目录存在
os.makedirs(FRONTEND_DIR, exist_ok=True)

# 模拟AI系统
class HomeSecurityAI:
    def __init__(self):
        self.model_status = "active"
    
    def detect(self):
        return random.choice(["家人", "陌生人"])

ai = HomeSecurityAI()

# 系统状态
state = {
    "door": "locked",
    "camera": "active",
    "defenses": {
        "signature_check": False,
        "model_protection": False
    },
    "stats": {
        "attacks": 0,
        "blocked": 0,
        "last_updated": None
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
# 核心路由
# ======================
@app.route('/')
@app.route('/<path:subpath>')
def serve_frontend(subpath=None):
    """服务前端入口文件"""
    try:
        return send_from_directory(FRONTEND_DIR, 'index.html')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ======================
# API路由
# ======================
@app.route('/api/health')
def health_check():
    """Render健康检查端点"""
    return jsonify({
        "status": "healthy",
        "timestamp": int(time.time())
    })

@app.route('/api/status')
def get_status():
    """获取系统状态"""
    state["stats"]["last_updated"] = time.strftime("%Y-%m-%d %H:%M:%S")
    return jsonify({
        "system": state,
        "ai": ai.model_status
    })

@app.route('/api/attack', methods=['POST'])
def handle_attack():
    """处理攻击请求"""
    data = request.json
    attack_type = data.get('type')
    
    state["stats"]["attacks"] += 1
    state["stats"]["last_updated"] = time.strftime("%Y-%m-%d %H:%M:%S")
    
    if attack_type == "command":
        if not state["defenses"]["signature_check"]:
            state["door"] = "unlocked"
            return jsonify({
                "success": True,
                "message": "门锁已被非法打开"
            })
        else:
            state["stats"]["blocked"] += 1
            return jsonify({
                "success": False,
                "message": "防御生效：指令验证已拦截"
            })
    
    elif attack_type == "camera":
        if not state["defenses"]["model_protection"]:
            state["camera"] = f"被欺骗({ai.detect()})"
            return jsonify({
                "success": True,
                "message": "摄像头被欺骗"
            })
        else:
            state["stats"]["blocked"] += 1
            return jsonify({
                "success": False,
                "message": "防御生效：AI模型已识别欺骗"
            })
    
    return jsonify({"success": False}), 400

@app.route('/api/defense', methods=['POST'])
def toggle_defense():
    """切换防御状态"""
    defense_type = request.json.get('type')
    if defense_type in state["defenses"]:
        state["defenses"][defense_type] = not state["defenses"][defense_type]
        return jsonify({
            "success": True,
            "state": state["defenses"][defense_type]
        })
    return jsonify({"success": False}), 400

# ======================
# 静态文件路由
# ======================
@app.route('/assets/<path:filename>')
def static_files(filename):
    """处理静态资源请求"""
    return send_from_directory(os.path.join(FRONTEND_DIR, 'assets'), filename)

# ======================
# 错误处理
# ======================
@app.errorhandler(404)
def not_found(e):
    """处理未找到的路由"""
    if request.path.startswith('/api'):
        return jsonify({"error": "API endpoint not found"}), 404
    return send_from_directory(FRONTEND_DIR, 'index.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False,
        threaded=True
    )