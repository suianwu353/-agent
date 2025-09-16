import dashscope
from dashscope import Generation
import json
import re
from datetime import datetime, timedelta

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
2. 提取时间信息并转换为ISO格式(time_iso),如果用户输入中包含相对时间（如“明天”、“后天”等），请根据当前日期计算出具体日期
3. 提取地点信息(location_expression)，如果没有则设为null
4. 判断是否需要天气信息(needs_weather)，如果需要则设为true

当前日期：{datetime.now().strftime('%Y年%m月%d日')}

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
            api_key="sk-e6ae8e4637e04f8aa40e73d9a2893723"  # 在实际应用中应该使用环境变量
        )
        print(f"API响应: {response}")
        # 提取模型返回的文本
        if response and response.output and response.output.text:
            result_text = response.output.text
            print(f"模型返回文本: {result_text}")

            # 清理响应文本，提取JSON部分
            json_match = re.search(r'\[.*\]', result_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                # 验证JSON格式
                try:
                    parsed_json = json.loads(json_str)
                    print(f"成功解析JSON: {parsed_json}")
                    
                    # 处理相对时间表达式
                    processed_tasks = []
                    for task in parsed_json:
                        time_iso = task.get('time_iso', '')
                        if time_iso:
                            # 转换相对时间为绝对时间
                            absolute_time = convert_relative_time(time_iso, user_input)
                            task['time_iso'] = absolute_time
                        processed_tasks.append(task)
                    
                    return json.dumps(processed_tasks, ensure_ascii=False)
                except json.JSONDecodeError as e:
                    print(f"JSON解析失败: {e}")
                    # 如果JSON解析失败，返回默认格式
                    return get_default_response(user_input)
            else:
                print("未找到JSON格式的响应")
                return get_default_response(user_input)
        else:
            print("API响应为空或格式不正确")
            return get_default_response(user_input)
            
    except Exception as e:
        print(f"NLU解析错误: {e}")
        return get_default_response(user_input)

def convert_relative_time(time_expression, user_input):
    """
    将相对时间表达式转换为绝对时间
    
    Args:
        time_expression: 时间表达式
        user_input: 原始用户输入（用于上下文理解）
        
    Returns:
        ISO格式的绝对时间字符串
    """
    now = datetime.now()
    
    # 首先检查是否是已经格式化的ISO时间（绝对时间）
    iso_pattern = r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}'
    if re.match(iso_pattern, time_expression):
        print(f"检测到ISO格式时间，直接返回: {time_expression}")
        return time_expression
    
    # 检查是否是日期格式（没有时间部分）
    date_pattern = r'\d{4}-\d{2}-\d{2}'
    if re.match(date_pattern, time_expression):
        print(f"检测到日期格式，添加默认时间: {time_expression}")
        return f"{time_expression}T12:00:00"
    
    # 处理常见的相对时间表达式
    relative_patterns = [
        (r'今天|今日', lambda: now.replace(hour=12, minute=0, second=0, microsecond=0)),
        (r'明天|明日', lambda: (now + timedelta(days=1)).replace(hour=12, minute=0, second=0, microsecond=0)),
        (r'后天', lambda: (now + timedelta(days=2)).replace(hour=12, minute=0, second=0, microsecond=0)),
        (r'大后天', lambda: (now + timedelta(days=3)).replace(hour=12, minute=0, second=0, microsecond=0)),
        (r'(\d+)小时后', lambda m: now + timedelta(hours=int(m.group(1)))),
        (r'(\d+)分钟?后', lambda m: now + timedelta(minutes=int(m.group(1)))),
        (r'(\d+)天后', lambda m: now + timedelta(days=int(m.group(1)))),
        (r'(\d+)周后', lambda m: now + timedelta(weeks=int(m.group(1)))),
        (r'(\d+)个月后', lambda m: now + timedelta(days=30*int(m.group(1)))),
        (r'(\d+)点钟?', lambda m: now.replace(hour=int(m.group(1)), minute=0, second=0, microsecond=0)),
        (r'下午(\d+)点', lambda m: now.replace(hour=int(m.group(1)) + 12, minute=0, second=0, microsecond=0)),
        (r'晚上(\d+)点', lambda m: now.replace(hour=int(m.group(1)) + 12, minute=0, second=0, microsecond=0)),
        (r'中午(\d+)点', lambda m: now.replace(hour=int(m.group(1)), minute=0, second=0, microsecond=0)),
        (r'上午(\d+)点', lambda m: now.replace(hour=int(m.group(1)), minute=0, second=0, microsecond=0)),
    ]
    
    # 检查是否是相对时间表达式
    for pattern, converter in relative_patterns:
        match = re.search(pattern, time_expression)
        if match:
            try:
                if callable(converter):
                    result_time = converter()
                else:
                    result_time = converter(match)
                print(f"相对时间 '{time_expression}' 转换为: {result_time}")
                return result_time.strftime('%Y-%m-%dT%H:%M:%S')
            except (ValueError, AttributeError):
                continue
    
    # 如果不是相对时间，尝试解析为绝对时间
    try:
        # 尝试解析各种时间格式
        time_formats = [
            '%Y年%m月%d日 %H:%M',
            '%Y-%m-%d %H:%M',
            '%Y/%m/%d %H:%M',
            '%m月%d日 %H:%M',
            '%m-%d %H:%M',
            '%H:%M'
        ]
        
        for time_format in time_formats:
            try:
                parsed_time = datetime.strptime(time_expression, time_format)
                # 如果只包含时间，使用当前日期
                if time_format == '%H:%M':
                    parsed_time = parsed_time.replace(
                        year=now.year, 
                        month=now.month, 
                        day=now.day
                    )
                # 如果只包含月日，使用当前年份
                elif time_format in ['%m月%d日 %H:%M', '%m-%d %H:%M']:
                    parsed_time = parsed_time.replace(year=now.year)
                
                return parsed_time.strftime('%Y-%m-%dT%H:%M:%S')
            except ValueError:
                continue
    except Exception:
        pass
    
    # 如果都无法解析，返回当前时间
    print(f"无法解析时间 '{time_expression}'，使用当前时间")
    return now.strftime('%Y-%m-%dT%H:%M:%S')

def get_default_response(user_input):
    """
    当模型解析失败时返回默认响应
    
    Args:
        user_input: 用户输入的文本
        
    Returns:
        默认的JSON响应
    """
    now = datetime.now()
    
    # 尝试从用户输入中提取相对时间
    relative_time = convert_relative_time(user_input, user_input)
    
    # 尝试提取地点信息
    location_pattern = r'(在|去|到)(.*?)(上课|开会|吃饭|购物|买东西|工作|学习|睡觉|休息|运动)'
    location_match = re.search(location_pattern, user_input)
    location_expression = location_match.group(2).strip() if location_match else None

    default_response = [
        {
            "task_content": user_input,
            "time_iso": relative_time,
            "location_expression": location_expression,
            "needs_weather": True
        }
    ]
    return json.dumps(default_response, ensure_ascii=False)

# 测试函数
if __name__ == "__main__":
    test_cases = [
        "明天下午3点记得去超市买东西",
        "2小时后开会",
        "后天早上9点上课",
        "10分钟后提醒我喝水",
        "3天后交作业",
        "今天下午5点健身"
    ]
    
    for test_input in test_cases:
        result = parse_user_input(test_input)
        print(f"输入: {test_input}")
        print(f"解析结果: {result}")
        print()