from datetime import datetime
import requests

class WeatherClient:
    def __init__(self, api_key, host='n56cdncx2r.re.qweatherapi.com'):
        self.api_key = api_key
        self.host = host

    def get_forecast(self, location: str, days: str = '15d', lang: str = 'zh', unit: str = 'm') -> dict:
        url = f'https://{self.host}/v7/weather/{days}?location={location}&lang={lang}&unit={unit}'
        headers = {
            'X-QW-Api-Key': self.api_key
        }

        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise Exception(f"请求失败：{response.status_code} - {response.text}")

        return response.json()

    def get_weather_by_date(self, location: str, target_date: str, days: str = '15d') -> dict:
        forecast = self.get_forecast(location, days=days)
        target = datetime.strptime(target_date, '%Y-%m-%d').date()

        for day in forecast.get('daily', []):
            fx_date = datetime.strptime(day['fxDate'], '%Y-%m-%d').date()
            if fx_date == target:
                return day

        raise ValueError(f"未找到 {target_date} 的天气数据，请确认日期是否在预报范围内。")
