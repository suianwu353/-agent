import os

def append_task_to_markdown(task, filename="task_log.md"):
    date_str = task["time_iso"].split("T")[0]
    header = f"## 📅 {date_str}\n"

    if not os.path.exists(filename):
        with open(filename, "w", encoding="utf-8") as f:
            f.write("# 📝 任务备忘录\n")

    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()

    if header not in content:
        with open(filename, "a", encoding="utf-8") as f:
            f.write(f"\n{header}")

    with open(filename, "a", encoding="utf-8") as f:
        f.write(f"\n### 📌 {task['task_content']}\n")
        f.write(f"- ⏰ 时间：{task['time_iso']}\n")
        f.write(f"- 📍 地点：{task.get('location_expression', '无')}\n")
        f.write(f"- 🌤️ 天气：{task.get('weather_info', '无')}\n")
        f.write(f"- 🗂 状态：pending\n")
