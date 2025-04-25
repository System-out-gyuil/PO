#필요한 라이브러리를 임포트합니다.
import win32com.client
import os
import re

#한글 파일을 열기 위해 HWP변수에 함수를 저장합니다.
hwp = win32com.client.gencache.EnsureDispatch('HWPFrame.HwpObject')

#HWP변수에 한글 보안 모듈을 적용합니다.
hwp.RegisterModule('FilePathCheckDLL', 'SecurityModule')

#파일의 경로를 지정해줍니다.
getPath = "C:\\Users\\user\\OneDrive\\Desktop\\피오\\기업마당\\"
savePath = "C:\\Users\\user\\OneDrive\\Desktop\\피오\\기업마당\\"

#불러올 파일의 경로에 있는 hwp확장자를 가진 파일들의 리스트를 가져옵니다.
files = [f for f in os.listdir(getPath) if re.match('.*[.]hwp', f)]

#for문을 이용해 한글 파일을 PDF 파일로 바꾸는 코드를 반복 실행해줍니다.
#file이라는 변수에 files라는 리스트에 들어있는 변수를 순서대로 대입하게 됩니다.
for file in files:
    
    #지정한 경로에 있는 한글 파일을 열어줍니다.
    hwp.Open(os.path.join(getPath, file))

    #불러온 파일의 파일명과 확장자를 분리합니다.
    pre, ext = os.path.splitext(file)
    
    #아래에 작성할 설정값으로 프로그램을 실행해달라는 명령어입니다.
    hwp.HAction.GetDefault("FileSaveAs_S", hwp.HParameterSet.HFileOpenSave.HSet)

    #파일 저장시 확장자를 pdf로 지정합니다.
    hwp.HParameterSet.HFileOpenSave.filename = os.path.join(savePath, pre + ".pdf")
    
    #파일 저장시 포맷을 pdf로 설정합니다.
    hwp.HParameterSet.HFileOpenSave.Format = "PDF"
    
    #위에 작성한 설정값으로 프로그램을 실행해달라는 명령어입니다.
    hwp.HAction.Execute("FileSaveAs_S", hwp.HParameterSet.HFileOpenSave.HSet);


#한글 파일을 종료합니다.
hwp.Quit()