# modules/scheduler.py
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime

# 初始化调度器
scheduler = BlockingScheduler(timezone="Asia/Shanghai") # 建议明确指定时区

def schedule_reminder(task_content: str, reminder_time: datetime):
    """添加一个提醒任务到调度器"""
    scheduler.add_job(
        func=trigger_reminder,      # 到时间时要执行的函数
        trigger='date',             # 一次性任务
        run_date=reminder_time,     # 运行时间
        args=[task_content]         # 传递给函数的参数
    )
    print(f"已成功设置提醒: '{task_content}' 在 {reminder_time.strftime('%Y-%m-%d %H:%M:%S')}")

def trigger_reminder(task_content: str):
    """这是提醒被触发时执行的函数"""
    print("\n-------------------------")
    print(f"⏰【提醒时间到！】⏰: {task_content}")
    print("-------------------------")

def start_scheduler():
    """启动调度器并阻塞进程"""
    print("调度器已启动，等待任务触发...")
    scheduler.start()