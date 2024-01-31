# 2.4.1、实现一个 NLU
import os
from openai import OpenAI

# 加载 .env 到环境变量
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

# 初始化 OpenAI 客户端 ???不知为何，这段代码无法正确调用API Key???
# 2024/1/31 修改.env之后需要关闭PyCharm一次，这样load_dotenv(find_dotenv())才能将到修改过的参数添加到现在的运行环境中。

# 初始化 OpenAI 客户端
client = OpenAI()  # 默认使用环境变量中的 OPENAI_API_KEY 和 OPENAI_BASE_URL

# 初始化 OpenAI 客户端，另一种方法
# client = OpenAI(
#     api_key = os.getenv("OPENAI_API_KEY_AGI"),
#     base_url = os.getenv("OPENAI_BASE_URL")
# )

# 基于 prompt 生成文本的函数
def get_completion(prompt, model_d="gpt-3.5-turbo"):    # 默认使用 gpt-3.5-turbo 模型
    messages_d = [{"role": "user", "content": prompt}]  # 将 prompt 作为用户输入
    response = client.chat.completions.create(          # chat.completions.create只能调用gpt-3.5-turbo 模型
        model=model_d,
        messages=messages_d,
        temperature=0,                                  # 模型输出的随机性，0 表示随机性最小
    )
    return response.choices[0].message.content          # 返回模型生成的文本

# 任务描述
instruction = """
你的任务是识别用户对手机流量套餐产品的选择条件。
每种流量套餐产品包含三个属性：名称，月费价格，月流量。
根据用户输入，识别用户在上述三种属性上的倾向。
"""

# 用户输入
input_text = """
办个100G的套餐。
"""

# prompt 模版。instruction 和 input_text 会被替换为上面的内容
prompt = f"""
{instruction}

用户输入：
{input_text}
"""

# 调用之前的函数get_completion()，与大模型进行交互
response = get_completion(prompt)
print("调整之前的输出，如下：－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－")
print(response)
print("－－－－－－－－－－－－－－－－－－我是分割线－－－－－－－－－－－－－－－－－－－－－－")

"""
大模型生成的反馈，即print(response)的输出结果：
－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－
根据用户输入，可以得出以下结论：
1. 名称：用户倾向选择100G的套餐。
2. 月费价格：用户没有提及对月费价格的倾向。
3. 月流量：用户倾向选择100G的套餐。
综上所述，用户对手机流量套餐产品的选择条件主要是在月流量上倾向选择100G的套餐。
－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－

这段输出结果已经按照“键值对”的规则将自然语言格式化，但还需要将这种格式转化为程序语言能够识别的数据格式，比如JSON。
但中文无法作为”键“在JSON格式中使用，因此需要进一步将”键“转化成英文。
"""

# 规定大模型的输出格式
output_format = """
以 JSON 格式输出
"""

# 稍微调整下咒语，加入输出格式{output_format}
prompt = f"""
{instruction}

{output_format}

用户输入：
{input_text}
"""
# 并任务描述增加了字段的英文标识符，【名称(name)，月费价格(price)，月流量(data)】。这段新内容覆盖变量instruction之前的内容。
instruction = """
你的任务是识别用户对手机流量套餐产品的选择条件。
每种流量套餐产品包含三个属性：名称(name)，月费价格(price)，月流量(data)。
根据用户输入，识别用户在上述三种属性上的倾向。
"""

response = get_completion(prompt)
print("第一次调整过后的输出，如下：－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－")
print(response)
print("－－－－－－－－－－－－－－－－－－我是分割线－－－－－－－－－－－－－－－－－－－－－－")

"""
大模型生成的反馈，即调整过后print(response)的的输出，如下：
－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－
{
  "名称": "100G套餐",
  "月费价格": "不确定",
  "月流量": "100G"
}
－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－
【名称(name)，月费价格(price)，月流量(data)】并没有自动变成英文。
虽然大模型是懂 JSON 的，但需要对 JSON 结构做严格定义。
"""
# 更精细的数据格式输出描述
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
"""

prompt = f"""
{instruction}

{output_format}

