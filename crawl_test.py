import requests
from bs4 import BeautifulSoup

# 1. URL 설정
url = 'https://www.bizinfo.go.kr/web/lay1/bbs/S1T122C128/AS/74/view.do?pblancId=PBLN_000000000108954'

# 2. 요청 보내기
response = requests.get(url)

# 3. HTML 파싱
soup = BeautifulSoup(response.text, 'html.parser')

# 4. 원하는 요소 찾기 (예: 모든 제목 h2 태그)
titles = soup.find_all('a')

# 5. 출력
for title in titles:
    print(title.text.strip())
