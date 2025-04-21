from langchain_openai import ChatOpenAI
from PyPDF2 import PdfReader
import olefile
import win32com.client as win32
import os
import json
from tqdm import tqdm
import pandas as pd

base_url = "C:\\Users\\user\\OneDrive\\Desktop\\피오\\기업마당\\"
api_key = ""
result_list = []
result_json = []
for_excel = []

#  경로 내 모든 파일 리스트 가져오기기
file_list = os.listdir(base_url)

for file_name in tqdm(file_list):
    # 모든 파일 리스트에서 pdf 파일만 가져오기
    if file_name.endswith(".pdf"):
        # 파일 경로 생성
        file_path = base_url + file_name

        # pdf 파일 읽기
        pdfReader = PdfReader(file_path)
        
        user_input = "아래 내용을 다음 항목에 맞게 요약해줘. 지역, 가능업종(제조업, 서비스업, 요식업, IT, 도소매, 건설업, 무역업,운수업,농수산업,미디어,기타), 수출실적여부(예/아니요), 지원규모, 모집기간, 핵심키워드 5개,공고내용 300자 요약해서 json 형식으로 만들어줘줘 "

        for page in pdfReader.pages:
          user_input += page.extract_text()

        llm = ChatOpenAI(
            temperature=0,
            model_name='gpt-4o-mini',
            openai_api_key=api_key
        )

        response = llm.invoke(user_input)
        print(response.content)

        result_list.append(response.content)

print(result_list[0])

for result in result_list:
    
    
    result = result.replace("```json", "").replace("```", "").replace("\n", "").replace("\"", "").replace("   ", "")

    result_json.append({"messages" : [
                        {"role" : "system", "content" : "너는 국가 지원사업 안내 전문가야. 지원사업의 다양한 내용을 안내할 수 있어야해."}, 
                        # {"role" : "user", "content" : "나에게 필요한 국가 지원사업을 알려줘"},
                        {"role" : "assistant", "content" : result}
                      ]})

# print(result_json)

with open("C:\\Users\\user\\OneDrive\\Desktop\\피오\\json_test\\result10.json", 'w', encoding='utf-8') as f:
    json.dump(result_json, f, indent=4, ensure_ascii=False)

