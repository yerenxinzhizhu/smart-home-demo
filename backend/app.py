import os
# 彻底禁用GPU（针对无GPU环境优化）
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'  # 关键设置

# 内存优化配置
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # 完全隐藏TensorFlow日志
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import random

app = Flask(__name__, static_folder='../frontend', template_folder='../frontend')
CORS(app)

# 模拟的轻量级AI模型（完全去除TensorFlow依赖）
class MockAI:
    def predict(self, input_data):
        return random.choice(["家人", "陌生人"])

# 初始化状态
state = {
    "lock_status": "关闭",
    "camera_status": "无",
    "defense": {
        "signature_check": False,
        "model_hardening": False
    },
    "attack_count": 0,
    "success_attack": 0,
    "defense_count": 0
}

model = MockAI()

# 健康检查端点（Render必需）
@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/')
def serve_frontend():
    return send_from_directory(app.template_folder, 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

@app.route('/attack', methods=['POST'])
def handle_attack():
    data = request.json
    attack_type = data['type']
    log = ""
    state["attack_count"] += 1

    if attack_type == "fake_command":
        if not state["defense"]["signature_check"]:
            state["lock_status"] = "被打开（攻击成功）"
            state["success_attack"] += 1
            log = "攻击：伪造开门指令成功！门锁已被打开"
        else:
            state["defense_count"] += 1
            log = "防御：指令签名校验生效，伪造指令被拦截"

    elif attack_type == "adversarial_image":
        prediction = model.predict(None)
        if not state["defense"]["model_hardening"]:
            state["camera_status"] = f"陌生人→误判为{prediction}（攻击成功）"
            state["success_attack"] += 1
            log = "攻击：对抗样本生效，摄像头AI误判"
        else:
            state["defense_count"] += 1
            log = "防御：模型加固生效，对抗样本被识别"

    rates = {
        "attackRate": calc_rate(state["success_attack"]),
        "defenseRate": calc_rate(state["defense_count"])
    }
    
    return jsonify({
        "log": log,
        "lockStatus": state["lock_status"],
        "cameraStatus": state["camera_status"],
        **rates
    })

def calc_rate(success_count):
    return int((success_count / state["attack_count"]) * 100) if state["attack_count"] > 0 else 0

@app.route('/defense', methods=['POST'])
def handle_defense():
    data = request.json
    defense_type = data['type']
    state["defense"][defense_type] = not state["defense"][defense_type]
    status = "开启" if state["defense"][defense_type] else "关闭"
    return jsonify({
        "log": f"防御：{defense_type}已{status}",
        "attackRate": calc_rate(state["success_attack"]),
        "defenseRate": calc_rate(state["defense_count"])
    })

@app.route('/status', methods=['GET'])
def get_status():
    return jsonify(state)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False,
        threaded=True  # 启用多线程处理请求
    )