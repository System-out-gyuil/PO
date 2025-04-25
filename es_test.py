from elasticsearch import Elasticsearch
import json

# Elasticsearch 연결
es = Elasticsearch("http://localhost:9200", verify_certs=False)
index_name = "support_projects"

# 지역 변환 매핑
region_map = {
    "서울": "서울특별시",
    "부산": "부산광역시",
    "대구": "대구광역시",
    "인천": "인천광역시",
    "광주": "광주광역시",
    "대전": "대전광역시",
    "울산": "울산광역시",
    "세종": "세종특별자치시",
    "경기": "경기도",
    "강원": "강원도",
    "충북": "충청북도",
    "충남": "충청남도",
    "전북": "전라북도",
    "전남": "전라남도",
    "경북": "경상북도",
    "경남": "경상남도",
    "제주": "제주특별자치도"
}

# 인덱스 삭제 및 재생성 (매핑 포함)
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
                    "핵심키워드":   {"type": "text"},
                    "공고내용":     {"type": "text"}
                }
            }
        }
    )
except Exception as e:
    print("❌ 인덱스 관련 오류:", e)

# JSONL 파일 열기 및 업로드
with open("C:/Users/user/OneDrive/Desktop/피오/json/parsed_support_projects_3.json", "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        try:
            data = json.loads(line)

            # 모집시작일 처리
            if data.get("모집기간").get("모집시작일") == "":
                data["모집기간"]["모집시작일"] = "1111-12-31"

            # 모집종료일 처리
            if data.get("모집기간").get("모집종료일") == "":
                data["모집기간"]["모집종료일"] = "9999-12-31"

            region = data.get("지역", "")

            # 지역이 리스트일 경우
            if isinstance(region, list):
                converted = []

                for r in region:
                    if r in region_map:
                        converted.append(region_map[r])
                    else:
                        converted.append(r)  # 변환 불가 시 원본 유지

                data["지역"] = ", ".join(converted)  # 문자열로 변환

            elif isinstance(region, str):
                if region in region_map:
                    data["지역"] = region_map[region]


            # 지원규모 처리 (dict → 문자열 변환)
            if isinstance(data.get("지원규모"), dict):
                data["지원규모"] = json.dumps(data["지원규모"], ensure_ascii=False)

            # 지원자격 처리 (dict → 문자열 변환)
            if isinstance(data.get("지원자격"), dict):
                data["지원자격"] = json.dumps(data["지원자격"], ensure_ascii=False)

            es.index(index=index_name, id=i, body=data)
            print(f"✅ {i}번째 문서 업로드 성공")

        except Exception as e:
            print(f"❌ {i}번째 문서 업로드 실패:", e)
