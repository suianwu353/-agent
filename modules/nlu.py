# modules/nlu.py
import os
from http import HTTPStatus
import dashscope
from dotenv import load_dotenv
from datetime import datetime
load_dotenv()
dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")
today_str = datetime.now().strftime("%Y年%m月%d日")
now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
def parse_user_input(user_text: str):
    """从用户输入中抽取任务信息"""
    prompt = f"""
    你是一个任务解析助手。请从以下文本中抽取出所有任务，并以 JSON 数组的格式返回。
    每个任务对象必须包含以下字段（按顺序）：
    - "task_content": 任务的具体内容（字符串）
    - "time_expression": 原始的时间描述文本（字符串）
    - "time_iso": 将 time_expression 转换为 ISO 格式的时间，例如 "2025-09-10T15:00:00"（字符串）
    - "location_expression": 地点描述文本（字符串）
    - "needs_weather": 是否需要天气信息（布尔
        

    今天是 {today_str}。请根据当前日期生成 ISO 格式时间。
    
    现在是{now_str}

    如果时间表达是“几秒后”、“几分钟后”、“几小时后”等相对时间，请基于当前时间 {now_str} 进行计算，并生成准确的 ISO 格式时间。

    请确保输出是合法的 JSON 数组，字段之间用英文逗号分隔，结构可被 Python 的 json.loads() 正确解析。

    如果文本中没有任务，请返回一个空数组 []。
    
    如果文本中没有明确地点，请根据任务合理推断。
    
    是否需要天气信息，通过语境判断（只有线上活动才不需要天气，如通过手机电脑进行操作的活动；其他情况一律需要天气。几乎所有情况都需要天气）
    
    请从文本中抽取所有任务，每个任务对象必须独立包含：
    - task_content
    - time_expression
    - time_iso
    - location_expression
    - needs_weather

    如果文本中包含多个任务，请将它们分别拆分为多个 JSON 对象，组成一个 JSON 数组返回。

    示例输入: "提醒我明天下午三点开会，还有晚上8点去健身"（前提是今天是2025-09-09）
    示例输出:
    [
      {{
        "task_content": "开会",
        "time_expression": "明天下午三点",
        "time_iso": "2025-09-10T15:00:00",
        "location_expression": "会议室"
        "needs_weather":True
      }},
      {{
        "task_content": "去健身",
        "time_expression": "晚上8点",
        "time_iso": "2025-09-09T20:00:00",
        "location_expression": "健身房"
        "needs_weather":True
      }}
    ]

    现在，请解析以下文本：
    "{user_text}"
    """



    response = dashscope.Generation.call(
        model='qwen-plus',
        prompt=prompt,
        response_format={'type': 'json_object'}
    )

    if response.status_code == HTTPStatus.OK:
        # qwen-plus的json模式输出在 response.output.text 中
        return response.output.text
    else:
        print(f"请求失败: {response.code} - {response.message}")
        return "[]"