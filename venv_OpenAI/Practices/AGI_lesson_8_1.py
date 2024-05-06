# 1.1 模型 API：LLM vs. ChatModel
# 安装最新版本
#!pip install --upgrade langchain
#!pip install --upgrade langchain-openai # v0.1.0新增的底包

# 1.1.1 OpenAI 模型封装

import os
from openai import OpenAI

# 加载 .env 到环境变量
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-3.5-turbo")  # 默认是gpt-3.5-turbo
response = llm.invoke("你是谁")    # 【invoke】意为调用
print(response.content)
print("response: ", response)

