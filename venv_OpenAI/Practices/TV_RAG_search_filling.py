# Lesson 5. RAG 系统的基本搭建流程
# 搭建过程：
# 1. 文档加载，并按一定条件切割成片段--参考AGI_lesson_5-1.py or TV_RAG_embedding.py
# 2. 将切割的文本片段灌入检索引擎
# 3. 封装检索接口
# 4. 构建调用流程：Query -> 检索 -> Prompt -> LLM -> 回复

# 2-1、灌入检索引擎
# 安装 ES 客户端↓
# pip install elasticsearch7

from elasticsearch7 import Elasticsearch, helpers
from dotenv import load_dotenv, find_dotenv
import os

_ = load_dotenv(find_dotenv())

# import warnings
# warnings.simplefilter("ignore")  # 屏蔽 ES 的一些Warnings

# 【import TV_RAG_embedding.py】导入时必须去掉扩展名。
from TV_RAG_embedding import paragraphs
from TV_1_RAG_classes import TextKeywordExtractor

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

# 2. 定义索引名称
# index_name = "xuc_index_t0308"
index_name = "xuc_index_t0323"

# ↓↓↓↓ 20240314 移至classes ↓↓↓↓
# 3. 如果索引已存在，删除它。!!!!危险命令!!!!
# if es.indices.exists(index=index_name):
#     es.indices.delete(index=index_name)

# 4. 创建索引，一个库(Index)只需执行一次。
es.indices.create(index=index_name)

# 5. 灌库指令
extractor = TextKeywordExtractor()

# 将要被灌入库中的内容
print("==========我是分割线 灌库前的文本===========")
for para in paragraphs[0-3]:
    print(extractor.to_keywords(para))

# """
# ↓↓↓↓ 20240314 移至classes ↓↓↓↓
actions = [
    {
        "_index": index_name,
        "_source": {
            "keywords": extractor.to_keywords(para),
            "text": para
        }
    }
    for para in paragraphs
]

# 6. 文本灌库
test_ku = helpers.bulk(es, actions)
print("==========我是分割线 灌库结果===========")
print(test_ku)
# """