# Lesson 5. RAG 系统的基本搭建流程
# 搭建流程：
# 1. 文档加载，并按一定条件切割成片段
# 2. 将切割的文本片段灌入检索引擎
# 3. 封装检索接口
# 4. 构建调用流程：Query -> 检索 -> Prompt -> LLM -> 回复

from dotenv import load_dotenv, find_dotenv
import os

# 从环境变量获取配置信息
es_host = os.environ.get("ES_HOST")
es_username = os.environ.get("ES_USERNAME")
es_password = os.environ.get("ES_PASSWORD")

# 0. 整理文件名
class FileNameModifier:
    def __init__(self, directory):
        '''初始化文件名修改器，设置工作目录'''
        self.directory = directory

    def replace_spaces_with_underscores(self):
        '''将目录下的所有文件名中的空格替换为下划线'''
        # 遍历目录下的所有文件
        for filename in os.listdir(self.directory):
            if ' ' in filename:
                new_filename = filename.replace(' ', '_')
                # 构建原始文件和新文件的完整路径
                original_path = os.path.join(self.directory, filename)
                new_path = os.path.join(self.directory, new_filename)
                # 重命名文件
                os.rename(original_path, new_path)
                print(f"Renamed '{filename}' to '{new_filename}'")

# 1. 文档加载，并按一定条件切割成片段
# 1-1、文档切割－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－
# 需要先安装 pdf 解析库
# pip install pdfminer.six

from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer

class PDFTextExtractor:
    def __init__(self, filename, page_numbers=None, min_line_length=1):
        '''从 PDF 文件中（按指定页码）提取文字'''
        self.filename = filename
        self.page_numbers = page_numbers
        self.min_line_length = min_line_length

    def extract_text(self):
        paragraphs = []
        buffer = ''
        full_text = ''
        # 提取全部文本
        for i, page_layout in enumerate(extract_pages(self.filename)):
            if self.page_numbers is not None and i not in self.page_numbers:
                continue
            for element in page_layout:
                if isinstance(element, LTTextContainer):
                    full_text += element.get_text() + '\n'
        # 按空行分隔，将文本重新组织成段落
        lines = full_text.split('\n')
        for text in lines:
            if len(text) >= self.min_line_length:
                buffer += (' '+text) if not text.endswith('-') else text.strip('-')
            elif buffer:
                paragraphs.append(buffer)
                buffer = ''
        if buffer:
            paragraphs.append(buffer)
        return paragraphs


# 1-2、文本处理－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－
# 安装NLTK（文本处理方法库）↓
# pip install nltk

from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import nltk
import re

# 'punkt'和'stopwords'只需在本地安装一次。
# nltk.download('punkt')  # 英文切词、词根、切句等方法
# nltk.download('stopwords')  # 英文停用词库

# 文本处理
class TextKeywordExtractor:
    def __init__(self):
        """初始化停用词和词干提取器"""
        self.stop_words = set(stopwords.words('english'))
        self.ps = PorterStemmer()
    def to_keywords(self, input_string):
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


# 2-1、Index管理－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－
# from dotenv import load_dotenv, find_dotenv
# import os
# import sys
#
# # 加载环境变量
# _ = load_dotenv(find_dotenv())

class ElasticsearchMgr:
    def __init__(self):
        self.es_host = os.environ.get("ES_HOST")
        self.es_username = os.environ.get("ES_USERNAME")
        self.es_password = os.environ.get("ES_PASSWORD")
        self.es = Elasticsearch(
            hosts=[self.es_host],
            http_auth=(self.es_username, self.es_password),
        )

    def check_index_exists(self, index_name):
        """检查索引是否存在"""
        return self.es.indices.exists(index=index_name)

    def create_index(self, index_name):
        """创建索引，如果已存在，则询问是否删除并重新创建"""
        if self.check_index_exists(index_name):
            print(f"索引 {index_name} 已存在。")
            choice = input("是否要删除原有的数据，并创建一个同名的空Index？(y/n): ")
            if choice.lower() == 'y':
                self.es.indices.delete(index=index_name)
                self.es.indices.create(index=index_name)
                print(f"已删除并重新创建了索引 {index_name}。")
            else:
                print("保留现有索引。")
        else:
            self.es.indices.create(index=index_name)
            print(f"创建成功：{index_name}。")


# 2-2、灌库－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－
# from elasticsearch7 import Elasticsearch, helpers
# from TV_RAG_classes import TextKeywordExtractor

class ElasticsearchBulkInserter:
    def __init__(self, es_host, es_username, es_password, index_name):
        self.es = Elasticsearch(
            hosts=[es_host],
            http_auth=(es_username, es_password),
        )
        self.index_name = index_name
        self.extractor = TextKeywordExtractor()  # 实例化你的关键字提取器

    def insert_text(self, paragraphs):
        actions = [
            {
                "_index": self.index_name,
                "_source": {
                    "keywords": self.extractor.to_keywords(para),
                    "text": para
                }
            }
            for para in paragraphs
        ]

        result = helpers.bulk(self.es, actions)
        print("==========我是分割线 灌库结果===========")
        print(result)


# 3. 封装检索接口－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－
# from elasticsearch7 import Elasticsearch, helpers
# from TV_RAG_classes import TextKeywordExtractor

class ElasticsearchSearcher:
    def __init__(self, es_host, es_username, es_password, index_name):
        self.es = Elasticsearch(
            hosts=[es_host],
            http_auth=(es_username, es_password),
        )
        self.index_name = index_name
        self.extractor = TextKeywordExtractor()  # 实例化你的关键字提取器

    def search(self, query_string, top_n=10):
        # 使用关键字提取器处理查询字符串
        search_query = {
            "match": {
                "keywords": self.extractor.to_keywords(query_string)
            }
        }
        res = self.es.search(index=self.index_name, query=search_query, size=top_n)
        print("==========我是分割线 in search, match KW ===========")
        print(res)
        return [hit["_source"]["text"] for hit in res["hits"]["hits"]]

