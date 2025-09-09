from flask import Flask, request, jsonify
from modules.dingtalk_bot import build_card, send_card_to_user
from modules.tools import WeatherClient
from modules.database import get_tasks_for_date  # 你需要封装这个方法
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

app = Flask(__name__)

# 初始化天气客户端
weather_client = WeatherClient(
    api_key=os.getenv("QWEATHER_API_KEY"),
    host=os.getenv("QWEATHER_API_HOST")
)

@app.route('/')
def index():
    return "✅ 钉钉智能提醒 Agent 已启动"

@app.route('/dingtalk/event', methods=['POST'])
def handle_event():
    data = request.json
    user_id = data.get("senderId")
    text = data.get("text", "").strip()

    # 示例：解析“查看9月10日杭州任务”
    if "查看" in text:
        date_str = "2025-09-10"  # TODO: 可用 NLP 模块解析
        location = "120.1551,30.2741"  # TODO: 可用地点解析模块

        try:
            tasks = get_tasks_for_date(date_str)
            if not tasks:
                return jsonify({"msg": "暂无任务"})

            weather = weather_client.get_weather_by_date(location, date_str)
            card = build_card(tasks[0], weather)
            result = send_card_to_user(user_id, card)
            return jsonify(result)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return jsonify({"msg": "未识别指令"})

@app.route('/test_card', methods=['GET'])
def test_card():
    # 用于本地测试卡片发送
    task = {
        "id": "test123",
        "task_content": "开会",
        "time_iso": "2025-09-10T09:00:00",
        "location_expression": "滨江"
    }
    weather = {
        "textDay": "晴",
        "tempMin": "28",
        "tempMax": "33"
    }
    card = build_card(task, weather)
    result = send_card_to_user("你的钉钉userId", card)
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
