import os
from openai import OpenAI

# 加载 .env 到环境变量
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

# 初始化 OpenAI 客户端 ???不知为何，这段代码无法正确调用API Key???
# client = OpenAI()  # 默认使用环境变量中的 OPENAI_API_KEY 和 OPENAI_BASE_URL

# 配置 OpenAI 服务
client = OpenAI(
    # defaults to os.environ.get("OPENAI_API_KEY")
    api_key=os.getenv("OPENAI_API_KEY_AGI"),
    base_url=os.getenv("OPENAI_BASE_URL")
)

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "你好",
        }
    ],
    model="gpt-3.5-turbo",
    # model="text-davinci-003", # 模型text-davinci-003已被弃用。
    # model="gpt-3.5-turbo-instruct", #chat.create调用gpt-3.5-turbo； completions.create调用gpt-3.5-turbo-instruct
)

print(chat_completion.choices[0].message.content)

# 如果出现问题请打印下面
print(chat_completion)