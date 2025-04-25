import logging
# 경고 숨기기
logging.getLogger("pdfminer").setLevel(logging.ERROR)
logging.getLogger("PyPDF2").setLevel(logging.ERROR)

from langchain_openai import ChatOpenAI
import pdfplumber
import os
from tqdm import tqdm
import json
from config import OPEN_AI_API_KEY

api_key = OPEN_AI_API_KEY
base_url = "C:\\Users\\user\\OneDrive\\Desktop\\피오\\Train_data\\"
output_path = "C:\\Users\\user\\OneDrive\\Desktop\\피오\\json_test\\train_data_7.jsonl"

file_list = os.listdir(base_url)

with open(output_path, 'w', encoding='utf-8') as outfile:
    for file_name in tqdm(file_list):
        if file_name.endswith(".pdf"):
            file_path = os.path.join(base_url, file_name)

            # pdfplumber로 텍스트 추출
            extracted_text = ""
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        extracted_text += page_text + "\n"

            if not extracted_text.strip():
                print(f"❗ 텍스트가 추출되지 않은 파일: {file_name}")
                continue

            # 사용자 질문 구성
            user_input = (
                "아래 내용을 다음 항목에 맞게 요약해줘. 공고명, 지역, 가능업종(제조업, 서비스업, 요식업, IT, 도소매, 건설업, 무역업, 운수업, 농수산업, 미디어, 기타), "
                "수출실적여부(예/아니요), 지원규모, 모집기간, 핵심키워드 5개, 공고내용을 300자 요약해줘.\n\n"
            ) + extracted_text

            llm = ChatOpenAI(
                temperature=0.1,
                model_name='gpt-4o-mini',
                openai_api_key=api_key
            )

            response = llm.invoke(user_input)
            content = response.content.strip()
            content = content.replace("```json", "").replace("```", "").replace("\n", "").strip()

            json_obj = {
                "messages": [
                    {"role": "system", "content": "너는 국가 지원사업 안내 전문가야. 지원사업의 다양한 내용을 안내할 수 있어야해."},
                    {"role": "user", "content": "나에게 필요한 국가 지원사업을 알려줘"},
                    {"role": "assistant", "content": content}
                ]
            }

            outfile.write(json.dumps(json_obj, ensure_ascii=False) + "\n")
