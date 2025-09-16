from flask import Flask, render_template, request, jsonify
import json
from datetime import datetime
from modules.nlu import parse_user_input
from modules.database import init_db, add_task_to_db, get_all_tasks, delete_task_by_id
from modules.tools import WeatherClient,get_location_coordinates
from modules.markdown_logger import append_task_to_markdown, delete_task_from_markdown
import sqlite3

app = Flask(__name__)

# 初始化数据库
init_db()

# 初始化天气客户端
weather_client = WeatherClient(api_key="bc4bdc854f774b3895afe2e2e517bbc0")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/add-task', methods=['POST'])
def add_task():
    try:
        data = request.get_json()
        user_input = data.get('user_input', '')
        
        if not user_input:
            return jsonify({'error': '输入不能为空'}), 400

        # 1. 语义解析
        tasks_json_str = parse_user_input(user_input)
        try:
            tasks = json.loads(tasks_json_str)
        except json.JSONDecodeError:
            return jsonify({'error': '解析任务失败，请检查输入或模型返回。'}), 500

        if not tasks:
            return jsonify({'error': '没有检测到任何任务。'}), 400

        results = []
        
        # 2. 遍历任务，处理记录逻辑
        for task in tasks:
            task_content = task.get("task_content")
            time_iso = task.get("time_iso")
            location_expression = task.get("location_expression")
            needs_weather = True

            if not task_content or not time_iso:
                continue

            # 时间解析 - 修复时间解析逻辑
            try:
                print(f"原始时间字符串: {time_iso}")
                # 直接解析ISO格式时间
                reminder_dt = datetime.fromisoformat(time_iso)
                print(f"解析后的时间: {reminder_dt}")
            except ValueError as e:
                print(f"时间解析失败: {e}, 时间字符串: {time_iso}")
                # 尝试其他解析方式
                try:
                    # 尝试去掉时区信息再解析
                    if 'Z' in time_iso:
                        time_iso = time_iso.replace('Z', '')
                    elif '+' in time_iso:
                        time_iso = time_iso.split('+')[0]
                    reminder_dt = datetime.fromisoformat(time_iso)
                    print(f"二次解析后的时间: {reminder_dt}")
                except ValueError as e2:
                    print(f"二次时间解析失败: {e2}")
                    # 使用当前时间作为备用
                    reminder_dt = datetime.now().replace(hour=12, minute=0, second=0, microsecond=0)
                    print(f"使用备用时间: {reminder_dt}")
            
            # 天气查询（如果需要）
            weather_info = "（无天气信息）"
            if needs_weather:
                if location_expression:
                    location = "120.1551,30.2741"  # 默认杭州经纬度
                    try:
                        location = get_location_coordinates(location_expression)
                        print(f"地点 '{location_expression}' 的坐标: {location}")
                        
                        target_date_str = reminder_dt.strftime('%Y-%m-%d')
                        print(f"查询天气日期: {target_date_str}")
                        
                        weather_data = weather_client.get_weather_by_date(location, target_date_str, days='15d')
                        if weather_data:
                            weather_info = (
                                f"{weather_data.get('textDay', '未知')}，"
                                f"{weather_data.get('tempMin', '未知')}°C~{weather_data.get('tempMax', '未知')}°C，"
                                f"风速：{weather_data.get('windSpeedDay', '未知')} km/h，"
                                f"湿度：{weather_data.get('humidity', '未知')}%"
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
            
            # 添加到返回结果
            results.append({
                "task_content": task_content,
                "time": reminder_dt.strftime('%Y-%m-%d %H:%M'),
                "location": location_expression or "无地点信息",
                "weather": weather_info
            })

        # 获取所有任务
        all_tasks = get_all_tasks()
        
        return jsonify({
            'success': True,
            'message': f'✅ 成功添加 {len(results)} 个任务',
            'new_tasks': results,
            'all_tasks': all_tasks
        })

    except Exception as e:
        return jsonify({'error': f'服务器错误: {str(e)}'}), 500

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    try:
        tasks = get_all_tasks()
        return jsonify({'tasks': tasks})
    except Exception as e:
        return jsonify({'error': f'获取任务失败: {str(e)}'}), 500
    
# ...existing code...
@app.route('/api/delete-task', methods=['POST'])
def delete_task():
    try:
        data = request.get_json()
        task_id = data.get('task_id')
        if task_id is None:
            return jsonify({'error': '缺少任务ID'}), 400
        try:
            task_id = int(task_id)
        except (ValueError, TypeError):
            return jsonify({'error': '任务ID格式错误'}), 400

        # 查询要删除的任务内容和时间
        conn = sqlite3.connect('tasks.db')
        c = conn.cursor()
        c.execute('SELECT task_content, reminder_time FROM tasks WHERE id = ?', (task_id,))
        row = c.fetchone()
        conn.close()
        if not row:
            return jsonify({'error': '任务不存在'}), 404
        task_content, reminder_time = row
        # 格式化时间为ISO
        if isinstance(reminder_time, str):
            try:
                reminder_time = datetime.fromisoformat(reminder_time)
            except Exception:
                pass
        time_iso = reminder_time.strftime('%Y-%m-%dT%H:%M:%S') if isinstance(reminder_time, datetime) else str(reminder_time)

        # 删除数据库任务
        success = delete_task_by_id(task_id)
        # 删除markdown任务
        delete_task_from_markdown(task_content, time_iso)

        if success:
            all_tasks = get_all_tasks()
            return jsonify({'success': True, 'message': '任务已删除', 'all_tasks': all_tasks})
        else:
            return jsonify({'error': '删除失败'}), 500
    except Exception as e:
        return jsonify({'error': f'服务器错误: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)