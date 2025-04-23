import win32com.client as win32
import os
from pyhwpx import Hwp

def convert_hwp_to_pdf(hwp_path, output_pdf_path):
    hwp = win32.gencache.EnsureDispatch("HWPFrame.HwpObject")  # 한글 프로그램 자동 실행
    hwp.XHwpWindows.Item(0).Visible = False  # 한글창 보이게 할지 (안 보이게 하려면 False)

    # 문서 열기 구문 - 보안 확인 없이 열기
    hwp.Open(hwp_path, "HWP", "forceopen:true")
    
    hwp.SaveAs(output_pdf_path, "PDF")  # 확장자는 자동으로 붙여줌
    hwp.Quit()

    print(f"✅ 변환 완료: {output_pdf_path}")

def remove_hwp(hwp_path):
    os.remove(hwp_path)
    print(f"✅ 삭제 완료: {hwp_path}")


base_url = "C:\\Users\\user\\OneDrive\\Desktop\\피오\\기업마당\\"

file_list = os.listdir(base_url)

for hwp_file_name in file_list:
    if hwp_file_name.endswith(".hwp"):

        hwp_file = base_url + hwp_file_name
        pdf_output = base_url + hwp_file_name + ".pdf"

        # HWP파일 PDF로 변환 함수
        convert_hwp_to_pdf(hwp_file, pdf_output)

        # 변환 완료된 후 HWP파일 삭제 함수
        remove_hwp(hwp_file)
