from elasticsearch import Elasticsearch, helpers
from board.models import BizInfo
from config import ELASTICSEARCH_API_KEY
from datetime import datetime

es = Elasticsearch(
    "https://0e0f4480a93d4cb78455e070163e467d.us-central1.gcp.cloud.es.io:443",
    api_key=ELASTICSEARCH_API_KEY
)

index_name = "po_index"

# ✅ 1. 인덱스 재생성 (옵션)
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
                "사업기간":     {"type": "text"},
                "수출여부":     {"type": "text"},
                "매출규모":     {"type": "text"},
                "직원수":       {"type": "text"},
                "핵심키워드":   {"type": "text"},
                "공고내용 요약": {"type": "text"}
            }
        }
    }
)

# ✅ 2. DB → Elasticsearch 변환
region_map = {
    "서울": "서울특별시", "경기": "경기도", "인천": "인천광역시",
    "부산": "부산광역시", "대구": "대구광역시", "광주": "광주광역시",
    "대전": "대전광역시", "울산": "울산광역시", "충북": "충청북도",
    "충남": "충청남도", "전북": "전라북도", "전남": "전라남도",
    "경북": "경상북도", "경남": "경상남도", "세종": "세종특별자치시",
    "강원": "강원특별자치도", "제주": "제주특별자치도"
}

actions = []

for i, item in enumerate(BizInfo.objects.all()):
    try:
        # 모집일 처리
        모집시작일 = item.reception_start.isoformat() if item.reception_start else "0000-01-01"
        모집종료일 = item.reception_end.isoformat() if item.reception_end else "9999-12-31"

        # 지역 정제
        region = item.region or ""
        if isinstance(region, str):
            region = region_map.get(region, region)

        doc = {
            "_index": index_name,
            "_id": item.pblanc_id,
            "_source": {
                "공고명": item.title,
                "지역": region,
                "가능업종": item.possible_industry or "",
                "수출실적여부": item.export_performance or "",
                "지원규모": item.revenue or "",
                "모집시작일": 모집시작일,
                "모집종료일": 모집종료일,
                "지원자격": item.target or "",
                "사업기간": item.business_period or "",
                "수출여부": item.export_performance or "",
                "매출규모": item.revenue or "",
                "직원수": item.employee_count or "",
                "핵심키워드": item.hashtag or "",
                "공고내용 요약": item.noti_summary or "",
            }
        }
        actions.append(doc)
    except Exception as e:
        print(f"❌ {i+1}번 항목 에러:", e)

# ✅ 3. Elasticsearch로 업로드
helpers.bulk(es, actions)
print(f"✅ 총 {len(actions)}개 DB 데이터를 Elasticsearch에 인덱싱 완료")
