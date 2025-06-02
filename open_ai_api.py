from openai import OpenAI
from langchain_openai import ChatOpenAI

from config import OPEN_AI_API_KEY



user_input = "카페을 운영하고 있는데 정확한 업종이 뭘까"


llm = ChatOpenAI(
    temperature=0,
    model_name='gpt-4o-mini',
    openai_api_key=OPEN_AI_API_KEY
)

response = llm.invoke(user_input)
print(response.content)