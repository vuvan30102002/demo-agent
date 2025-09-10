from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import CrossEncoder
import re
from langchain.schema import Document
# Đọc file PDF
path = "data"
loader = DirectoryLoader(path=path, glob="*.pdf", loader_cls=PyPDFLoader)
documents = loader.load()

# Chia nhỏ
# text_splitter = RecursiveCharacterTextSplitter(
#     chunk_size=512, chunk_overlap=50,
#     separators=["\n\n", "\n", ".", " ", ""]
# )
# print((documents))
# new_docs = []
# for doc in documents:
#     txt = doc.page_content.replace("\r\n","\n").replace("\r","\n").strip()
#     txt = re.sub(r'(?<!\n)\n(?!\n)', '', txt)
#     paragraphs = [p.strip() for p in txt.split("\n\n") if p.strip()]
#     for o in paragraphs:
#         new_docs.append(Document(page_content=o, metadata=doc.metadata))
# print(new_docs)
# text_splitter = RecursiveCharacterTextSplitter(
#     separators="\n\n",
#     chunk_size = 10000
# )
# docs = text_splitter.split_documents(new_docs)
def chunk_by_structure(text):
    # Tách theo heading 1,2,3,4 hoặc I, II,...
    # pattern = r"(?=\n\d+\.\s|\n[IVXLCDM]+\.\s)" # nó chia cả số la mã và số thường
    pattern = r"(?=\n[IVXLCDM]+\.\s)" # chỉ chia theo số la mã
    chunks = re.split(pattern,text)
    return chunks
# print(type(docs))
knowledge = []
for i,doc in enumerate(documents,0):
    texts = doc.page_content
    knowledge.append(texts)

full_text = "\n".join(knowledge)   # nối list thành 1 chuỗi

chunks = chunk_by_structure(full_text)
# for i,chunk in enumerate(chunks,1):
#     print(f"\n--- Chunk {i} ---\n{chunk}...")

# docs = chunks
# docs ở đây đang là list[string] bắt buộc phải chuyển về list[Document]
docs = [Document(page_content=c.strip(), metadata = {"source" : "custom_chunk"}) for c in chunks if c.strip()]

# Dùng E5 sẵn có từ HuggingFaceEmbeddings
embedding_model = HuggingFaceEmbeddings(model_name="intfloat/multilingual-e5-base")

# Tạo FAISS index, docs ở đây phải nhận đầu vào là list[Document]
db = FAISS.from_documents(docs, embedding=embedding_model)
db.save_local("quang_ne")

# Sau này có thể truy vấn
# Lấy top 5 chunk kèm điểm similarity
# query = "Chương trình khuyến mãi sinh nhật quý 3 có gì"
# results = db.similarity_search(query, k=20)

# # for i, (doc, score) in enumerate(results, start=1):
# #     print(f"Chunk {i} | Score: {score:.4f}")
# #     print(doc.page_content[:200], "\n")

# reranking = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
# pairs = [(query, doc.page_content) for doc in results]

# scores = reranking.predict(pairs)
# ranked_results = sorted(zip(results,scores),key=lambda x: x[1], reverse=True)
# for i, (doc, score) in enumerate(ranked_results[:5], start=1):
#     print(f"Rank {i} | Score: {score:.4f}")
#     print(doc.page_content[:200], "\n")
