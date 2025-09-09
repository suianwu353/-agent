import requests
import os

def get_access_token(app_key=None, app_secret=None):
    app_key = app_key or os.getenv("DINGTALK_APP_KEY")
    app_secret = app_secret or os.getenv("DINGTALK_APP_SECRET")

    url = "https://oapi.dingtalk.com/gettoken"
    params = {
        "appkey": app_key,
        "appsecret": app_secret
    }
    response = requests.get(url, params=params)
    data = response.json()
    if data.get("errcode") == 0:
        return data["access_token"]
    else:
        raise Exception(f"获取 access_token 失败：{data}")

def send_card_to_user(user_id: str, card_json: dict) -> dict:
    access_token = get_access_token()
    url = f"https://oapi.dingtalk.com/topapi/message/corpconversation/asyncsend_v2?access_token={access_token}"

    payload = {
        "agent_id": os.getenv("DINGTALK_AGENT_ID"),
        "userid_list": user_id,
        "msg": card_json
    }

    response = requests.post(url, json=payload)
    return response.json()

def build_card(task: dict, weather: dict) -> dict:
    date_str = task.get("time_iso", "")[:10]
    title = f"📅 {date_str} {task.get('location_expression', '未知地点')}日程"
    text = (
        f"📝 任务：{task.get('task_content', '无')}\n"
        f"🌤️ 天气：{weather.get('textDay', '未知')}，{weather.get('tempMin', '?')}°C~{weather.get('tempMax', '?')}°C\n"
        f"🕒 时间：{task.get('time_iso', '未知')}\n"
        f"📍 地点：{task.get('location_expression', '未指定')}"
    )

    return {
        "msgtype": "actionCard",
        "actionCard": {
            "title": title,
            "text": text,
            "btnOrientation": "0",
            "btns": [
                {
                    "title": "✅ 完成",
                    "actionURL": f"https://your-server.com/complete?task_id={task.get('id')}"
                },
                {
                    "title": "🗑️ 删除",
                    "actionURL": f"https://your-server.com/delete?task_id={task.get('id')}"
                }
            ]
        }
    }
