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
base_url = "C:\\Users\\user\\Desktop\\po\\기업마당\\"
output_path = "C:\\Users\\user\\Desktop\\po\\Data_json\\2025_05_09_test_1.json"

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

        def clean(date_str, is_start=False):
            if not date_str or any(kw in date_str for kw in ["상시", "소진", "미정"]):
                return "0000-01-01" if is_start else "9999-12-31"
            match = re.search(r"\d{4}-\d{2}-\d{2}", date_str)
            return match.group(0) if match else date_str

        # 모집기간 내부 값을 직접 수정 (새 key 추가하지 않음)
        json_obj["모집시작일"] = clean(start, is_start=True)
        json_obj["모집종료일"] = clean(end)

        return json_obj

    except Exception as e:
        print(f"[ERROR] 날짜 정규화 실패: {e}")
        return json_obj

# GPT 기반 요약 및 JSON 저장 (JSON 파일로 저장)
def to_json(text, output_path):

    user_input = (
        "아래 텍스트는 정부 지원사업 공고문에서 추출된 실제 내용입니다. "
        "이 내용을 기반으로 허구 없이 정확하게 요약해줘. 추가적인 추론이나 가정은 하지 말고, 원문 기반으로만 작성해줘.\n\n"
        "※ 매우 중요: 선택 가능한 모든 기준에서 복수 선택이 가능하며, 해당하는 모든 항목을 반드시 포함해야 합니다.\n"
        "예를 들어, 사업기간이 3년 이상이면 '3~7년', '7년 이상'을 모두 선택하고, 매출규모가 1억 이상 10억 이하라면 '1~5억', '5~10억'을 모두 포함해야 합니다. 직원수가 1인 이상이라면 '1~4인', '5인 이상' 중 해당하는 모든 항목을 반드시 포함해야 합니다.\n\n"
        "만약 모든 항목이 포함된다면 \'무관\' 하나만 넣어줘"
        "📌 아래 항목들을 정확히 JSON 형식으로 추출해줘:\n"
        "- 공고명\n"
        "- 지역\n"
        "- 가능업종: 제조업, 서비스업, 요식업, IT, 도소매, 건설업, 무역업, 운수업, 농수산업, 미디어 (해당되는 모든 항목을 복수 선택)\n"
        "- 수출실적여부: 무관, 수출기업, 수출 희망 중 하나 이상 선택 (해당되는 모든 항목을 복수 선택)\n"
        "- 지원규모\n"
        "- 모집시작일: (형식: yyyy-mm-dd)\n"
        "- 모집종료일: (형식: yyyy-mm-dd)\n"
        "  ※ 모집시작일이 없다면 비워두고, 모집종료일에 연도가 없다면 2025로 간주\n"
        "- 지원자격\n"
        "- 사업기간(업력): 무관, 예비 창업, 1년 이하, 1~3년, 3~7년, 7년 이상 (해당되는 모든 항목을 복수 선택, 예: 업력이 3년 이상이면 '3~7년', '7년 이상'을 반드시 모두 포함)\n"
        "- 매출규모: 무관, 1억 이하, 1~5억, 5~10억, 10~30억, 30억 이상 (해당되는 모든 항목을 복수 선택, 예: 매출이 1억 이상 10억 이하라면 '1~5억', '5~10억'을 반드시 모두 포함)\n"
        "- 직원수: 무관, 1~4인, 5인 이상 (해당되는 모든 항목을 복수 선택, 예: 직원수가 1인 이상이라면 '1~4인', '5인 이상' 중 해당하는 모든 항목을 반드시 모두 포함)\n"
        "- 핵심키워드: 최대 5개, 반드시 array로. '중소기업', '소상공인'은 제외\n"
        "- 공고내용: 최소 450자 이상, 최대한 자세히 (500자 이상 권장)\n\n"
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
