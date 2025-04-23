import requests
import uuid
import time
import json
from langchain_openai import ChatOpenAI
from config import OPEN_AI_API_KEY, NAVER_CLOUD_CLOVA_OCR_API_KEY

api_key = OPEN_AI_API_KEY
secret_key = NAVER_CLOUD_CLOVA_OCR_API_KEY
api_url = 'https://al8xehpqhk.apigw.ntruss.com/custom/v1/41183/6e746e62807a38c39a5706cf9e7b11a454bfacc8608dd7dbaa9e1c8ab32ddf93/general'
image_file = 'C:\\Users\\user\\OneDrive\\Desktop\\피오\\기업마당\\1541_2025 충북 디지털무역종합지원센터(deXter) 활용 화상상담회 참여기업 모집공고 (2차).png'

request_json = {
    'images': [
        {
            'format': 'png',
            'name': 'demo'
        }
    ],
    'requestId': str(uuid.uuid4()),
    'version': 'V1',
    'timestamp': int(round(time.time() * 1000))
}

payload = {'message': json.dumps(request_json).encode('UTF-8')}
files = [
  ('file', open(image_file,'rb'))
]
headers = {
  'X-OCR-SECRET': secret_key
}

response = requests.request("POST", api_url, headers=headers, data = payload, files = files)

# print(response.text.encode('utf8'))

full_text = ''

# 원래 코드는 print(response.text.encode('utf8'))이지만 수정
for i in response.json()['images'][0]['fields']:
    text = i['inferText']
    # print(text)
    full_text += text

# print(full_text)

user_input = "아래 내용을 다음 항목에 맞게 요약해줘. 지역, 가능업종(제조업, 서비스업, 요식업, IT, 도소매, 건설업, 무역업,운수업,농수산업,미디어,기타), 수출실적여부(예/아니요), 지원규모, 모집기간, 핵심키워드 5개,공고내용 300자 요약해서 json 형식으로 만들어줘줘 "

user_input += full_text

llm = ChatOpenAI(
    temperature=0,
    model_name='gpt-4o-mini',
    openai_api_key=api_key
)

response = llm.invoke(user_input)
print(response.content)