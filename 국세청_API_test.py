import requests
import json

api_key = "lRyvfpVqTGofvOWVZ77vanxSvQyUWz6sfaJmcKYtsn22ZyfRwJBm3NvyJy9xE309Cbs5MqmM1%2BItQIU2xGg8DQ%3D%3D"

url = f"https://api.odcloud.kr/api/nts-businessman/v1/validate?serviceKey={api_key}&returnType=json"

# ✅ 반드시 'businesses' 키로 감싼 리스트 안에 딕셔너리 형태로
payload = {
    "businesses": [
        {
            "b_no": "8475900799",
            "start_dt": "20241216",
            "p_nm": "김솔",

        }
    ]
}

headers = {
    "Content-Type": "application/json"
}

response = requests.post(url, headers=headers, data=json.dumps(payload))

if response.status_code == 200:
    result = response.json()
    print(json.dumps(result, indent=2, ensure_ascii=False))
else:
    print("요청 실패:", response.status_code, response.text)
