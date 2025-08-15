import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import random
import time
from flask import make_response
from flask import render_template
# 禁用GPU并优化TensorFlow日志
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

app = Flask(__name__, static_folder='../frontend', template_folder='../frontend')
CORS(app)  # 允许跨域

# 模拟的轻量级AI模型（避免使用真实TensorFlow）
class HomeSecurityAI:
    def __init__(self):
        self.model_loaded = True
    
    def predict_person(self):
        return random.choice(["家人", "陌生人"])
    
    def check_command(self, cmd):
        return cmd == "合法指令"

ai_system = HomeSecurityAI()

# 系统状态存储
system_state = {
    "door_lock": "locked",
    "camera": {"status": "active", "last_detection": None},
    "defense": {
        "signature_verification": False,
        "model_protection": False
    },
    "stats": {
        "total_attacks": 0,
        "blocked_attacks": 0,
        "last_attack": None
    }
}

# 强制JSON响应中间件
@app.after_request
def enforce_json(response):
    response.headers['Content-Type'] = 'application/json'
    response.headers['Cache-Control'] = 'no-cache, no-store'
    return response

# Render必需的健康检查端点
@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "services": {
            "ai": ai_system.model_loaded,
            "last_heartbeat": int(time.time())
        }
    })

# 前端路由
@app.route('/')
def home():
    response = make_response(render_template('index.html'))
    response.headers['Content-Type'] = 'text/html; charset=utf-8'
    return response@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

# API路由
@app.route('/api/status')
def get_status():
    return jsonify({
        "system": system_state,
        "ai_ready": ai_system.model_loaded
    })

@app.route('/api/attack', methods=['POST'])
def handle_attack():
    data = request.json
    attack_type = data.get('type')
    
    system_state["stats"]["total_attacks"] += 1
    system_state["stats"]["last_attack"] = time.strftime("%Y-%m-%d %H:%M:%S")
    
    if attack_type == "command_injection":
        if not system_state["defense"]["signature_verification"]:
            system_state["door_lock"] = "unlocked_attacked"
            result = {"success": True, "message": "门锁已被非法打开"}
        else:
            system_state["stats"]["blocked_attacks"] += 1
            result = {"success": False, "message": "防御生效：指令签名验证已拦截攻击"}
    
    elif attack_type == "camera_spoof":
        detection = ai_system.predict_person()
        if not system_state["defense"]["model_protection"]:
            system_state["camera"]["last_detection"] = f"误判为{detection}"
            result = {"success": True, "message": "摄像头被欺骗"}
        else:
            system_state["stats"]["blocked_attacks"] += 1
            result = {"success": False, "message": "防御生效：模型保护已识别欺骗"}
    
    return jsonify({
        **result,
        "stats": system_state["stats"]
    })

@app.route('/api/defense', methods=['POST'])
def toggle_defense():
    defense_type = request.json.get('type')
    if defense_type in system_state["defense"]:
        system_state["defense"][defense_type] = not system_state["defense"][defense_type]
        return jsonify({
            "success": True,
            "new_state": system_state["defense"][defense_type],
            "message": f"{defense_type}已{'启用' if system_state['defense'][defense_type] else '禁用'}"
        })
    return jsonify({"success": False, "message": "无效的防御类型"}), 400

@app.route('/api/reset', methods=['POST'])
def reset_system():
    system_state.update({
        "door_lock": "locked",
        "camera": {"status": "active", "last_detection": None},
        "stats": {
            "total_attacks": 0,
            "blocked_attacks": 0,
            "last_attack": None
        }
    })
    return jsonify({"success": True, "message": "系统已重置"})

# 通配路由处理前端路由
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    if path.startswith('api/'):
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