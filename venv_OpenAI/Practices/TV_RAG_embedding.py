# Lesson 5. RAG 系统的基本搭建流程
# 搭建流程：
# 1. 文档加载，并按一定条件切割成片段
# 2. 将切割的文本片段灌入检索引擎
# 3. 封装检索接口
# 4. 构建调用流程：Query -> 检索 -> Prompt -> LLM -> 回复

# ↓↓↓↓ 20240314 移至classes ↓↓↓↓
# 1、文档的加载与切割
# 需要先安装 pdf 解析库
# pip install pdfminer.six
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer

def extract_text_from_pdf(filename, page_numbers=None, min_line_length=1):
    '''从 PDF 文件中（按指定页码）提取文字'''
    paragraphs = []
    buffer = ''
    full_text = ''
    # 提取全部文本
    for i, page_layout in enumerate(extract_pages(filename)):
        # 如果指定了页码范围，跳过范围外的页
        if page_numbers is not None and i not in page_numbers:
            continue
        for element in page_layout:
            if isinstance(element, LTTextContainer):
                full_text += element.get_text() + '\n'
    # 按空行分隔，将文本重新组织成段落
    lines = full_text.split('\n')
    for text in lines:
        if len(text) >= min_line_length:
            buffer += (' '+text) if not text.endswith('-') else text.strip('-')
        elif buffer:
            paragraphs.append(buffer)
            buffer = ''
    if buffer:
        paragraphs.append(buffer)
    return paragraphs

paragraphs_dell = extract_text_from_pdf(f"E:/Programs/materials/h15201-data-protector-for-z-systems-zdp-essentials.pdf", page_numbers=[1], min_line_length=2)
# paragraphs_telus = extract_text_from_pdf("../materials/TELUS_Contributor Agreement_Media Search.pdf",  page_numbers=[1], min_line_length=2)
# paragraphs_vmware = extract_text_from_pdf("../materials/vmware-vsphere-80-release-notes.pdf",  page_numbers=[1], min_line_length=2)

# print("==========我是分割线 PDF抽取结果↓↓↓===========")
# for para in paragraphs_dell[:5]:
#     print(para+"\n")
# print("==========我是分割线 PDF抽取结果↓↓↓===========")
# for para in paragraphs_telus[:5]:
#     print(para+"\n")
# print("==========我是分割线 PDF抽取结果↓↓↓===========")
# for para in paragraphs_vmware[:5]:
#     print(para+"\n")

"""
↓↓↓↓ 20240314 移至classes ↓↓↓↓
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
        # 初始化停用词和词干提取器
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
"""

"""
20:39 2024/03/11
xxx！！！注意！！！ 不能将结果转换为【字符串】并连接！！！xxx
# paragraphs = "\n\n".join(["\n\n".join(paragraphs_dell), "\n\n".join(paragraphs_telus), "\n\n".join(paragraphs_vmware)]) + f"\n\n==========完了==========="
因为，如果Elasticsearch接收到的参数是string，Elasticsearch的算法会自动把这个字符串转换成一个单个字母的列表。
比如说，上传一个字符串"Yes"，Elasticsearch会把它拆解为"Y"、"e"、"s"。
而上传一个列表["Yes"]，Elasticsearch就会将"Yes"作为列表中的第一项存储起来。
使用pdfminer拆解后，文本的类型是一个列表；该列表中的各项是单词，而不是字母。
所以正确的文本结合方式是，直接将列表结合↓↓↓↓，而不是转换成文字列。
# paragraphs = paragraphs_dell + paragraphs_telus + paragraphs_vmware
"""


# paragraphs = paragraphs_dell + paragraphs_telus + paragraphs_vmware
paragraphs = paragraphs_dell
print(paragraphs[0-15])

paragraphs.append("\n\n==========完了===========")
print(type(paragraphs))

# fifth = paragraphs[-1]
# print(fifth)
# print(paragraphs.index("\n\n==========完了==========="))
