import requests
from config import BIZINFO_API_KEY

url = "https://www.bizinfo.go.kr/uss/rss/bizinfoApi.do"

params = {
    "crtfcKey": BIZINFO_API_KEY,  # ← 본인 키 사용
    "dataType": "json",
    "searchCnt": 10,
    "pageUnit": 10,
    "pageIndex": 1
}

try:
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()

    items = data.get("jsonArray", [])  # ← 여기가 핵심
    for item in items:
        print(f"{item.get('pblancNm')}")
except requests.exceptions.RequestException as e:
    print("요청 실패:", e)