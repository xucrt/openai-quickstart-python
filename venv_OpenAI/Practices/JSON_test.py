
import json

data = {
    "name": "Alice",
    "age": 23,
    "hobi": ["reading", "swimming", "traveling"]
}

print("最初のdataのタイプ＝", type(data))

json_str = json.dumps(data)

print(json_str)
print("jsom.dumpsで変換した後、json_strのタイプ＝", type(json_str))

print("俺は－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－")

json_str2 = '{"name": "hahah", "age": 333, "hobi": ["hahah", "hahah", "hahah"]}'
print("json_str2のタイプ＝", type(json_str2))

data2 = json.loads(json_str2)
print("json.loadsでjson_str2を変換した後、data2のタイプ＝", type(data2))
print(data2)