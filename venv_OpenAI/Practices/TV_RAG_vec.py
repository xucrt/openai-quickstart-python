# Lesson 5. RAG 系统的基本搭建流程
# 四、向量检索
# 4.1、文本向量（Text Embeddings)

import numpy as np
from numpy import dot
from numpy.linalg import norm
from dotenv import load_dotenv, find_dotenv
import os
import sys

# 加载环境变量
_ = load_dotenv(find_dotenv())

from openai import OpenAI
client = OpenAI()

def cos_sim(a, b):
    '''余弦距离 -- 越大越相似'''
    return dot(a, b)/(norm(a)*norm(b))


def l2(a, b):
    '''欧式距离 -- 越小越相似'''
    x = np.asarray(a)-np.asarray(b)
    return norm(x)

def get_embeddings(texts, model="text-embedding-ada-002", dimensions=None):
    '''封装 OpenAI 的 Embedding 模型接口'''
    if model == "text-embedding-ada-002":
        dimensions = None
    if dimensions:
        data = client.embeddings.create(
            input=texts, model=model, dimensions=dimensions).data
    else:
        data = client.embeddings.create(input=texts, model=model).data
    return [x.embedding for x in data]

test_query = ["测试文本"]
vec = get_embeddings(test_query)[0]
print(vec[:10])
print(len(vec))

# query = "国际争端"

# 且能支持跨语言
query = "global conflicts"

documents = [
    "联合国就苏丹达尔富尔地区大规模暴力事件发出警告",
    "土耳其、芬兰、瑞典与北约代表将继续就瑞典“入约”问题进行谈判",
    "日本岐阜市陆上自卫队射击场内发生枪击事件 3人受伤",
    "国家游泳中心（水立方）：恢复游泳、嬉水乐园等水上项目运营",
    "我国首次在空间站开展舱外辐射生物学暴露实验",
]

query_vec = get_embeddings([query])[0]
doc_vecs = get_embeddings(documents)

print("Cosine distance:")
print(cos_sim(query_vec, query_vec))
for vec in doc_vecs:
    print(cos_sim(query_vec, vec))

print("\nEuclidean distance:")
print(l2(query_vec, query_vec))
for vec in doc_vecs:
    print(l2(query_vec, vec))

# 4.3、向量数据库－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－
# 要先安装[pip install chromadb]和【pip install pysqlite3】
# __import__('pysqlite3')
# import sys
# sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
"""
__import__ 是 Python 中的一个内置函数，用于动态地导入模块。
它可以接受一个字符串作为参数，该字符串表示要导入的模块的名称。
与常规的 import 语句不同，__import__ 函数可以在运行时根据字符串动态导入模块。
而 pysqlite3 可能是一个代替标准库 sqlite3 的外部模块，通过动态导入的方式可以灵活地切换模块的实现，而不需要更改代码。
"""

from TV_1_RAG_classes import PDFTextExtractor
# extract_text = PDFTextExtractor()
# 为了演示方便，我们只取两页（第一章）
paragraphs = PDFTextExtractor(f"E:/Programs/materials/Dell_XC_Family_datasheet.pdf")
    # page_numbers=[4, 5],
    # min_line_length=10

import chromadb
from chromadb.config import Settings

class MyVectorDBConnector:
    def __init__(self, collection_name, embedding_fn):
        chroma_client = chromadb.Client(Settings(allow_reset=True))

        # 为了演示，实际不需要每次 reset()
        # chroma_client.reset()

        # 创建一个 collection
        self.collection = chroma_client.get_or_create_collection(
            name=collection_name)
        self.embedding_fn = embedding_fn

    def add_documents(self, documents):
        '''向 collection 中添加文档与向量'''
        self.collection.add(
            embeddings=self.embedding_fn(documents),  # 每个文档的向量
            documents=documents,  # 文档的原文
            ids=[f"id{i}" for i in range(len(documents))]  # 每个文档的 id
        )

    def search(self, query, top_n):
        '''检索向量数据库'''
        results = self.collection.query(
            query_embeddings=self.embedding_fn([query]),
            n_results=top_n
        )
        return results

# 创建一个向量数据库对象
vector_db = MyVectorDBConnector("demo", get_embeddings)
# 向向量数据库中添加文档
vector_db.add_documents(paragraphs)

user_query = "What is Dell XC Family?"
results = vector_db.search(user_query, 2)

for para in results['documents'][0]:
    print(para+"\n")