import os
from datetime import datetime

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
            formatted_time = task_time.strftime('%Y年%m月%d日 %H:%M')
        except (ValueError, KeyError):
            formatted_time = "未知时间"
        
        # 获取任务内容
        task_content = task_data.get('task_content', '无任务内容')
        
        # 获取地点信息
        location = task_data.get('location_expression', '无地点信息')
        if not location or location == 'null':
            location = '无地点信息'
        
        # 获取天气信息
        weather_info = task_data.get('weather_info', '无天气信息')
        
        # 检查文件是否存在，如果不存在则创建并添加表头
        if not os.path.exists(filename):
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("# 任务日志\n\n")
                f.write("> 本文件由智能提醒系统自动生成\n\n")
                f.write("| 时间 | 任务内容 | 地点 | 天气信息 | 记录时间 |\n")
                f.write("|------|----------|------|----------|----------|\n")
        
        # 追加任务信息
        with open(filename, 'a', encoding='utf-8') as f:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"| {formatted_time} | {task_content} | {location} | {weather_info} | {current_time} |\n")
        
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
            lines = f.readlines()
        
        # 提取指定日期的任务
        daily_tasks = []
        for line in lines:
            if line.startswith('|') and date in line:
                daily_tasks.append(line)
        
        # 生成报告
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write(f"# 每日任务报告 - {date}\n\n")
            
            if daily_tasks:
                f.write("## 今日任务汇总\n\n")
                f.write("| 时间 | 任务内容 | 地点 | 天气信息 | 记录时间 |\n")
                f.write("|------|----------|------|----------|----------|\n")
                for task in daily_tasks:
                    f.write(task)
                
                f.write(f"\n## 统计信息\n\n")
                f.write(f"- 今日共记录 {len(daily_tasks)} 个任务\n")
                
                # 简单分析
                morning_tasks = sum(1 for task in daily_tasks if ' 00:' in task or ' 01:' in task or ' 02:' in task or 
                                   ' 03:' in task or ' 04:' in task or ' 05:' in task or ' 06:' in task or 
                                   ' 07:' in task or ' 08:' in task or ' 09:' in task or ' 10:' in task or ' 11:' in task)
                afternoon_tasks = sum(1 for task in daily_tasks if ' 12:' in task or ' 13:' in task or ' 14:' in task or 
                                     ' 15:' in task or ' 16:' in task or ' 17:' in task)
                evening_tasks = sum(1 for task in daily_tasks if ' 18:' in task or ' 19:' in task or ' 20:' in task or 
                                   ' 21:' in task or ' 22:' in task or ' 23:' in task)
                
                f.write(f"- 上午任务: {morning_tasks} 个\n")
                f.write(f"- 下午任务: {afternoon_tasks} 个\n")
                f.write(f"- 晚上任务: {evening_tasks} 个\n")
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
            lines = f.readlines()
        
        # 计算日期范围
        from datetime import datetime, timedelta
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        recent_tasks = []
        for line in lines:
            if line.startswith('|') and len(line.split('|')) >= 6:
                parts = line.split('|')
                if len(parts) >= 2:
                    time_str = parts[1].strip()
                    try:
                        # 尝试解析时间
                        task_time = datetime.strptime(time_str, '%Y年%m月%d日 %H:%M')
                        if start_date <= task_time <= end_date:
                            recent_tasks.append({
                                'time': time_str,
                                'content': parts[2].strip() if len(parts) > 2 else '',
                                'location': parts[3].strip() if len(parts) > 3 else '',
                                'weather': parts[4].strip() if len(parts) > 4 else '',
                                'recorded_at': parts[5].strip() if len(parts) > 5 else ''
                            })
                    except ValueError:
                        # 如果时间解析失败，跳过
                        continue
        
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