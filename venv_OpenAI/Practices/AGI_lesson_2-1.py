# 2.4.2、支持多轮对话 DST
import os
from openai import OpenAI

# 加载 .env 到环境变量
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

# 初始化 OpenAI 客户端
client = OpenAI()

def get_completion(prompt, model_d="gpt-3.5-turbo"):    # 默认使用 gpt-3.5-turbo 模型
    messages_d = [{"role": "user", "content": prompt}]  # 将 prompt 作为用户输入
    response = client.chat.completions.create(          # chat.completions.create只能调用gpt-3.5-turbo 模型
        model=model_d,
        messages=messages_d,
        temperature=0,                                  # 模型输出的随机性，0 表示随机性最小
    )
    return response.choices[0].message.content          # 返回模型生成的文本

instruction = """
你的任务是识别用户对手机流量套餐产品的选择条件。
每种流量套餐产品包含三个属性：名称(name)，月费价格(price)，月流量(data)。
根据对话上下文，识别用户在上述属性上的倾向。识别结果要包含整个对话的信息。
"""

# 输出描述
output_format = """
以JSON格式输出。
1. name字段的取值为string类型，取值必须为以下之一：经济套餐、畅游套餐、无限套餐、校园套餐 或 null；

2. price字段的取值为一个结构体 或 null，包含两个字段：
(1) operator, string类型，取值范围：'<='（小于等于）, '>=' (大于等于), '=='（等于）
(2) value, int类型

3. data字段的取值为取值为一个结构体 或 null，包含两个字段：
(1) operator, string类型，取值范围：'<='（小于等于）, '>=' (大于等于), '=='（等于）
(2) value, int类型或string类型，string类型只能是'无上限'

4. 用户的意图可以包含按price或data排序，以sort字段标识，取值为一个结构体：
(1) 结构体中以"ordering"="descend"表示按降序排序，以"value"字段存储待排序的字段
(2) 结构体中以"ordering"="ascend"表示按升序排序，以"value"字段存储待排序的字段

只输出中只包含用户提及的字段，不要猜测任何用户未直接提及的字段。不要输出值为null的字段。
DO NOT OUTPUT NULL-VALUED FIELD! 确保输出能被json.loads加载。
"""
# DO NOT OUTPUT NULL-VALUED FIELD!

# 多轮对话的例子
examples = """
客服：有什么可以帮您
用户：100G套餐有什么

{"data":{"operator":">=","value":100}}

客服：有什么可以帮您
用户：100G套餐有什么
客服：我们现在有无限套餐，不限流量，月费300元
用户：太贵了，有200元以内的不

{"data":{"operator":">=","value":100},"price":{"operator":"<=","value":200}}

客服：有什么可以帮您
用户：便宜的套餐有什么
客服：我们现在有经济套餐，每月50元，10G流量
用户：100G以上的有什么

{"data":{"operator":">=","value":100},"sort":{"ordering"="ascend","value"="price"}}

客服：有什么可以帮您
用户：100G以上的套餐有什么
客服：我们现在有畅游套餐，流量100G，月费180元
用户：流量最多的呢

{"sort":{"ordering"="descend","value"="data"},"data":{"operator":">=","value":100}}
"""

# input_text = "哪个便宜"
# input_text = "无限量哪个多少钱"
# input_text = "流量最大的多少钱"
input_text = "我要无限量套餐"

# 多轮对话上下文
context = f"""
客服：有什么可以帮您  
用户：有什么100G以上的套餐推荐
客服：我们有畅游套餐和无限套餐，您有什么价格倾向吗
用户：{input_text}
"""

prompt = f"""
{instruction}

{output_format}

{examples}

{context}
"""

response = get_completion(prompt)
print(response)

"""
input_text = "哪个便宜"，获得以下反馈：
－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－
{"sort":{"ordering"="ascend","value"="price"},"data":{"operator":">=","value":100}}
－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－

input_text = "无限量哪个多少钱"
－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－
{"sort":{"ordering"="ascend","value"="price"},"data":{"operator":">=","value":100}}
－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－

input_text = "流量最大的多少钱"
－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－
{"sort":{"ordering"="descend","value"="data"},"data":{"operator":">=","value":100}}
－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－

input_text = "我要无限量套餐"
－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－
{"data":{"operator":">=","value":100},"sort":{"ordering"="descend","value"="data"}}
－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－
"""