# Lesson 5. RAG 系统的基本搭建流程
# 搭建过程：
# 1. 文档加载，并按一定条件切割成片段--参考AGI_lesson_5-1.py or TV_RAG_embedding.py
# 2. 将切割的文本片段灌入检索引擎
# 3. 封装检索接口
# 4. 构建调用流程：Query -> 检索 -> Prompt -> LLM -> 回复

# 2-2、实现关键字检索
from TV_1_RAG_classes import ElasticsearchSearcher

# 这里的索引名需要手动贴过来
index = "xuc_index_t0421"

es_search = ElasticsearchSearcher(index)

# results = es_search.search("what is dell?", 10)
#
# for r in results:
#     print(r+"\n")

prompt_template = """
You are a question-and-answer robot.
Your task is to answer user questions based on the given [known information] and make sure you reviewed all lines in [known information].
Ensure that your reply is completely based on the given [known information]. Do not make up answers.
If the given [known information] is not sufficient to answer the user's question, please reply directly with "I cannot answer your question."
If your response is not 'I cannot answer your question.' then you must give me the original contents that you found.
If your response is "I cannot answer your question." then you must tell me the reseaon?

[known information]:
__INFO__

[user questions]：
__QUERY__

Answer in Chinese only.
"""

# user_query = "how many parameters does llama 2 have?"
# ⇒正确回答如下：
#     ===回复===
#     我无法回答您的问题。
# user_query = "How many known issues you can found?"

user_query = "How many Cloud Foundation version you can found?"

# 1. 检索
search_results = es_search.search(user_query)

# 2. 构建 Prompt
from TV_1_RAG_classes import OpenAICompletion
from TV_1_RAG_classes import PromptBuilder

get_OpAI = OpenAICompletion()
prmpt = PromptBuilder(prompt_template)

prompt = prmpt.build_prompt(info=search_results, query=user_query)
print("===Prompt===")
print(prompt)

# 3. 调用 LLM
response = get_OpAI.get_completion(prompt)

print("===回复===")
print(response)
