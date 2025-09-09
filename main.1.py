import json
from datetime import datetime
from modules.nlu import parse_user_input
from modules.scheduler import schedule_reminder, start_scheduler, scheduler
from modules.database import init_db, add_task_to_db
from modules.tools import WeatherClient
from modules.markdown_logger import append_task_to_markdown

# 初始化数据库
init_db()

# 初始化天气客户端（请替换为你的真实 API Key）
weather_client = WeatherClient(api_key= "19a19215c23589dfcd506d58480f069f"
)

def main():
    user_input = input("你好！请输入你的提醒事项：")

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

    # 2. 遍历任务，处理提醒逻辑
    for task in tasks:
        task_content = task.get("task_content")
        time_iso = task.get("time_iso")
        location_expression = task.get("location_expression")
        needs_weather = task.get("needs_weather")

        if not task_content or not time_iso:
            print("任务缺少必要字段，跳过。")
            continue

        # 2a. 时间解析
        try:
            reminder_dt = datetime.fromisoformat(time_iso)
        except ValueError:
            print(f"无法解析时间: {time_iso}")
            continue

        # 2b. 天气查询（如果需要）
        weather_info = None
        print(needs_weather,location_expression)
        if needs_weather :

            #and location_expression:
            # 你可以在此加入地点到城市编码的映射逻辑
            # 示例：杭州 → 330100
            city_code = "330100"  # 默认使用杭州
            try:
                weather_data = weather_client.query_weather(city_code, mode="base")
                live = weather_data["lives"][0]
                weather_info = f"{live['weather']}，{live['temperature']}℃"
                print(f"【{live['city']}】当前天气：{live['weather']}，温度：{live['temperature']}℃")

            except Exception as e:
                print("天气查询失败：", e)

        # 2c. 设置提醒
        schedule_reminder(task_content, reminder_dt)

        # 2d. 存入数据库
        add_task_to_db(
            task_content=task_content,
            reminder_time=reminder_dt,
            location=location_expression,
            weather_info=weather_info
        )

    # 3. 启动调度器
    if scheduler.get_jobs():
        start_scheduler()
    else:
        print("没有成功设置任何提醒。")

if __name__ == "__main__":
    main()
