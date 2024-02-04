import json
import copy
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

client = OpenAI()

instruction = """
你的任务是识别用户对手机流量套餐产品的选择条件。
每种流量套餐产品包含三个属性：名称(name)，月费价格(price)，月流量(data)。
根据用户输入，识别用户在上述三种属性上的倾向。
"""

# 输出格式
output_format = """
以JSON格式输出。
1. name字段的取值为string类型，取值必须为以下之一：经济套餐、畅游套餐、无限套餐、校园套餐 或 null；

2. price字段的取值为一个结构体 或 null，包含两个字段：
(1) operator, string类型，取值范围：'<='（小于等于）, '>=' (大于等于), '=='（等于）
(2) value, int类型

3. data字段的取值为一个结构体 或 null，包含两个字段：
(1) operator, string类型，取值范围：'<='（小于等于）, '>=' (大于等于), '=='（等于）
(2) value, int类型或string类型，string类型只能是'无上限'

4. 用户的意图可以包含按price或data排序，以sort字段标识，取值为一个结构体：
(1) 结构体中以"ordering"="descend"表示按降序排序，以"value"字段存储待排序的字段
(2) 结构体中以"ordering"="ascend"表示按升序排序，以"value"字段存储待排序的字段

只输出中只包含用户提及的字段，不要猜测任何用户未直接提及的字段。
DO NOT OUTPUT NULL-VALUED FIELD! 确保输出能被json.loads加载。
只输出中只包含用户提及的字段，不要猜测任何用户未直接提及的字段，不输出值为null的字段。
"""

# 22:13 2024/02/03 使用examples(加入例子)，未获得完善的反馈。
# examples = """
# 便宜的套餐：{"sort":{"ordering"="ascend","value"="price"}}
# 有没有不限流量的：{"data":{"operator":"==","value":"无上限"}}
# 流量大的：{"sort":{"ordering"="descend","value"="data"}}
# 100G以上流量的套餐最便宜的是哪个：{"sort":{"ordering"="ascend","value"="price"},"data":{"operator":">=","value":100}}
# 月费不超过200的：{"price":{"operator":"<=","value":200}}
# 就要月费180那个套餐：{"price":{"operator":"==","value":180}}
# 经济套餐：{"name":"经济套餐"}
# 我是学生：{"name":"校园套餐"}
# """

