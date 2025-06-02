import requests
import pandas as pd
from config import BIZINFO_API_KEY

# API 요청
url = "https://www.bizinfo.go.kr/uss/rss/bizinfoApi.do"
params = {
    "crtfcKey": BIZINFO_API_KEY,
    "dataType": "json",
    "searchCnt": 500,
    "pageUnit": 500,
    "pageIndex": 1
}

items = []

try:
    response = requests.get(url, params=params, timeout=1000)
    response.raise_for_status()
    items = response.json().get("jsonArray", [])
except Exception as e:
    print(f"Error: {e}")

# inqireCo 기준 내림차순 정렬
top_items = sorted(items, key=lambda x: int(x.get("inqireCo", 0)), reverse=True)

# 엑셀에 저장할 필드 선택 (원하는 필드만 추출)
records = []
for item in top_items:
    records.append({
        "공고명": item.get("pblancNm"),
        "조회수": item.get("inqireCo"),
        "공고ID": item.get("pblancId"),
        "접수기간": item.get("reqstBeginEndDe"),
        "수행기관": item.get("excInsttNm"),
        "지원대상": item.get("trgetNm"),
        "요약": item.get("bsnsSumryCn"),
        "첨부파일": item.get("fileNm"),
        "공고파일URL": item.get("flpthNm"),
        "등록일시": item.get("creatPnttm")
    })

# DataFrame으로 변환 후 Excel 저장
df = pd.DataFrame(records)
df.to_excel("bizinfo_0520_0530.xlsx", index=False, engine='openpyxl')

print("✅ 파일 저장 완료")
