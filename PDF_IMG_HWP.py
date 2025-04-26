import logging
import win32com.client as win32
import requests
import uuid
import time
import json
import os
from pyhwpx import Hwp
from config import OPEN_AI_API_KEY, NAVER_CLOUD_CLOVA_OCR_API_KEY, NAVER_CLOUD_CLOVA_OCR_API_URL
from langchain_openai import ChatOpenAI
import pdfplumber
from tqdm import tqdm
from datetime import datetime
import shutil  # 추가
import re

# 경고 숨기기
logging.getLogger("pdfminer").setLevel(logging.ERROR)
logging.getLogger("PyPDF2").setLevel(logging.ERROR)

# 설정 값
api_key = OPEN_AI_API_KEY
secret_key = NAVER_CLOUD_CLOVA_OCR_API_KEY
api_url = NAVER_CLOUD_CLOVA_OCR_API_URL
base_url = "C:\\Users\\user\\OneDrive\\Desktop\\po\\기업마당\\"
output_path = "C:\\Users\\user\\OneDrive\\Desktop\\po\\Data_json\\2025_04_25_1313.json"

# GPT LLM 세팅
llm = ChatOpenAI(
    temperature=0,
    model_name='gpt-4o-mini',
    openai_api_key=api_key
)

# OCR 요청 생성
def clova_ocr(image_file, fmt):
    request_json = {
        'images': [{'format': fmt, 'name': 'demo'}],
        'requestId': str(uuid.uuid4()),
        'version': 'V1',
        'timestamp': int(round(time.time() * 1000))
    }
    payload = {'message': json.dumps(request_json).encode('UTF-8')}
    files = [('file', open(image_file, 'rb'))]
    headers = {'X-OCR-SECRET': secret_key}
    response = requests.post(api_url, headers=headers, data=payload, files=files)
    return response

# HWP -> PDF 변환
def convert_hwp_to_pdf(hwp_path, output_pdf_path):
    hwp = win32.gencache.EnsureDispatch("HWPFrame.HwpObject")
    hwp.XHwpWindows.Item(0).Visible = False
    hwp.RegisterModule("FilePathCheckDLL", "AutomationModule")
    hwp.Open(hwp_path, "HWP", "forceopen:true")
    hwp.SaveAs(output_pdf_path, "PDF")
    hwp.Quit()
    print(f"✅ 변환 완료: {output_pdf_path}")

def remove_hwp(hwp_path):
    os.remove(hwp_path)
    print(f"✅ 삭제 완료: {hwp_path}")

# 상시접수 및 날짜 파싱 보정
def normalize_dates(json_obj):
    try:
        start = json_obj.get("모집시작일", "")
        end = json_obj.get("모집종료일", "")

        today = datetime.today().strftime("%Y-%m-%d")

        def clean(date_str, is_start=False):
            if not date_str or "상시" in date_str or "소진" in date_str:
                return today if is_start else "9999-12-31"
            match = re.search(r"\d{4}-\d{2}-\d{2}", date_str)
            return match.group(0) if match else date_str

        json_obj["모집시작일"] = clean(start, is_start=True)
        json_obj["모집종료일"] = clean(end)

        return json_obj
    except Exception as e:
        print(f"[ERROR] 날짜 정규화 실패: {e}")
        return json_obj

# GPT 기반 요약 및 JSON 저장 (JSON 파일로 저장)
def to_json(text, output_path):
    user_input = (
        "아래 텍스트는 정부 공고문에서 추출된 실제 내용입니다. \
        이 내용을 기반으로 허구 없이 정확하게 요약해줘. 추가적인 추론이나 가정은 하지 말고, \
        원문 기반으로만 작성해줘. 각 항목은 다음과 같아.\n"
        "공고명, 지역, 가능업종(제조업, 서비스업, 요식업, IT, 도소매, 건설업, 무역업, 운수업, 농수산업, 미디어, 기타 등) 다중선택 가능,\n"
        "수출실적여부(수출기업/무관), 지원규모, 모집기간을 분석해서 모집시작일과 모집종료일(yyyy-mm-dd),\n"
        "만약 모집 시작일이 없다면 비워두고, 모집 종료일의 년도가 없다면 2025로 고정해서 써줘.\n"
        "지원자격도 넣어줘.\n"
        "핵심키워드 (5개 array)핵심 키워드엔 중소기업, 소상공인은 제외해줘, 공고내용 요약은 최대한 자세하게 써주고 500자에 가깝게 써줘 최소 450자 이상.\n"
        "정확히 JSON 형식으로 응답해줘.\n\n"
    ) + text

    response = llm.invoke(user_input)
    content = response.content.strip()
    print("[GPT 응답 원본]:", content)
    content = content.replace("```json", "").replace("```", "").strip()

    try:
        parsed = json.loads(content)
        parsed = normalize_dates(parsed)
        with open(output_path, 'a', encoding='utf-8') as outfile:
            json.dump(parsed, outfile, ensure_ascii=False)
            outfile.write("\n")
    except Exception as e:
        print("❌ JSON 변환 실패:", e)
        print(content)

# 전체 파일 처리
file_list = os.listdir(base_url)

# HWP -> PDF 변환 및 삭제
for file_name in tqdm(file_list):
    if file_name.endswith(".hwp"):
        hwp_path = os.path.join(base_url, file_name)
        pdf_output = hwp_path.replace(".hwp", ".pdf")
        convert_hwp_to_pdf(hwp_path, pdf_output)
        remove_hwp(hwp_path)


# 파일별 OCR 또는 PDF 텍스트 추출 후 요약
for file_name in tqdm(os.listdir(base_url)):
    file_path = os.path.join(base_url, file_name)
    full_text = ""

    try:
        if file_name.endswith(".png"):
            response = clova_ocr(file_path, 'png')
            for field in response.json()['images'][0]['fields']:
                full_text += field['inferText']

        elif file_name.endswith(".jpg"):
            response = clova_ocr(file_path, 'jpg')
            for field in response.json()['images'][0]['fields']:
                full_text += field['inferText']

        elif file_name.endswith(".pdf"):
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        full_text += page_text + "\n"

        if full_text.strip():
            to_json(full_text, output_path)
        else:
            print(f"❌ 텍스트 추출 실패: {file_name}")

    except Exception as e:
        print(f"❌ 오류 발생, 파일 이동: {file_name}, 오류: {e}")
        try:
            error_dir = r"C:\Users\user\OneDrive\Desktop\po\오류"
            os.makedirs(error_dir, exist_ok=True)  # 오류 폴더 없으면 생성
            shutil.move(file_path, os.path.join(error_dir, file_name))
        except Exception as move_error:
            print(f"❌ 파일 이동 실패: {file_name}, 오류: {move_error}")
