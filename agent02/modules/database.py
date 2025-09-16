import sqlite3
from datetime import datetime
import re

def init_db():
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_content TEXT NOT NULL,
            reminder_time DATETIME NOT NULL,
            location TEXT,
            weather_info TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    print("数据库初始化完成")

def add_task_to_db(task_content, reminder_time, location, weather_info):
    try:
        conn = sqlite3.connect('tasks.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO tasks (task_content, reminder_time, location, weather_info)
            VALUES (?, ?, ?, ?)
        ''', (task_content, reminder_time, location, weather_info))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"数据库插入失败: {e}")

def delete_task_by_id(task_id):
    """
    根据任务ID删除任务
    """
    try:
        conn = sqlite3.connect('tasks.db')
        c = conn.cursor()
        c.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        conn.commit()
        conn.close()
        print(f"任务 {task_id} 已删除")
        return True
    except Exception as e:
        print(f"删除任务失败: {e}")
        return False
    
def get_all_tasks():
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute('''
        SELECT id, task_content, reminder_time, location, weather_info 
        FROM tasks 
        ORDER BY reminder_time DESC
    ''')
    tasks = []
    for row in c.fetchall():
        task_id, task_content, reminder_time, location, weather_info = row
        # 格式化时间
        if isinstance(reminder_time, str):
            try:
                reminder_time = datetime.fromisoformat(reminder_time)
                formatted_time = reminder_time.strftime('%Y-%m-%d %H:%M')
            except ValueError:
                formatted_time = reminder_time
        else:
            formatted_time = reminder_time.strftime('%Y-%m-%d %H:%M')
        tasks.append({
            'id': task_id,
            'task_content': task_content,
            'time': formatted_time,
            'location': location or '无地点信息',
            'weather_info': weather_info
        })
    conn.close()
    return tasks
def format_datetime(dt_value):
    """
    统一格式化日期时间
    
    Args:
        dt_value: 日期时间值,可能是字符串或datetime对象
        
    Returns:
        格式化后的时间字符串
    """
    if isinstance(dt_value, datetime):
        # 如果是datetime对象，直接格式化
        return dt_value.strftime('%Y-%m-%d %H:%M')
    elif isinstance(dt_value, str):
        try:
            # 尝试解析ISO格式
            if 'T' in dt_value:
                dt_obj = datetime.fromisoformat(dt_value.replace('Z', '+00:00'))
                return dt_obj.strftime('%Y-%m-%d %H:%M')
            # 尝试解析SQLite的日期时间格式
            elif re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', dt_value):
                dt_obj = datetime.strptime(dt_value, '%Y-%m-%d %H:%M:%S')
                return dt_obj.strftime('%Y-%m-%d %H:%M')
            else:
                # 其他格式直接返回
                return dt_value
        except (ValueError, AttributeError):
            # 解析失败，返回原始值
            return dt_value
    else:
        # 其他类型，转换为字符串
        return str(dt_value)