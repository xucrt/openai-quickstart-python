import chromadb
from chromadb.config import Settings

# 初始化客户端
client = chromadb.Client(Settings())

# 获取所有 collections 的列表
collections = client.list_collections()
print(collections)

client.delete_collection(name="demo")