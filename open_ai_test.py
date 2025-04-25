from elasticsearch import Elasticsearch
from datetime import datetime
import json

# 사용자 조건
region = "경북"
industry = "제조업"
user_input = f"나는 {region}에서 {industry}을 하고있어, 나에게 맞는 지원 사업을 추천해줘"

# Elasticsearch 연결
es = Elasticsearch("http://localhost:9200", verify_certs=False)
index_name = "support_projects"

# 검색 함수
def search_support_projects(region: str, industry: str, sample_size: int = 20):
    query = {
        "query": {
            "bool": {
                "must": [
                    { "match": { "가능업종": industry } }
                ],
                "should": [
                    { "match_phrase": { "지역": region } },
                    { "wildcard": { "지역": f"*{region}*" } },
                    { "match_phrase": { "공고내용": region } },
                    { "wildcard": { "공고내용": f"*{region}*" } }
                ],
                "minimum_should_match": 1
            }
        }
    }

    res = es.search(index=index_name, body=query, size=sample_size)
    
    return [hit["_source"] for hit in res["hits"]["hits"]]

# 날짜 유효성 검사
def is_valid_date_range(start_date: str, end_date: str) -> bool:
    try:
        today = datetime.today().date()
        if not end_date or end_date == "9999-12-31":
            return True
        return datetime.strptime(end_date, "%Y-%m-%d").date() >= today
    except:
        return False

# 날짜 포맷
def format_date_range(start: str, end: str) -> str:
    if not end or end == "9999-12-31":
        return "사업비 소진 시까지 (상시접수)"
    if not start or start == "1111-12-31":
        return f"~ {end}"
    return f"{start} ~ {end}"

# 정렬 기준: 모집 종료일이 빠른 순 (상시모집은 맨 뒤)
def sort_key(project):
    try:
        end_date = project.get("모집기간", {}).get("모집종료일", "")
        if end_date == "9999-12-31":
            return datetime.max
        return datetime.strptime(end_date, "%Y-%m-%d")
    except:
        return datetime.max

# 문서 검색 및 정렬
matched_projects = sorted(search_support_projects(region, industry), key=sort_key)

# 결과 출력
count = 1  # 추천 번호 카운터
for project in matched_projects:
    if is_valid_date_range(project.get("모집기간").get("모집시작일"), project.get("모집기간").get("모집종료일")):
        print(f"\n========== ✅ 추천 {count} ==========")
        print(f"""
📢 지원사업 추천 정보

📝 공고명: {project['공고명']}
📍 지역: {project['지역']}
🏭 업종: {', '.join(project['가능업종'])}
🚢 수출 실적 여부: {project['수출실적여부']}
💰 지원 규모: {project['지원규모']}
👤 지원 자격: {project['지원자격']}
📆 모집 기간: {format_date_range(project['모집기간']['모집시작일'], project['모집기간']['모집종료일'])}
🔑 핵심 키워드: {', '.join(project['핵심키워드'])}

📄 공고 내용 요약:
{project['공고내용']}
""")
        count += 1

# 유효한 결과가 하나도 없을 경우
if count == 1:
    print("❗ 조건에 맞는 결과가 없습니다.")
