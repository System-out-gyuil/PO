import olefile

f = olefile.OleFileIO('C:\\Users\\user\\OneDrive\\Desktop\\피오\\기업마당\\1506_러시아(모스크바ㆍ상트) 시장개척단 파견 참가기업 모집 공고.hwp')  
encoded_text = f.openstream('PrvText').read() 
decoded_text = encoded_text.decode('utf-16')  

print(decoded_text)