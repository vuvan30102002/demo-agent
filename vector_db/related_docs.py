# from langchain_community.vectorstores import FAISS
# from langchain_community.embeddings import HuggingFaceBgeEmbeddings
# from sentence_transformers import CrossEncoder
# data_embedding = "quang_ne"
# model = HuggingFaceBgeEmbeddings(model_name="intfloat/multilingual-e5-base")
# db = FAISS.load_local(data_embedding,model,allow_dangerous_deserialization=True)
# reranking = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from sentence_transformers import CrossEncoder
data_embedding = "quang_ne"
model = HuggingFaceEmbeddings(model_name="D:\Fast-API\quang2\models\multilingual-e5-base")
db = FAISS.load_local(data_embedding,model,allow_dangerous_deserialization=True)
reranking = CrossEncoder("D:\Fast-API\quang2\models\ms-marco-MiniLM-L-6-v2")


