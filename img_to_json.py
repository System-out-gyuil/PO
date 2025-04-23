import os
from tqdm import tqdm
from PIL import Image
import numpy as np
from paddleocr import PaddleOCR
import re
from langchain_openai import ChatOpenAI
from config import OPEN_AI_API_KEY

api_key = OPEN_AI_API_KEY

# PaddleOCR 초기화 (한글 + 영어 지원, 방향 보정 포함)
ocr = PaddleOCR(use_angle_cls=True, lang='korean')

# 경로 설정
base_url = "C:\\Users\\user\\OneDrive\\Desktop\\피오\\기업마당\\"
file_list = os.listdir(base_url)

# 정제 함수
def clean_text(text):
    # 특수문자 정리 + 이상한 영어 조합 제거
    text = re.sub(r'[a-zA-Z]{2,}', '', text)  # 긴 영문 제거
    text = re.sub(r'[^\uAC00-\uD7A3\s0-9~\.\-\[\]\(\)]', '', text)  # 한글/숫자/기호만 남김
    text = re.sub(r'\s+', ' ', text)  # 다중 공백 제거
    text = text.strip()
    return text

# 날짜 형식 정제 (예: 20250414 → 2025.04.14)
def fix_dates(text):
    return re.sub(r'(\d{4})(\d{2})(\d{2})', r'\1.\2.\3', text)

# OCR 실행
for file_name in tqdm(file_list):
    file_path = os.path.join(base_url, file_name)

    if not os.path.isfile(file_path):
        continue

    if file_name.lower().endswith((".jpg", ".png")):
        # try:
            image = Image.open(file_path)
            image_np = np.array(image)

            result = ocr.ocr(image_np, cls=True)

            print(f"\n===== {file_name} 결과 (정제 후) =====")
            full_text = []

            for line in result[0]:
                raw = line[1][0]
                cleaned = fix_dates(clean_text(raw))
                if cleaned:
                    full_text.append(cleaned)

            user_input = "아래 내용을 다음 항목에 맞게 요약해줘. 지역, 가능업종(제조업, 서비스업, 요식업, IT, 도소매, 건설업, 무역업,운수업,농수산업,미디어,기타 중 하나) , 수출실적여부(예/아니요), 지원규모, 모집기간, 핵심키워드 5개,공고내용 300자 요약해서 json 형식으로 만들어줘줘 "

            for text in full_text:
                user_input += text

            llm = ChatOpenAI(
                temperature=0,
                model_name='gpt-4o-mini',
                openai_api_key=api_key
            )

            response = llm.invoke(user_input)
            print(response.content)

            # 문단 기준으로 정리해 출력
        #     for i, line in enumerate(full_text):
        #         if len(line) < 5:
        #             continue
        #         if any(keyword in line for keyword in ["사업기간", "접수", "지원", "제공", "상담", "컨설팅", "바이어"]):
        #             print(f"\n🟩 {line}")
        #         else:
        #             print(f"  - {line}")

        # except Exception as e:
        #     print(f"에러 발생: {file_path} - {e}")
