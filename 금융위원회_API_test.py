import requests
import json

SERVICE_KEY = "lRyvfpVqTGofvOWVZ77vanxSvQyUWz6sfaJmcKYtsn22ZyfRwJBm3NvyJy9xE309Cbs5MqmM1+ItQIU2xGg8DQ=="

# ✅ 기본 요청 파라미터
params = {
    'serviceKey': SERVICE_KEY,
    'pageNo': 1,
    'numOfRows': 10,
    'resultType': 'json',
    'crno': '120111-1435339'
}


url = 'https://apis.data.go.kr/1160100/service/GetCorpBasicInfoService_V2/getCorpOutline_V2'

response = requests.get(url, params=params)

# ✅ 응답 확인
if response.status_code == 200:
    print(response.json())
else:
    print(f"요청 실패: {response.status_code}")
    print(response.text)