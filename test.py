from config import OPEN_AI_API_KEY
from langchain_openai import ChatOpenAI

api_key = OPEN_AI_API_KEY

# GPT LLM 세팅
llm = ChatOpenAI(
    temperature=0,
    model_name='gpt-4o',
    openai_api_key=api_key
)

user_input = (
        "https://www.bizinfo.go.kr/web/lay1/bbs/S1T122C128/AS/74/view.do?pblancId=PBLN_000000000108439 해당 페이지에 있는 공고를 요약해줘"
    )

response = llm.invoke(user_input)
content = response.content.strip()
print("[GPT 응답 원본]:", content)