# 10:37 2024/02/04 将前一天的examples(加入例子)更换成多轮对话的examples(2.4.2、支持多轮对话 DST)，未获得完善反馈。
examples = """
# 10:50 2024/02/04 新增以下对话例
客服：您好！有什么可以帮您
用户：我是学生，有什么合适的套餐
客服：我们现在有校园套餐，流量200G，月费150元
用户：流量最多的呢

{"name":"校园套餐"}

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

class NLU:
    def __init__(self):
        self.prompt_template = f"{instruction}\n\n{output_format}\n\n{examples}\n\n用户输入：\n__INPUT__"

    def _get_completion(self, prompt, model="gpt-3.5-turbo"):
        messages = [{"role": "user", "content": prompt}]
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0,  # 模型输出的随机性，0 表示随机性最小
        )
        semantics = json.loads(response.choices[0].message.content)
        return {k: v for k, v in semantics.items() if v}

    def parse(self, user_input):
        prompt = self.prompt_template.replace("__INPUT__", user_input)
        return self._get_completion(prompt)


class DST:
    def __init__(self):
        pass

    def update(self, state, nlu_semantics):
        if "name" in nlu_semantics:
            state.clear()
        if "sort" in nlu_semantics:
            slot = nlu_semantics["sort"]["value"]
            if slot in state and state[slot]["operator"] == "==":
                del state[slot]
        for k, v in nlu_semantics.items():
            state[k] = v
        return state


class MockedDB:
    def __init__(self):
        self.data = [
            {"name": "经济套餐", "price": 50, "data": 10, "requirement": None},
            {"name": "畅游套餐", "price": 180, "data": 100, "requirement": None},
            {"name": "无限套餐", "price": 300, "data": 1000, "requirement": None},
            {"name": "校园套餐", "price": 150, "data": 200, "requirement": "在校生"},
        ]

    def retrieve(self, **kwargs):
        records = []
        for r in self.data:
            select = True
            if r["requirement"]:
                if "status" not in kwargs or kwargs["status"] != r["requirement"]:
                    continue
            for k, v in kwargs.items():

                # 11:21 2024/02/04 添加跳过NoneType的处理↓↓↓↓↓↓
                if v['value'] is None:
                    continue
                try:
                    if not eval(f"r['{k}'] {v['operator']} {v['value']}"):
                        select = False
                        break
                except TypeError:
                    print(f"TypeError comparing {k} with value {v['value']}")
                    select = False
                    break
                # 11:21 2024/02/04 添加跳过NoneType的处理↑↑↑↑↑↑↑

                if k == "sort":
                    continue
                if k == "data" and v["value"] == "无上限":
                    if r[k] != 1000:
                        select = False
                        break
                if "operator" in v:
                    if not eval(str(r[k])+v["operator"]+str(v["value"])):
                        select = False
                        break
                elif str(r[k]) != str(v):
                    select = False
                    break
            if select:
                records.append(r)
        if len(records) <= 1:
            return records
        key = "price"
        reverse = False
        if "sort" in kwargs:
            key = kwargs["sort"]["value"]
            reverse = kwargs["sort"]["ordering"] == "descend"
        return sorted(records, key=lambda x: x[key], reverse=reverse)

# ★★★★★★ORIGINAL★★★★★★
# class MockedDB:
#     def __init__(self):
#         self.data = [
#             {"name": "经济套餐", "price": 50, "data": 10, "requirement": None},
#             {"name": "畅游套餐", "price": 180, "data": 100, "requirement": None},
#             {"name": "无限套餐", "price": 300, "data": 1000, "requirement": None},
#             {"name": "校园套餐", "price": 150, "data": 200, "requirement": "在校生"},
#         ]
#
#     def retrieve(self, **kwargs):
#         records = []
#         for r in self.data:
#             select = True
#             if r["requirement"]:
#                 if "status" not in kwargs or kwargs["status"] != r["requirement"]:
#                     continue
#             for k, v in kwargs.items():
#                 if k == "sort":
#                     continue
#                 if k == "data" and v["value"] == "无上限":
#                     if r[k] != 1000:
#                         select = False
#                         break
#                 if "operator" in v:
#                     if not eval(str(r[k])+v["operator"]+str(v["value"])):
#                         select = False
#                         break
#                 elif str(r[k]) != str(v):
#                     select = False
#                     break
#             if select:
#                 records.append(r)
#         if len(records) <= 1:
#             return records
#         key = "price"
#         reverse = False
#         if "sort" in kwargs:
#             key = kwargs["sort"]["value"]
#             reverse = kwargs["sort"]["ordering"] == "descend"
#         return sorted(records, key=lambda x: x[key], reverse=reverse)


class DialogManager:
    def __init__(self, prompt_templates):
        self.state = {}
        self.session = [
            {
                "role": "system",
                "content": "你是一个手机流量套餐的客服代表，你叫小瓜。可以帮助用户选择最合适的流量套餐产品。"
            }
        ]
        self.nlu = NLU()
        self.dst = DST()
        self.db = MockedDB()
        self.prompt_templates = prompt_templates

    def _wrap(self, user_input, records):
        if records:
            prompt = self.prompt_templates["recommand"].replace(
                "__INPUT__", user_input)
            r = records[0]
            for k, v in r.items():
                prompt = prompt.replace(f"__{k.upper()}__", str(v))
        else:
            prompt = self.prompt_templates["not_found"].replace(
                "__INPUT__", user_input)
            for k, v in self.state.items():
                if "operator" in v:
                    prompt = prompt.replace(
                        f"__{k.upper()}__", v["operator"]+str(v["value"]))
                else:
                    prompt = prompt.replace(f"__{k.upper()}__", str(v))
        return prompt

    def _call_chatgpt(self, prompt, model="gpt-3.5-turbo"):
        session = copy.deepcopy(self.session)
        session.append({"role": "user", "content": prompt})
        response = client.chat.completions.create(
            model=model,
            messages=session,
            temperature=0,
        )
        return response.choices[0].message.content

    def run(self, user_input):
        # 调用NLU获得语义解析
        semantics = self.nlu.parse(user_input)
        print("===semantics===")
        print(semantics)

        # 调用DST更新多轮状态
        self.state = self.dst.update(self.state, semantics)
        print("===state===")
        print(self.state)

        # 根据状态检索DB，获得满足条件的候选
        records = self.db.retrieve(**self.state)

        # 拼装prompt调用chatgpt
        prompt_for_chatgpt = self._wrap(user_input, records)
        print("===gpt-prompt===")
        print(prompt_for_chatgpt)

        # 调用chatgpt获得回复
        response = self._call_chatgpt(prompt_for_chatgpt)

        # 将当前用户输入和系统回复维护入chatgpt的session
        self.session.append({"role": "user", "content": user_input})
        self.session.append({"role": "assistant", "content": response})
        return response

prompt_templates = {
    "recommand": "用户说：__INPUT__ \n\n向用户介绍如下产品：__NAME__，月费__PRICE__元，每月流量__DATA__G。",
    "not_found": "用户说：__INPUT__ \n\n没有找到满足__PRICE__元价位__DATA__G流量的产品，询问用户是否有其他选择倾向。"
}

# 定义语气要求。"NO COMMENTS. NO ACKNOWLEDGEMENTS."是常用 prompt，表示「有事儿说事儿，别 bb」
ext = "很口语，亲切一些。不用说“抱歉”。直接给出回答，不用在前面加“小瓜说：”。NO COMMENTS. NO ACKNOWLEDGEMENTS."
prompt_templates = {k: v+ext for k, v in prompt_templates.items()}

# ext = "\n\n遇到类似问题，请参照以下回答：\n问：流量包太贵了\n答：亲，我们都是全省统一价哦。"
# prompt_templates = {k: v+ext for k, v in prompt_templates.items()}

dm = DialogManager(prompt_templates)

response = dm.run("`我是学生，有没有价格在180元以内合适的套餐？流量能有多少？`")
# response = dm.run("流量大的")
print("===response 1===")
print(response)

response = dm.run("`流量太少了，有没有大一些的？`")
print("===response 2===")
print(response)

"""
22:13 2024/02/03：：：：：：：：：：：：：：：：：：：：：：：
使用examples(加入例子)，未获得完善的反馈。
－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－
输入：
response = dm.run("`我是学生，有没有价格在180元以内合适的套餐？流量能有多少？`")

