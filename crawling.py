from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time

# chromedriver 경로
CHROMEDRIVER_PATH = "C:/Users/user/Desktop/po/Code/chromedriver.exe"

# Chrome 옵션 설정
options = webdriver.ChromeOptions()
options.add_argument('--headless=chrome')  # GUI 없이 실행
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

# WebDriver 실행
service = Service(executable_path=CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service, options=options)

# 페이지 접속
url = "https://www.bizinfo.go.kr/web/lay1/bbs/S1T122C128/AS/74/view.do?pblancId=PBLN_000000000108952"
driver.get(url)
time.sleep(1)

# 현재 페이지 HTML 파싱
html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')

# iframe 중 PDF viewer로 보이는 것 추출 (보통 src에 pdf 또는 viewer 포함됨)
iframe_tags = soup.find_all("iframe")
pdf_iframes = [iframe for iframe in iframe_tags if "pdf" in iframe.get("src", "").lower() or "viewer" in iframe.get("src", "").lower()]

# 결과 출력
if pdf_iframes:
    for idx, iframe in enumerate(pdf_iframes, 1):
        print(f"📄 PDF iframe {idx} ▶ src: {iframe.get('src')}")
else:
    print("❌ PDF iframe을 찾을 수 없습니다.")

# 브라우저 종료
driver.quit()
