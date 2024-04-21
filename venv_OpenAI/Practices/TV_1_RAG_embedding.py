# Lesson 5. RAG 系统的基本搭建流程
# 搭建过程：
# 1. 文档加载，并按一定条件切割成片段--参考AGI_lesson_5-1.py or TV_RAG_embedding.py
# 2. 将切割的文本片段灌入检索引擎
# 3. 封装检索接口
# 4. 构建调用流程：Query -> 检索 -> Prompt -> LLM -> 回复

# 1、文档的加载与切割
# 需要先安装 pdf 解析库
# pip install pdfminer.six

from TV_1_RAG_classes import PDFTextExtractor
from TV_1_RAG_classes import FileNameModifier
from TV_1_RAG_classes import TextKeywordExtractor

modifier = FileNameModifier("E:/Programs/materials")
modifier.replace_spaces_with_underscores()

# paragraphs_dell_extr = PDFTextExtractor(f"E:/Programs/materials/Dell_XC_Family_datasheet.pdf", page_numbers=[1], min_line_length=2)
paragraphs_dell_extr = PDFTextExtractor(f"E:/Programs/materials/Dell_XC_Family_datasheet.pdf")
paragraphs_dell = paragraphs_dell_extr.extract_text()

print("==========我是分割线 PDF抽取结果↓↓↓===========")
print("paragraphs_dell_extr:", type(paragraphs_dell_extr))
print("paragraphs_dell type:", type(paragraphs_dell), "paragraphs_dell len:", len(paragraphs_dell))
# for para in paragraphs_dell[:5]:
#      print(para+"\n")


# paragraphs_vmware_extr = PDFTextExtractor(f"E:/Programs/materials/vmware-cloud-foundation-311-on-dell-emc-vxrail-release-notes.pdf", page_numbers=[1], min_line_length=2)
paragraphs_vmware_extr = PDFTextExtractor(f"E:/Programs/materials/vmware-cloud-foundation-311-on-dell-emc-vxrail-release-notes.pdf")
paragraphs_vmware = paragraphs_vmware_extr.extract_text()

print("==========我是分割线 PDF抽取结果↓↓↓===========")
print("paragraphs_vmware_extr:", type(paragraphs_vmware_extr))
print("paragraphs_vmware:", len(paragraphs_vmware))
# for para in paragraphs_vmware[:5]:
#      print(para+"\n")


# paragraphs_nuta_extr = PDFTextExtractor(f"E:/Programs/materials/fy19q4_1065-ss-xc-appliance-spec-sheet-120718.pdf", page_numbers=[1], min_line_length=2)
paragraphs_nuta_extr = PDFTextExtractor(f"E:/Programs/materials/fy19q4_1065-ss-xc-appliance-spec-sheet-120718.pdf")
paragraphs_nuta = paragraphs_vmware_extr.extract_text()

print("==========我是分割线 PDF抽取结果↓↓↓===========")
print(paragraphs_nuta_extr)
print("paragraphs_nuta:", len(paragraphs_nuta))
# for para in paragraphs_nuta[:5]:
#      print(para+"\n")


paragraphs = paragraphs_nuta + paragraphs_vmware + paragraphs_dell
paragraphs.append("\n\n==========完了===========")
print("==========我是分割线 PDF抽取结果↓↓↓===========")
print("paragraphs type:", type(paragraphs), "paragraphs len:", len(paragraphs))


# 分解文本
extractor = TextKeywordExtractor()

# 将要被灌入库中的内容
print("==========我是分割线 灌库前的文本===========")
print(paragraphs[-15])
# for para in paragraphs[0-15]:
#     print(extractor.to_keywords(para))
