import os
from datetime import datetime
import re
def append_task_to_markdown(task_data, filename="task_log.md"):
    """
    将任务信息追加到Markdown文件
    
    Args:
        task_data: 任务数据字典，包含task_content, time_iso, location_expression, weather_info
        filename: Markdown文件名
    """
    try:
        # 解析时间
        try:
            task_time = datetime.fromisoformat(task_data['time_iso'])
            formatted_date = task_time.strftime('%Y-%m-%d')
            formatted_time = task_time.strftime('%H:%M')
        except (ValueError, KeyError):
            formatted_date = "未知日期"
            formatted_time = "未知时间"
        
        # 获取任务内容
        task_content = task_data.get('task_content', '无任务内容')
        
        # 获取地点信息
        location = task_data.get('location_expression', '无地点信息')
        if not location or location == 'null':
            location = '无地点信息'
        
        # 获取天气信息
        weather_info = task_data.get('weather_info', '无天气信息')
        
        # 检查文件是否存在，如果不存在则创建并添加初始内容
        if not os.path.exists(filename):
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("# 文件    大纲\n\n")
        
        # 读取现有内容
        lines = []
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        
        # 查找或创建日期标题
        date_header = f"{formatted_date}\n"
        date_found = False
        task_inserted = False
        new_lines = []
        
        for i, line in enumerate(lines):
            # 检查是否找到日期标题
            if line.strip() == formatted_date:
                date_found = True
                new_lines.append(line)
                # 在日期标题后插入任务
                new_lines.append(f"{task_content}\n\n")
                new_lines.append(f"时间：{task_data['time_iso']}\n")
                if location != '无地点信息':
                    new_lines.append(f"地点：{location}\n")
                if weather_info != '无天气信息':
                    new_lines.append(f"天气：{weather_info}\n")
                new_lines.append("状态：pending\n\n")
                task_inserted = True
            else:
                new_lines.append(line)
        
        # 如果没有找到日期标题，在文件末尾添加
        if not date_found:
            new_lines.append(f"\n{formatted_date}\n")
            new_lines.append(f"{task_content}\n\n")
            new_lines.append(f"时间：{task_data['time_iso']}\n")
            if location != '无地点信息':
                new_lines.append(f"地点：{location}\n")
            if weather_info != '无天气信息':
                new_lines.append(f"天气：{weather_info}\n")
            new_lines.append("状态：pending\n\n")
            task_inserted = True
        
        # 如果任务已经插入，直接写入文件
        if task_inserted:
            with open(filename, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
        else:
            # 在文件末尾添加新任务
            with open(filename, 'a', encoding='utf-8') as f:
                f.write(f"\n{formatted_date}\n")
                f.write(f"{task_content}\n\n")
                f.write(f"时间：{task_data['time_iso']}\n")
                if location != '无地点信息':
                    f.write(f"地点：{location}\n")
                if weather_info != '无天气信息':
                    f.write(f"天气：{weather_info}\n")
                f.write("状态：pending\n\n")
        
        print(f"任务已记录到 {filename}")
        
    except Exception as e:
        print(f"记录到Markdown文件失败: {e}")

def generate_daily_report(date=None, filename="task_log.md", report_filename=None):
    """
    生成每日任务报告
    
    Args:
        date: 日期字符串，格式为YYYY-MM-DD，默认为今天
        filename: 任务日志文件名
        report_filename: 报告文件名，默认为daily_report_YYYY-MM-DD.md
    """
    try:
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        if report_filename is None:
            report_filename = f"daily_report_{date}.md"
        
        # 读取任务日志
        if not os.path.exists(filename):
            print("任务日志文件不存在")
            return
        
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取指定日期的任务
        daily_tasks = []
        lines = content.split('\n')
        current_date = None
        current_task = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 检测日期标题
            if re.match(r'\d{4}-\d{2}-\d{2}', line):
                current_date = line
                continue
                
            # 如果是任务内容
            if current_date == date and line and not line.startswith(('时间：', '地点：', '天气：', '状态：')):
                if current_task:  # 保存上一个任务
                    daily_tasks.append(current_task)
                current_task = {'content': line, 'date': current_date}
            elif current_date == date and line.startswith('时间：'):
                current_task['time'] = line.replace('时间：', '')
            elif current_date == date and line.startswith('地点：'):
                current_task['location'] = line.replace('地点：', '')
            elif current_date == date and line.startswith('天气：'):
                current_task['weather'] = line.replace('天气：', '')
            elif current_date == date and line.startswith('状态：'):
                current_task['status'] = line.replace('状态：', '')
        
        # 添加最后一个任务
        if current_task and current_date == date:
            daily_tasks.append(current_task)
        
        # 生成报告
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write(f"# 每日任务报告 - {date}\n\n")
            
            if daily_tasks:
                f.write("## 今日任务汇总\n\n")
                for task in daily_tasks:
                    f.write(f"### {task.get('content', '无内容')}\n")
                    f.write(f"- **时间**: {task.get('time', '未知时间')}\n")
                    if 'location' in task:
                        f.write(f"- **地点**: {task.get('location')}\n")
                    if 'weather' in task:
                        f.write(f"- **天气**: {task.get('weather')}\n")
                    f.write(f"- **状态**: {task.get('status', '未知状态')}\n\n")
                
                f.write(f"## 统计信息\n\n")
                f.write(f"- 今日共记录 {len(daily_tasks)} 个任务\n")
                
            else:
                f.write("今日暂无任务记录\n")
        
        print(f"每日报告已生成: {report_filename}")
        
    except Exception as e:
        print(f"生成每日报告失败: {e}")

def get_recent_tasks(days=7, filename="task_log.md"):
    """
    获取最近几天的任务
    
    Args:
        days: 最近多少天
        filename: 任务日志文件名
        
    Returns:
        最近任务的列表
    """
    try:
        if not os.path.exists(filename):
            return []
        
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 计算日期范围
        from datetime import datetime, timedelta
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        recent_tasks = []
        lines = content.split('\n')
        current_date = None
        current_task = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 检测日期标题
            date_match = re.match(r'(\d{4}-\d{2}-\d{2})', line)
            if date_match:
                current_date = date_match.group(1)
                continue
                
            # 如果是任务内容
            if current_date and line and not line.startswith(('时间：', '地点：', '天气：', '状态：')):
                if current_task and current_date:  # 保存上一个任务
                    try:
                        task_date = datetime.strptime(current_date, '%Y-%m-%d')
                        if start_date <= task_date <= end_date:
                            recent_tasks.append(current_task)
                    except ValueError:
                        pass
                current_task = {'content': line, 'date': current_date}
            elif current_date and line.startswith('时间：'):
                current_task['time'] = line.replace('时间：', '')
            elif current_date and line.startswith('地点：'):
                current_task['location'] = line.replace('地点：', '')
            elif current_date and line.startswith('天气：'):
                current_task['weather'] = line.replace('天气：', '')
            elif current_date and line.startswith('状态：'):
                current_task['status'] = line.replace('状态：', '')
        
        # 添加最后一个任务
        if current_task and current_date:
            try:
                task_date = datetime.strptime(current_date, '%Y-%m-%d')
                if start_date <= task_date <= end_date:
                    recent_tasks.append(current_task)
            except ValueError:
                pass
        
        return recent_tasks
        
    except Exception as e:
        print(f"获取最近任务失败: {e}")
        return []

# 测试函数
if __name__ == "__main__":
    # 测试记录任务
    test_task = {
        "task_content": "测试任务内容",
        "time_iso": "2023-12-01T15:00:00",
        "location_expression": "测试地点",
        "weather_info": "晴天，25°C"
    }
    
    append_task_to_markdown(test_task)
    
    # 测试生成报告
    generate_daily_report("2023-12-01")
    
    # 测试获取最近任务
    recent = get_recent_tasks(7)
    print(f"最近7天的任务数量: {len(recent)}")