用户输入：
{input_text}
"""

response = get_completion(prompt)
print("第二次调整，规定了更精细的数据给后的输出，如下：－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－")
print(response)
print("－－－－－－－－－－－－－－－－－－我是分割线－－－－－－－－－－－－－－－－－－－－－－")

"""
第二次调整，规定了更精细的数据给后的输出，如下：
－－－－－－－－－－－－－－－－－－
{
  "name": null,
  "price": null,
  "data": {
    "operator": ">=",
    "value": 100
  },
  "sort": null
}
－－－－－－－－－－－－－－－－－－
与期待的格式一致。
下面再加上用户的需求，即【用户输入：{input_text}】的内容，看看效果。
"""

# input_text = "办个100G以上的套餐"
# input_text = "我要无限量套餐"
# input_text = "有没有便宜的套餐"
input_text = "我要突然死了，怎么办？"

prompt = f"""
{instruction}

{output_format}

用户输入：
{input_text}
"""

response = get_completion(prompt)
print("第三次调整，加入了用户的需求后的输出，如下：－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－")
print(response)
print("－－－－－－－－－－－－－－－－－－我是分割线－－－－－－－－－－－－－－－－－－－－－－")

"""
第三次调整，加入了用户的需求后的输出，如下：

【input_text = "办个100G以上的套餐"】,得到反馈：
－－－－－－－－－－－－－－－－－－
{
  "data": {
    "operator": ">=",
    "value": 100
  }
}
－－－－－－－－－－－－－－－－－－

【input_text = "我要无限量套餐"】，得到反馈：
－－－－－－－－－－－－－－－－－
{
  "name": "无限套餐"
}
－－－－－－－－－－－－－－－－－

【input_text = "有没有便宜的套餐"】，得到反馈：
－－－－－－－－－－－－－－－－－
{
  "name": "经济套餐",
  "price": {
    "operator": "<=",
    "value": 100
  }
}
－－－－－－－－－－－－－－－－－－

【input_text = "我要突然死了，怎么办？"】，没有得到反馈：
－－－－－－－－－－－－－－－－－－
{}
－－－－－－－－－－－－－－－－－－

为了让大模型的回答更加稳定，可以给他一些回答的例子，用于学习。
这些例子放在变量prompt当中。
"""

examples = """
便宜的套餐：{"sort":{"ordering"="ascend","value"="price"}}
有没有不限流量的：{"data":{"operator":"==","value":"无上限"}}
流量大的：{"sort":{"ordering"="descend","value"="data"}}
100G以上流量的套餐最便宜的是哪个：{"sort":{"ordering"="ascend","value"="price"},"data":{"operator":">=","value":100}}
月费不超过200的：{"price":{"operator":"<=","value":200}}
就要月费180那个套餐：{"price":{"operator":"==","value":180}}
经济套餐：{"name":"经济套餐"}
突然死了：{"name":"不用担心，根据我的计算，您会长命百岁的。"}
"""

# input_text = "有没有便宜的套餐"
# input_text = "有没有土豪套餐"
# input_text = "办个200G的套餐"
# input_text = "有没有流量大的套餐"
# input_text = "200元以下，流量大的套餐有啥"
# input_text = "你说那个10G的套餐，叫啥名字"
input_text = "我要突然死了，怎么办？"

# 有了例子
prompt = f"""
{instruction}

{output_format}

例如：
{examples}

用户输入：
{input_text}
"""

response = get_completion(prompt)
print("第四次调整，加入了回答案例后的输出，如下：－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－")
print(response)
print("－－－－－－－－－－－－－－－－－－我是分割线－－－－－－－－－－－－－－－－－－－－－－")

"""
第四次调整，加入了回答案例后的输出，如下：
【input_text = "有没有土豪套餐"】，得到反馈：
－－－－－－－－－－－－－－－－－－
{"name": "无限套餐"}
－－－－－－－－－－－－－－－－－－

【input_text = "我要突然死了，怎么办？"】，得到了预期的反馈：
－－－－－－－－－－－－－－－－－－
{"name":"不用担心，根据我的计算，您会长命百岁的。"}
－－－－－－－－－－－－－－－－－－

★划重点：「给例子」很常用，效果特别好
改变习惯，优先用 Prompt 解决问题
用好 prompt 可以减轻预处理和后处理的工作量和复杂度。
★划重点：一切问题先尝试用 prompt 解决，往往有四两拨千斤的效果
"""