# Lesson 5. RAG 系统的基本搭建流程
# 搭建过程：
# 1. 文档加载，并按一定条件切割成片段--参考AGI_lesson_5-1.py or TV_RAG_embedding.py
# 2. 将切割的文本片段灌入检索引擎
# 3. 封装检索接口
# 4. 构建调用流程：Query -> 检索 -> Prompt -> LLM -> 回复

# 3-1. 封装LLM接口
from dotenv import load_dotenv, find_dotenv
import os

_ = load_dotenv(find_dotenv())

from TV_RAG_search_search import search

from openai import OpenAI
client = OpenAI()

def get_completion(prompt, model="gpt-3.5-turbo"):
    '''封装 openai 接口'''
    messages = [{"role": "user", "content": prompt}]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,  # 模型输出的随机性，0 表示随机性最小
    )
    return response.choices[0].message.content

# 4. 构建调用流程：Query -> 检索 -> Prompt -> LLM -> 回复
# 4-1. Prompt 模板
def build_prompt(prompt_template, **kwargs):
    '''将 Prompt 模板赋值'''
    prompt = prompt_template
    for k, v in kwargs.items():
        if isinstance(v, str):
            val = v
        elif isinstance(v, list) and all(isinstance(elem, str) for elem in v):
            val = '\n'.join(v)
        else:
            val = str(v)
        prompt = prompt.replace(f"__{k.upper()}__", val)
    return prompt

prompt_template = """
You are a question and answer bot.
Your task is to answer user questions based on the known information given below.
Make sure that your responses are based solely on the known information below. Do not make up answers.
If the following known information is not sufficient to answer the user's question, simply reply with "I can't answer your question".

Known information:
__INFO__

The user asked:
__QUERY__
"""

user_query = "What is zDP??"

# 1. 检索
search_results = search(user_query, 2)

# 2. 构建 Prompt
prompt = build_prompt(prompt_template, info=search_results, query=user_query)
print("===Prompt===")
print(prompt)

# 3. 调用 LLM
response = get_completion(prompt)

print("===回复===")
print(response)