输出：
===semantics===
{'name': '校园套餐', 'price': {'operator': '<=', 'value': 200}}
===state===
{'name': '校园套餐', 'price': {'operator': '<=', 'value': 200}}
===gpt-prompt===
用户说：`我是学生，有没有价格在200元以内合适的套餐？` 

没有找到满足<=200元价位__DATA__G流量的产品，询问用户是否有其他选择倾向。很口语，亲切一些。不用说“抱歉”。直接给出回答，不用在前面加“小瓜说：”。NO COMMENTS. NO ACKNOWLEDGEMENTS.
===response===
我们有一款适合学生的套餐，叫做“学生流量包”。它每月只需199元，包含__DATA__G流量，适合日常上网、社交娱乐等使用。您可以考虑选择这个套餐。如果您有其他需求或者想了解更多套餐信息，请告诉我。
－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－

有两个问题：
1. semantics和state都正确获取的语义，但是在拼装回答的语句时，__DATA__没有拼装进去。
2. 拼装之后输出语句中的价格和名称都不对。

2024/02/04 ：：：：：：：：：：：：：：：：：：：：：：：
将前一天的examples(加入例子)更换成多轮对话的examples(2.4.2、支持多轮对话 DST)，未获得完善反馈。
－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－
输入：
response = dm.run("`我是学生，有没有价格在180元以内合适的套餐？流量能有多少？`")

输出：
===semantics===
{'price': {'operator': '<=', 'value': 180}}
===state===
{'price': {'operator': '<=', 'value': 180}}
===gpt-prompt===
用户说：`我是学生，有没有价格在180元以内合适的套餐？流量能有多少？` 

向用户介绍如下产品：经济套餐，月费50元，每月流量10G。很口语，亲切一些。不用说“抱歉”。直接给出回答，不用在前面加“小瓜说：”。NO COMMENTS. NO ACKNOWLEDGEMENTS.
===response===
学生用户您好！我们有一款非常适合您的经济套餐，每月仅需50元，您将享受到10G的流量。这个套餐价格在您所期望的180元以内，而且流量也足够您在日常使用中畅快上网。如果您对这个套餐感兴趣，我可以帮您办理。

有一个问题：
1. 逻辑正确，但未能推荐校园套餐。
猜测是采用asend排序之后，直接推荐了最便宜的套餐。
"""




