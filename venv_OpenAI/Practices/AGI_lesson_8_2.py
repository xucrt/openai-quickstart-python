# 1.1 模型 API：LLM vs. ChatModel
# 安装最新版本
#!pip install --upgrade langchain
#!pip install --upgrade langchain-openai # v0.1.0新增的底包

# 1.1.2 多轮对话 Session 封装

import os
from openai import OpenAI

# 加载 .env 到环境变量
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-3.5-turbo")  # 默认是gpt-3.5-turbo

from langchain.schema import (
    AIMessage,  # 等价于OpenAI接口中的assistant role
    HumanMessage,  # 等价于OpenAI接口中的user role
    SystemMessage  # 等价于OpenAI接口中的system role
)

messages = [
    SystemMessage(content="你是AGIClass的课程助理。"),
    HumanMessage(content="我是一个心怀梦想，眼高手低的学员，我叫传说。"),
    AIMessage(content="欢迎！"),
    HumanMessage(content="我是谁")
]

ret = llm.invoke(messages)

print(ret.content)