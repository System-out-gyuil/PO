import pandas as pd
import os
import json

def road_json(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        datas = json.loads(f.read())
    return datas

datas = road_json("C:\\Users\\user\\OneDrive\\Desktop\\피오\\json_test\\result9.json")

content = datas[0]['messages'][1]['content']

# df = pd.DataFrame(content)

# print(df)

# df.to_excel("C:\\Users\\user\\OneDrive\\Desktop\\피오\\result9.xlsx", index=False)
import re
import ast

# 'key: value' 형식을 "key": "value" 형식으로 바꾸기
json_like_str = re.sub(r'(\w+):', r'"\1":', content)  # key에 큰따옴표 추가
json_like_str = re.sub(r':\s*\[([^\]]+)\]', lambda m: ': [' + ', '.join(f'"{x.strip()}"' for x in m.group(1).split(',')) + ']', json_like_str)
json_like_str = json_like_str.replace('\n', '').strip()

# 2. 문자열을 실제 딕셔너리로 변환
data_dict = ast.literal_eval(json_like_str)

# 3. pandas로 DataFrame 만들기
df = pd.DataFrame([data_dict])  # 하나의 dict를 한 행으로

# 4. 엑셀로 저장
df.to_excel("지원사업_정보.xlsx", index=False)

print("엑셀 파일로 저장 완료!")