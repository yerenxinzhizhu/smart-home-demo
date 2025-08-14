import os
os.environ['KERAS_BACKEND'] = 'tensorflow'  # 强制使用TensorFlow后端
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'   # 禁用oneDNN警告
import tensorflow as tf
from tensorflow import keras
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import random

app = Flask(__name__, static_folder='../frontend', template_folder='../frontend')
CORS(app)  # 允许前端跨域访问

# 初始化状态变量
state = {
    "lock_status": "关闭",
    "camera_status": "无",
    "defense": {
        "signature_check": False,  # 指令签名校验（默认关闭）
        "model_hardening": False   # 模型加固（默认关闭）
    },
    "attack_count": 0,
    "success_attack": 0,
    "defense_count": 0
}

# 加载预训练模型（模拟摄像头AI）
model = tf.keras.applications.MobileNetV2(weights='imagenet')

# 前端路由
@app.route('/')
def serve_frontend():
    return send_from_directory(app.template_folder, 'index.html')

# 静态文件路由
@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

# API路由
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
        if not state["defense"]["model_hardening"]:
            state["camera_status"] = "陌生人→误判为家人（攻击成功）"
            state["success_attack"] += 1
            log = "攻击：对抗样本生效，摄像头AI误判"
        else:
            state["defense_count"] += 1
            log = "防御：模型加固生效，对抗样本被识别"

    attack_rate = int((state["success_attack"] / state["attack_count"]) * 100) if state["attack_count"] > 0 else 0
    defense_rate = int((state["defense_count"] / state["attack_count"]) * 100) if state["attack_count"] > 0 else 0

    return jsonify({
        "log": log,
        "lockStatus": state["lock_status"],
        "cameraStatus": state["camera_status"],
        "attackRate": attack_rate,
        "defenseRate": defense_rate
    })

@app.route('/defense', methods=['POST'])
def handle_defense():
    data = request.json
    defense_type = data['type']
    state["defense"][defense_type] = not state["defense"][defense_type]
    status = "开启" if state["defense"][defense_type] else "关闭"
    return jsonify({
        "log": f"防御：{defense_type}已{status}",
        "attackRate": int((state["success_attack"] / state["attack_count"]) * 100) if state["attack_count"] > 0 else 0,
        "defenseRate": int((state["defense_count"] / state["attack_count"]) * 100) if state["attack_count"] > 0 else 0
    })

@app.route('/status', methods=['GET'])
def get_status():
    return jsonify(state)

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')