#Lesson 3. Function Calling
# 示例 5：用 Function Calling 实现多表查询
# 需求：从订单表中查询各种信息，比如某个用户的订单数量、某个商品的销量、某个用户的消费总额等等。
# 初始化
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
import json
import sqlite3

_ = load_dotenv(find_dotenv())

client = OpenAI()

def print_json(data):
    """
    打印参数。如果参数是有结构的（如字典或列表），则以格式化的 JSON 形式打印；
    否则，直接打印该值。
    """
    if hasattr(data, 'model_dump_json'):
        data = json.loads(data.model_dump_json())

    if (isinstance(data, (list))):
        for item in data:
            print_json(item)
    elif (isinstance(data, (dict))):
        print(json.dumps(
            data,
            indent=4,
            ensure_ascii=False
        ))
    else:
        print(data)

def get_sql_completion(messages, model="gpt-3.5-turbo"):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,
        tools=[{  # 摘自 OpenAI 官方示例 https://github.com/openai/openai-cookbook/blob/main/examples/How_to_call_functions_with_chat_models.ipynb
            "type": "function",
            "function": {
                "name": "ask_database",
                "description": "Use this function to answer user questions about business. \
                            Output should be a fully formed SQL query.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": f"""
                            SQL query extracting info to answer the user's question.
                            SQL should be written using this database schema:
                            {database_schema_string}
                            The query should be returned in plain text, not in JSON.
                            The query should only contain grammars supported by SQLite.
                            """,
                        }
                    },
                    "required": ["query"],
                }
            }
        }],
    )
    return response.choices[0].message

#  描述数据库表结构。与示例4相比，此处定义了三份表格，分别是【customers】、【products】和【orders】。示例4仅定义了【orders】。
database_schema_string = """
CREATE TABLE customers (
    id INT PRIMARY KEY NOT NULL, -- 主键，不允许为空
    customer_name VARCHAR(255) NOT NULL, -- 客户名，不允许为空
    email VARCHAR(255) UNIQUE, -- 邮箱，唯一
    register_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- 注册时间，默认为当前时间
);
CREATE TABLE products (
    id INT PRIMARY KEY NOT NULL, -- 主键，不允许为空
    product_name VARCHAR(255) NOT NULL, -- 产品名称，不允许为空
    price DECIMAL(10,2) NOT NULL -- 价格，不允许为空
);
CREATE TABLE orders (
    id INT PRIMARY KEY NOT NULL, -- 主键，不允许为空
    customer_id INT NOT NULL, -- 客户ID，不允许为空
    product_id INT NOT NULL, -- 产品ID，不允许为空
    price DECIMAL(10,2) NOT NULL, -- 价格，不允许为空
    status INT NOT NULL, -- 订单状态，整数类型，不允许为空。0代表待支付，1代表已支付，2代表已退款
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- 创建时间，默认为当前时间
    pay_time TIMESTAMP -- 支付时间，可以为空
);
"""

# 创建数据库连接
conn = sqlite3.connect(':memory:')
cursor = conn.cursor()

# 将SQL字符串分割成单独的命令
commands = database_schema_string.strip().split(';')

# 移除空命令并执行每个SQL命令
for command in filter(None, commands):
    cursor.execute(command)

# 检查表是否创建成功
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables_created = cursor.fetchall()

tables_created

# 插入5条明确的模拟记录
mock_data = [
    (1, 1001, 'TSHIRT_1', 50.00, 0, '2023-10-12 10:00:00', None),
    (2, 1001, 'TSHIRT_2', 75.50, 1, '2023-10-16 11:00:00', '2023-08-16 12:00:00'),
    (3, 1002, 'SHOES_X2', 25.25, 2, '2023-10-17 12:30:00', '2023-08-17 13:00:00'),
    (4, 1003, 'HAT_Z112', 60.75, 1, '2023-10-20 14:00:00', '2023-08-20 15:00:00'),
    (5, 1002, 'WATCH_X001', 90.00, 0, '2023-10-28 16:00:00', None)
]

for record in mock_data:
    cursor.execute('''
    INSERT INTO orders (id, customer_id, product_id, price, status, create_time, pay_time)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', record)
"""
"?"是一个占位符，用于参数化查询，可以防止SQL注入攻击。record元组中的值将依次替换"?"。
在参数化查询中，SQL语句使用占位符（如?或命名占位符）代替直接在语句中嵌入值。
然后，这些占位符在执行查询时被绑定到实际的参数值上，而不是将参数值直接拼接到SQL字符串中。
这种分离确保了传递给数据库的数据不会被解释为SQL命令的一部分，因此，即使数据包含潜在的SQL代码，它也不会被执行。
"""

# 提交事务
conn.commit()

def ask_database(query):
    cursor.execute(query)
    records = cursor.fetchall()
    return records

prompt = "统计每月每件商品的销售额"
# prompt = "这星期消费最高的用户是谁？他买了哪些商品？ 每件商品买了几件？花费多少？"

messages = [
    {"role": "system", "content": "基于 order 表回答用户问题"},
    {"role": "user", "content": prompt}
]

response = get_sql_completion(messages)
print("====response中的SQL语句====")
print(response.tool_calls[0].function.arguments)

#-------------------------------------------------
response2 = get_sql_completion(messages)
if response2 is None or not hasattr(response2, 'choices') or len(response2.choices) == 0:
    print("====API调用失败或返回结构不符合预期====")
    print_json(messages)
else:
    message = response2.choices[0].messages
    print(messages)
#-------------------------------------------------

if response.content is None:
    response.content = ""

messages.append(response)

print("====Function Calling====")
print_json(response)

if response.tool_calls is not None:
    tool_call = response.tool_calls[0]
    if tool_call.function.name == "ask_database":
        arguments = tool_call.function.arguments
        args = json.loads(arguments)
        print("====SQL====")
        print(args["query"])
        result = ask_database(args["query"])
        print("====DB Records====")
        print(result)

        messages.append({
              "tool_call_id": tool_call.id,
              "role": "tool",
              "name": "ask_database",
              "content": str(result)
        })
        response = get_sql_completion(messages)
        print("====最终回复====")
        print(response.content)
