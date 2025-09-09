import json
from datetime import datetime
from modules.nlu import parse_user_input
from modules.database import init_db, add_task_to_db
from modules.tools import WeatherClient
from modules.markdown_logger import append_task_to_markdown  # 新增模块

# 初始化数据库
init_db()

# 初始化天气客户端（请替换为你的真实 API Key）
weather_client = WeatherClient(api_key="bc4bdc854f774b3895afe2e2e517bbc0")

def main():
    user_input = input("你好！请输入你的提醒事项：")
    while True if user_input not in {"exit"} else False:

        # 1. 语义解析
        tasks_json_str = parse_user_input(user_input)
        try:
            tasks = json.loads(tasks_json_str)
        except json.JSONDecodeError:
            print("解析任务失败，请检查输入或模型返回。")
            return

        if not tasks:
            print("没有检测到任何任务。")
            return

        # 2. 遍历任务，处理记录逻辑
        for task in tasks:
            task_content = task.get("task_content")
            time_iso = task.get("time_iso")
            location_expression = task.get("location_expression")
            needs_weather = task.get("needs_weather")

            if not task_content or not time_iso:
                print("任务缺少必要字段，跳过。")
                continue

            # 时间解析
            try:
                reminder_dt = datetime.fromisoformat(time_iso)
            except ValueError:
                print(f"无法解析时间: {time_iso}")
                continue

            # 天气查询（如果需要）
            # 天气查询（如果需要）
            weather_info = "（无天气信息）"
            if needs_weather:
                if location_expression:
                    location = "120.1551,30.2741"  # 默认杭州经纬度，可扩展为地点→坐标映射
                    try:
                        target_date_str = reminder_dt.strftime('%Y-%m-%d')  # 从 ISO 时间提取日期
                        weather_data = weather_client.get_weather_by_date(location, target_date_str, days='15d')
                        if weather_data:
                            weather_info = (
                                f"{weather_data['textDay']}，{weather_data['tempMin']}°C~{weather_data['tempMax']}°C，"
                                f"风速：{weather_data['windSpeedDay']} km/h，湿度：{weather_data['humidity']}%"
                            )
                        else:
                            weather_info = "（未找到该日期的天气数据）"
                    except Exception as e:
                        print("天气查询失败：", e)
                        weather_info = "（天气查询失败）"
                else:
                    weather_info = "（未提供地点，无法查询天气）"

            # 存入数据库
            add_task_to_db(
                task_content=task_content,
                reminder_time=reminder_dt,
                location=location_expression,
                weather_info=weather_info
            )

            # 写入 Markdown 备忘录
            append_task_to_markdown({
                "task_content": task_content,
                "time_iso": time_iso,
                "location_expression": location_expression,
                "weather_info": weather_info
            })

        print("✅ 所有任务已记录完成，可在 task_log.md 中查看。")
        user_input=input("请继续输入,输入exit退出记录")
if __name__ == "__main__":
    main()
