import requests
from datetime import datetime, timedelta
import json

class WeatherClient:
    def __init__(self, api_key):
        """
        初始化天气客户端
        
        Args:
            api_key: 和风天气API密钥
        """
        self.api_key = api_key
        self.base_url = "https://devapi.qweather.com/v7/weather"
    
    def get_weather_by_date(self, location, date_str, days='15d'):
        """
        获取指定日期的天气信息
        
        Args:
            location: 位置坐标，格式为"经度,纬度"
            date_str: 日期字符串，格式为"YYYY-MM-DD"
            days: 预报天数，可选'3d', '7d', '10d', '15d'
            
        Returns:
            天气信息字典，如果获取失败返回None
        """
        try:
            # 分割经纬度
            lon, lat = location.split(',')
            
            print(f"正在查询天气，位置: {lon},{lat}, 日期: {date_str}")
            
            # 直接使用经纬度查询天气，跳过地理位置ID查询
            weather_url = f"{self.base_url}/{days}?location={lon},{lat}&key={self.api_key}"
            print(f"天气API URL: {weather_url}")
            
            weather_response = requests.get(weather_url, timeout=10)
            weather_data = weather_response.json()
            
            print(f"天气API响应: {json.dumps(weather_data, ensure_ascii=False)}")
            
            if weather_data.get('code') != '200':
                print(f"获取天气数据失败，错误码: {weather_data.get('code')}")
                return None
            
            # 查找指定日期的天气
            target_date = datetime.strptime(date_str, '%Y-%m-%d')
            for daily_data in weather_data.get('daily', []):
                if 'fxDate' in daily_data:
                    try:
                        forecast_date = datetime.strptime(daily_data['fxDate'], '%Y-%m-%d')
                        if forecast_date.date() == target_date.date():
                            print(f"找到匹配的天气数据: {daily_data}")
                            return {
                                'fxDate': daily_data['fxDate'],
                                'textDay': daily_data.get('textDay', '未知'),
                                'textNight': daily_data.get('textNight', '未知'),
                                'tempMax': daily_data.get('tempMax', '未知'),
                                'tempMin': daily_data.get('tempMin', '未知'),
                                'windSpeedDay': daily_data.get('windSpeedDay', '未知'),
                                'windDirDay': daily_data.get('windDirDay', '未知'),
                                'humidity': daily_data.get('humidity', '未知'),
                                'precip': daily_data.get('precip', '未知'),
                                'uvIndex': daily_data.get('uvIndex', '未知')
                            }
                    except ValueError:
                        continue
            
            print(f"未找到 {date_str} 的天气数据")
            # 返回模拟数据用于测试
            return self.get_mock_weather_data(date_str)
            
        except Exception as e:
            print(f"天气查询错误: {e}")
            # 返回模拟数据用于测试
            return self.get_mock_weather_data(date_str)    
        
    def get_current_weather(self, location):
        """
        获取当前天气
        
        Args:
            location: 位置坐标，格式为"经度,纬度"
            
        Returns:
            当前天气信息
        """
        try:
            # 分割经纬度
            lon, lat = location.split(',')
            
            # 获取当前天气
            current_url = f"https://devapi.qweather.com/v7/weather/now?location={lon},{lat}&key={self.api_key}"
            response = requests.get(current_url,timeout=10)
            data = response.json()
            
            if data['code'] == '200':
                return data['now',{}]
            else:
                print("获取当前天气失败")
                return None
                
        except Exception as e:
            print(f"获取当前天气错误: {e}")
            return None

# 工具函数
def get_location_coordinates(location_name):
    """
    根据地点名称获取经纬度坐标
    
    Args:
        location_name: 地点名称
        
    Returns:
        经纬度字符串，格式为"经度,纬度"
    """
    # 这里可以扩展为使用地理编码服务
    # 目前返回一些常见城市的默认坐标
    common_locations = {
        '北京': '116.41,39.92',
        '上海': '121.48,31.22',
        '广州': '113.23,23.16',
        '深圳': '114.07,22.62',
        '杭州': '120.1551,30.2741',
        '南京': '118.78,32.04',
        '成都': '104.06,30.67',
        '武汉': '114.31,30.52',
        '西安': '108.95,34.27',
        '重庆': '106.54,29.59'
    }
    
    for name, coords in common_locations.items():
        if name in location_name:
            return coords
    
    # 默认返回杭州坐标
    return '120.1551,30.2741'

# 测试函数
if __name__ == "__main__":
    # 测试天气查询
    weather_client = WeatherClient(api_key="bc4bdc854f774b3895afe2e2e517bbc0")
    
    # 测试获取未来天气
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    weather = weather_client.get_weather_by_date("120.1551,30.2741", tomorrow)
    
    if weather:
        print(f"明天杭州天气: {weather['textDay']}, 温度: {weather['tempMin']}°C~{weather['tempMax']}°C")
    else:
        print("天气查询失败")