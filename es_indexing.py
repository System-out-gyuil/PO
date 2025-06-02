from elasticsearch import Elasticsearch
import json
from config import ELASTICSEARCH_API_KEY

es = Elasticsearch(
    "https://0e0f4480a93d4cb78455e070163e467d.us-central1.gcp.cloud.es.io:443",
    api_key=ELASTICSEARCH_API_KEY
)
index_name = "po_index"
json_url = "C:/Users/user/Desktop/po/Data_json/2025_05_06_1074.json"

region_map = {
    "서울": "서울특별시", 
    "경기": "경기도", 
    "인천": "인천광역시", 
    "부산": "부산광역시", 
    "대구": "대구광역시", 
    "광주": "광주광역시",
    "대전": "대전광역시", 
    "울산": "울산광역시", 
    "충북": "충청북도", 
    "충남": "충청남도", 
    "전북": "전라북도", 
    "전남": "전라남도", 
    "경북": "경상북도",
    "경남": "경상남도", 
    "세종": "세종특별자치시", 
    "강원": "강원특별자치도",
    "제주": "제주특별자치도"
}

# 인덱스 삭제 후 재생성
try:
    if es.indices.exists(index=index_name):
        es.indices.delete(index=index_name)

    es.indices.create(
        index=index_name,
        body={
            "mappings": {
                "properties": {
                    "공고명":        {"type": "text"},
                    "지역":         {"type": "text"},
                    "가능업종":     {"type": "text"},
                    "수출실적여부": {"type": "text"},
                    "지원규모":     {"type": "text"},
                    "모집시작일":   {"type": "date"},
                    "모집종료일":   {"type": "date"},
                    "지원자격":     {"type": "text"},
                    "사업기간(업력)": {"type": "text"},
                    "수출여부":     {"type": "text"},
                    "매출규모":     {"type": "text"},
                    "직원수":       {"type": "text"},
                    "핵심키워드":   {"type": "text"},
                    "공고내용 요약": {"type": "text"}
                }
            }
        }
    )
except Exception as e:
    print("❌ 인덱스 초기화 실패:", e)

# 문서 업로드
with open(json_url, "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        try:
            data = json.loads(line) 

            # 모집기간 처리
            모집기간 = data.get("모집기간", {})
            data["모집시작일"] = 모집기간.get("모집시작일") or "0000-01-01"
            data["모집종료일"] = 모집기간.get("모집종료일") or "9999-12-31"

            # 사업기간 key명 변환
            data["사업기간"] = data.get("사업기간(업력)", "")

            # 지역 변환
            region = data.get("지역", "")
            if isinstance(region, list):
                data["지역"] = ", ".join([region_map.get(r, r) for r in region])
            elif isinstance(region, str):
                data["지역"] = region_map.get(region, region)

            # 문자열화가 필요한 필드들
            for field in ["지원규모", "지원자격"]:
                if isinstance(data.get(field), dict):
                    data[field] = json.dumps(data[field], ensure_ascii=False)

            # 리스트를 문자열로 변환할 필드들
            for field in ["가능업종", "핵심키워드", "사업기간", "매출규모"]:
                if isinstance(data.get(field), list):
                    data[field] = ", ".join(data[field])

            # 누락된 텍스트 필드 처리
            for field in ["수출여부", "직원수", "공고내용 요약"]:
                if not data.get(field):
                    data[field] = ""

            # 업로드
            es.index(index=index_name, id=i, body=data)
            print(f"✅ {i+1}번째 문서 업로드 성공")

        except Exception as e:
            print(f"❌ {i+1}번째 문서 업로드 실패:", e)
