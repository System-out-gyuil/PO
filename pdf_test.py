import fitz  # PyMuPDF를 임포트

# 문서 열기
doc = fitz.open("C:\\Users\\user\\OneDrive\\Desktop\\피오\\기업마당\\1700_1. 모집 공고문.pdf")

# 첫 페이지의 텍스트 추출
page = doc.load_page(0)
text = page.get_text("text")

print(text)

# 문서 닫기
doc.close()