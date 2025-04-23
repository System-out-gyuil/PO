from elasticsearch import Elasticsearch
import json

# 인증 생략 및 보안 관련 오류 방지
es = Elasticsearch("http://localhost:9200", verify_certs=False)

index_name = "support_projects"

# 인덱스 존재 여부 확인 및 삭제 → 생성
try:
    if es.indices.exists(index=index_name):
        es.indices.delete(index=index_name)
    es.indices.create(index=index_name)
except Exception as e:
    print("❌ 인덱스 관련 오류:", e)

# 문서 업로드
with open("C:/Users/user/OneDrive/Desktop/피오/json_test/train_data_7.jsonl", "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        data = json.loads(line)
        content = data["messages"][-1]["content"]
        try:
            es.index(index=index_name, id=i, body={"text": content})
            print(f"✅ {i}번째 문서 업로드 성공")
        except Exception as e:
            print(f"❌ {i}번째 문서 업로드 실패:", e)
