from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import re

loader = PyPDFLoader("D:\Fast-API\quang2\data\Chương trình khuyến mãi.pdf")
docs = loader.load()

def chunk_by_structure(text):
    # Tách theo heading 1,2,3,4 hoặc I, II,...
    # pattern = r"(?=\n\d+\.\s|\n[IVXLCDM]+\.\s)" # nó chia cả số la mã và số thường
    pattern = r"(?=\n[IVXLCDM]+\.\s)" # chỉ chia theo số la mã
    chunks = re.split(pattern,text)
    return chunks
# print(type(docs))
knowledge = []
for i,doc in enumerate(docs,0):
    texts = doc.page_content
    knowledge.append(texts)

full_text = "\n".join(knowledge)   # nối list thành 1 chuỗi

chunks = chunk_by_structure(full_text)
# for i,chunk in enumerate(chunks,1):
#     print(f"\n--- Chunk {i} ---\n{chunk}...")

print((chunks))
