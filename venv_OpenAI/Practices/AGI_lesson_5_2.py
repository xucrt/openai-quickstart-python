# Lesson 5. RAG 系统的基本搭建流程
# 搭建过程：
# 1. 文档加载，并按一定条件切割成片段
# 2. 将切割的文本片段灌入检索引擎
# 3. 封装检索接口
# 4. 构建调用流程：Query -> 检索 -> Prompt -> LLM -> 回复

# 1-1、文档的加载与切割
# 需要实现安装 pdf 解析库
# pip install pdfminer.six
# 参考AGI_lesson_5-1.py

# import AGI_lesson_5_1
from AGI_lesson_5_1 import paragraphs

# 2-1、灌入检索引擎
# 安装 ES 客户端↓
# pip install elasticsearch7
#
# 安装NLTK（文本处理方法库）↓
# pip install nltk

from elasticsearch7 import Elasticsearch, helpers
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import nltk
import re

import warnings
warnings.simplefilter("ignore")  # 屏蔽 ES 的一些Warnings

# nltk.download('punkt')  # 英文切词、词根、切句等方法
# nltk.download('stopwords')  # 英文停用词库

def to_keywords(input_string):
    '''（英文）文本只保留关键字'''
    # 使用正则表达式替换所有非字母数字的字符为空格
    no_symbols = re.sub(r'[^a-zA-Z0-9\s]', ' ', input_string)
    word_tokens = word_tokenize(no_symbols)
    # 加载停用词表
    stop_words = set(stopwords.words('english'))
    ps = PorterStemmer()
    # 去停用词，取词根
    filtered_sentence = [ps.stem(w)
                         for w in word_tokens if not w.lower() in stop_words]
    return ' '.join(filtered_sentence)

# 将文本灌入检索引擎
# 1. 创建Elasticsearch连接
es = Elasticsearch(
    hosts=['http://11'],  # 服务地址与端口
    http_auth=("e", "F"),  # 用户名，密码
)

# 2. 定义索引名称
# index_name = "xuc_index_tmp"
index_name = "xuc_index_t3"

# # # 3. 如果索引已存在，删除它（仅供演示，实际应用时不需要这步）
# if es.indices.exists(index=index_name):
#     es.indices.delete(index=index_name)
#
# # 4. 创建索引
# es.indices.create(index=index_name)
#
# # 5. 灌库指令
# actions = [
#     {
#         "_index": index_name,
#         "_source": {
#             "keywords": to_keywords(para),
#             "text": para
#         }
#     }
#     for para in paragraphs
# ]

# 被灌入库中的内容
print(paragraphs)

# # 6. 文本灌库
# test_ku = helpers.bulk(es, actions)
# print("==========我是分割线 灌库结果===========")
# print(test_ku)

# 实现关键字检索
def search(query_string, top_n=10):
    # ES 的查询语言
    search_query = {
        "match": {
            "keywords": to_keywords(query_string)
            }
    }
    res = es.search(index=index_name, query=search_query, size=top_n)
    print("==========我是分割线 in search ===========")
    print(res)
    return [hit["_source"]["text"] for hit in res["hits"]["hits"]]

# 关键词分解结果
print("==========我是分割线 分解===========")
keyW = to_keywords("technic")
print(keyW)
print("==========我是分割线 search查询结果===========")

results = search("TELUS", 10)
print(results)

print("==========我是分割线 查询其他库===========")
#xuc_index_tmp UUID: _EUFttWvQ6qL38tA0MKLAg

search_query_test = {
    "query": {
        "match": {
            "text": "data"
        }
    }
}

raw_results = es.search(index="xuc_index_tmp", body=search_query_test, size=10)
print(raw_results)

search_query_test = {
    "query": {
        "match": {
            "text": "务必"
        }
    }
}

other_results_1 = es.search(index="ai_reoprt", body=search_query_test, size=10)
print(other_results_1)

search_query_test = {
    "query": {
        # "match": {
        #     "text": "story"
        # },
        "match": {
            "keywords": "tell"
        }
    }
}

other_results_2 = es.search(index="book_index_20240301", body=search_query_test, size=10)
print(other_results_2)

search_query_test = {
    "query": {
        "match": {
            "text": "zDP"
        },
        # "match": {
        #     "keywords": "conf"
        # }
    }
}

new_results = es.search(index="xuc_index_tmp", body=search_query_test, size=10)
print(new_results)

# for r in results:
#     print(r+"\n")