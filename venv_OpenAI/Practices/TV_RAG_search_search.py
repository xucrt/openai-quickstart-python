# Lesson 5. RAG 系统的基本搭建流程
# 搭建过程：
# 1. 文档加载，并按一定条件切割成片段--参考AGI_lesson_5-1.py or TV_RAG_embedding.py
# 2. 将切割的文本片段灌入检索引擎
# 3. 封装检索接口
# 4. 构建调用流程：Query -> 检索 -> Prompt -> LLM -> 回复

# 2-2、实现关键字检索
from elasticsearch7 import Elasticsearch, helpers
from dotenv import load_dotenv, find_dotenv
import os

import warnings
warnings.simplefilter("ignore")  # 屏蔽 ES 的一些Warnings

from TV_RAG_embedding import TextKeywordExtractor

_ = load_dotenv(find_dotenv())

# 从环境变量获取配置信息
es_host = os.environ.get("ES_HOST")
es_username = os.environ.get("ES_USERNAME")
es_password = os.environ.get("ES_PASSWORD")

# 将文本灌入检索引擎
# 1. 创建Elasticsearch连接
es = Elasticsearch(
    hosts=[es_host],  # 服务地址与端口
    http_auth=(es_username, es_password),  # 用户名，密码
)

index_name = "xuc_index_t0311"

extractor = TextKeywordExtractor()
def search(query_string, top_n=10):
    # ES 的查询语言
    search_query = {
        "match": {
            "keywords": extractor.to_keywords(query_string)
            }
    }
    res = es.search(index=index_name, query=search_query, size=top_n)
    print("==========我是分割线 in search, match KW ===========")
    print(res)
    return [hit["_source"]["text"] for hit in res["hits"]["hits"]]

results = search("what is vmware?", 1)

# search_query_test = {
#     "query": {
#         "match": {
#             "keywords": "vmware"
#         }
#     }
# }
# raw_results = es.search(index="xuc_index_t0311", body=search_query_test, size=10)
# print("==========我是分割线, match text===========")
# print(raw_results)

