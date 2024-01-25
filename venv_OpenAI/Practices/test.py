import os
import openai
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY_AGI"),
    base_url=os.getenv("OPENAI_BASE_URL")
)
print(openai.__version__)

response = client.completions.create(
    # model="text-davinci-004",
    model="gpt-3.5-turbo-instruct",
    prompt="你好",
    # streams="true",
    # temperature=0,
    # max_tokens=5,
    # messages=[
    #     {
    #         "role": "user",
    #         "content": "你好"
    #     }
    # ],
)

print(response)

