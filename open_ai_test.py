from langchain_openai import ChatOpenAI
from elasticsearch import Elasticsearch
import json
from config import OPEN_AI_API_KEY

# 🔑 API 키
api_key = OPEN_AI_API_KEY

# 🧑 사용자 입력
user_input = "나는 경주에서 IT업을 하고있어, 나에게 필요한 국가 지원사업을 알려줘."

# 🔍 Elasticsearch 연결
es = Elasticsearch("http://localhost:9200", verify_certs=False)
index_name = "support_projects"

# 📋 Function Calling 스펙 정의
functions = [
    {
        "name": "get_support_info",
        "description": "국가 지원사업 정보를 반환",
        "parameters": {
            "type": "object",
            "properties": {
                "공고명": {"type": "string"},
                "지역": {"type": "string"},
                "가능업종": {"type": "string"},
                "수출실적여부": {"type": "string"},
                "지원규모": {"type": "string"},
                "모집기간": {"type": "string"},
                "핵심키워드": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 1,
                    "maxItems": 5
                },
                "공고내용": {"type": "string"}
            },
            "required": ["공고명", "지역", "가능업종", "수출실적여부", "지원규모", "모집기간", "핵심키워드", "공고내용"]
        }
    }
]

# 🔍 Elasticsearch 검색 함수
def search_support_projects(user_query: str, top_k: int = 3):
    query = {
        "query": {
            "match": {
                "text": user_query
            }
        }
    }
    res = es.search(index=index_name, body=query, size=top_k)
    return [hit["_source"]["text"] for hit in res["hits"]["hits"]]

# 🧠 LLM 객체 생성 (GPT + Function Call)
llm = ChatOpenAI(
    temperature=0,
    model_name='gpt-4o-mini',  # 또는 fine-tuned 모델
    openai_api_key=api_key,
    model_kwargs={
        "functions": functions,
        "function_call": {"name": "get_support_info"}
    }
)

# 1. 🔍 문서 검색
retrieved_docs = search_support_projects(user_input)

# 2. 🔗 검색 결과를 context로 연결
context = "\n\n".join(retrieved_docs)

# 3. 🤖 GPT에 전달할 프롬프트 구성
final_prompt = f"""
사용자 조건: {user_input}

다음은 검색된 실제 지원사업입니다:

{context}

위 정보를 참고해서 사용자에게 적절한 지원사업을 응답해줘.
지역과 업종을 중점으로 찾아줘
"""

# 4. 🚀 GPT 호출
response = llm.invoke(final_prompt)

# 5. 🧾 JSON → 보기 좋은 자연어 변환 함수
def format_result(raw_json: str):
    parsed = json.loads(raw_json)
    return f"""
📢 지원사업 추천 정보

📝 공고명: {parsed['공고명']}
📍 지역: {parsed['지역']}
🏭 업종: {parsed['가능업종']}
🚢 수출 실적 여부: {parsed['수출실적여부']}
💰 지원 규모: {parsed['지원규모']}
📆 모집 기간: {parsed['모집기간']}
🔑 핵심 키워드: {', '.join(parsed['핵심키워드'])}

📄 공고 내용 요약:
{parsed['공고내용']}
"""

# 6. 📤 결과 출력
arguments = response.additional_kwargs.get("function_call", {}).get("arguments")
if arguments:
    print(format_result(arguments))
else:
    print("❗ 함수 호출 결과가 없습니다.")
