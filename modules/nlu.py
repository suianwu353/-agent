import dashscope
from dashscope import Generation
import json
import re

def parse_user_input(user_input):
    """
    使用通义千问模型解析用户输入，提取任务信息
    
    Args:
        user_input: 用户输入的文本
        
    Returns:
        JSON字符串，包含解析出的任务信息
    """
    # 构建提示词
    prompt = f"""
请从以下用户输入中提取提醒事项信息，并以JSON格式返回。请确保时间转换为ISO 8601格式。

要求：
1. 提取任务内容(task_content)
2. 提取时间信息并转换为ISO格式(time_iso)
3. 提取地点信息(location_expression)，如果没有则设为null
4. 判断是否需要天气信息(needs_weather)，如果需要则设为true

如果用户输入中包含多个任务，请返回任务数组。

输出格式示例：
[
  {{
    "task_content": "任务内容描述",
    "time_iso": "2023-12-01T15:00:00",
    "location_expression": "地点信息或null",
    "needs_weather": true/false
  }}
]

用户输入：{user_input}

请直接返回JSON格式，不要有其他解释文字。
"""

    try:
        # 调用通义千问API
        response = Generation.call(
            model='qwen-plus',
            prompt=prompt,
            api_key='sk-e6ae8e4637e04f8aa40e73d9a2893723'  # 在实际应用中应该使用环境变量
        )
        
        # 提取模型返回的文本
        if response and response.output and response.output.text:
            result_text = response.output.text
            
            # 清理响应文本，提取JSON部分
            json_match = re.search(r'\[.*\]', result_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                # 验证JSON格式
                try:
                    parsed_json = json.loads(json_str)
                    return json.dumps(parsed_json, ensure_ascii=False)
                except json.JSONDecodeError:
                    # 如果JSON解析失败，返回默认格式
                    return get_default_response(user_input)
            else:
                return get_default_response(user_input)
        else:
            return get_default_response(user_input)
            
    except Exception as e:
        print(f"NLU解析错误: {e}")
        return get_default_response(user_input)

def get_default_response(user_input):
    """
    当模型解析失败时返回默认响应
    
    Args:
        user_input: 用户输入的文本
        
    Returns:
        默认的JSON响应
    """
    default_response = [
        {
            "task_content": user_input,
            "time_iso": "2023-12-01T12:00:00",  # 默认时间
            "location_expression": None,
            "needs_weather": False
        }
    ]
    return json.dumps(default_response, ensure_ascii=False)

# 测试函数
if __name__ == "__main__":
    test_input = "明天下午3点记得去超市买东西"
    result = parse_user_input(test_input)
    print("解析结果:", result)