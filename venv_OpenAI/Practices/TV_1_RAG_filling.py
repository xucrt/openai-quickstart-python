# Lesson 5. RAG 系统的基本搭建流程
# 搭建过程：
# 1. 文档加载，并按一定条件切割成片段--参考AGI_lesson_5-1.py or TV_RAG_embedding.py
# 2. 将切割的文本片段灌入检索引擎
# 3. 封装检索接口
# 4. 构建调用流程：Query -> 检索 -> Prompt -> LLM -> 回复

# 2-1、灌入检索引擎
# 安装 ES 客户端↓
# pip install elasticsearch7

# import os
#
# _ = load_dotenv(find_dotenv())

from TV_1_RAG_embedding import paragraphs
from TV_1_RAG_classes import ElasticsearchMgr

es_mgr = ElasticsearchMgr()

# 4. 创建索引
index = "xuc_index_t0421"
# index = "xuc_index_t0311"

# 3. 检查索引是否已存在。如果已存在，请手动修改index的值。
es_mgr.create_index(index)

# 5. 灌库指令
from TV_1_RAG_classes import ElasticsearchBulkInserter

es_bulk = ElasticsearchBulkInserter(index)

es_bulk.insert_text(paragraphs)
