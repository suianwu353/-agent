import json
from datetime import datetime
from modules.nlu import parse_user_input
from modules.scheduler import schedule_reminder, start_scheduler, scheduler

from datetime import datetime
print("系统当前时间：", datetime.now())

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

    # 2. 遍历任务，进行调度
    for task in tasks:
        task_content = task.get("task_content")
        time_iso = task.get("time_iso")  # 使用模型返回的标准时间字段
        location_expression = task.get("location_expression")

        if not task_content or not time_iso or not location_expression:
            continue

        # 2a. 解析 ISO 时间
        try:
            reminder_dt = datetime.fromisoformat(time_iso)
        except ValueError:
            print(f"无法解析任务 '{task_content}' 的时间 '{time_iso}'")
            continue

        # 2b. 设置提醒
        schedule_reminder(task_content, reminder_dt)

    # 3. 启动调度器
    if scheduler.get_jobs():
        start_scheduler()
    else:
        print("没有成功设置任何提醒。")


if __name__ == "__main__":
    main()
