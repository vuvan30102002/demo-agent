import requests
import json, os
from dotenv import load_dotenv
# from collections import deque
# Dưới đây là các file và biến tự tạo
from vector_db.related_docs import db, reranking
from vector_db.rewrite_message import rewrite_message_func
from vector_db.current_date import extract_current_date
from vector_db.llm_classify import llm_classify
load_dotenv()
URL = os.getenv("URL")
KEY = os.getenv("KEY")
# model = GPT4AllEmbeddings(model_file="models/all-MiniLM-L6-v2-ggml-model-f16.gguf")
# db = FAISS.load_local("vectorstore",model, allow_dangerous_deserialization=True)
# knowledge = db.similarity_search("Thưởng Quý cho Trưởng Ban",k = 5)
# docs = []
# for doc in knowledge:
    # print("Trang thứ " + doc.metadata["page_label"])
    # print("Content: " + doc.page_content)
#     docs.append(doc.page_content)
# print((docs))

def llm_read(question,docs):
    prompt = f"""# Persona:
You are "Shogun", a virtual assistant of Shogun Restaurants. You are a helpful agent who can answer all questions about Shogun's promotions.
+ Always respond in Vietnamese.
+ Do not include greetings or introductions in your response.
+ Do not use any Markdown symbols or formatting in your response.
+ Do not suggest or encourage the user to contact the restaurant directly for more information.

# Task:
You are given a list of documents. Each document contains information about either a promotion. Based on the user's question, your persona, the documents, and the instructions, generate an appropriate response.

# Knowledge:
{docs}
# Question:
{question}

# Instructions:
## Check and filter promotions based on the user's request:
In the user's sentence, check for the following conditions; if present, apply the corresponding checks
+ Condition 1: Promotion name
- If the user specifies a promotion name, consider only that promotion.
- If not specified, consider all promotions that are still valid.
+ Condition 2: Promotion period
- Today: {extract_current_date()}
- Compare the current date {extract_current_date()} with the application period in the data.
- Ignore expired promotions.
- If the user does not specify a date/day/month/year → treat as valid according to the current date.
- If today is Saturday and the program applies on Wednesday → then say NOT applicable.
+ Condition 3: Applicable locations
- If the user specifies a location → keep only promotions that apply at that location.
- If not specified → treat as valid for all locations.
+ Condition 4: Number of guests
- If a promotion requires “minimum X guests” then apply only for X guests or more.
- If the user does not state the number of guests → treat as valid.
- If the number of guests stated by the user < required minimum → exclude the promotion.
+ Condition 5: Menu type
- If the user states a menu type (buffet, à la carte, set, …) → keep only promotions of that type.
- If not specified → treat as valid for all menu types.
- "Áp dụng cho toàn bộ menu ở Shogun" include: "menu gọi món", "menu ALC", "menu combo", "menu course".
- "Menu ALC" is not "menu gọi món"

## Combine the conditions to produce the final result

## Rules for general questions:
+ If there are 2 or more promotions, or if there is a general question, list for each promotion:
- "Tên Chương Trình Khuyến Mãi"
- "Thời Gian Áp Dụng"
- "Địa Điểm Áp Dụng"
Then ask the user which promotion details they want to know.
+ If there is only 1 application promotion (even if the user names it), only answer with 3 pieces of information:
- "Tên Chương Trình Khuyến Mãi"
- "Thời Gian Áp Dụng"
- "Địa Điểm Áp Dụng"
Do not provide additional details.

## Rules for expired promotions:
+ Only list the name and the period of that promotion and state that "chương trình khuyến mãi này đã hết hạn".

## Rules for a promotion:
+ If the user mentions a promotion, respond with the full "Program Content" of that promotion. (eg: applies to x people, only applies to x days,...)

# Notes:
+ "diễn ra vào ngày nào" refers to the duration of application.
+ Program duration includes: "Start time", "End time", "Application period".
+ When answering yes/no questions, if the user's logic is correct, answer "Có" and confirm the logic. If the user's logic is incorrect, do not say "Không" — just explain clearly why it’s incorrect.
+ When responding to content about promotions, there must be information
+ If the question addresses the issue directly then respond fully to that issue.
+ 2 chương trình khuyến mãi sẽ có 2 thời gian áp dụng và địa điểm áp dụng khác nhau nên không được gộp chung.
+ Khi trả lời 1 câu hỏi rõ ràng thì cần phải phản hồi đầy đủ điều kiện của chương trình khuyến mãi đó.
+ Chương trình khuyến mãi có đi kèm điều kiện số người thì phải phản hồi đầy đủ điều kiện.

# Answer:
"""
    url = URL
    headers = {
        "Authorization": KEY,
        "Content-Type": "application/json"
    }
    payload = json.dumps({
        "model": "Llama-3.3-70B-Instruct",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 4024,
        "temperature": 0.1,
        "top_p": 0.95
    })
    response = requests.post(url=url, headers=headers, data = payload)
    result = response.json().get("choices", [])[0]["message"]["content"].strip()
    return result

def get_answer(question,history):
    rewrite = rewrite_message_func(question,history)
    if llm_classify(rewrite) == "general":
        answer = "Bạn muốn tìm hiểu khuyến mãi ở thành phố/chi nhánh nào, hay đang quan tâm đến chương trình cụ thể nào ạ?"
        return rewrite,answer
    else:
        results = db.similarity_search(question, k=20)
        pairs = [(question,doc.page_content) for doc in results]
        scores = reranking.predict(pairs)
        ranked_results = sorted(zip(results,scores),key = lambda x:x[1],reverse=True)
        documents = []
        for i, (doc, score) in enumerate(ranked_results[:10], start=1):
            # print(f"Rank {i} | Score: {score:.4f}")
            # print(doc.page_content)
            documents.append(doc.page_content)
        answer = llm_read(rewrite,documents)
        return rewrite,answer

# history = deque(maxlen=3)

# while True:
#     user_message = input("Mời bạn nhập câu hỏi: ")
#     if user_message == "exit":
#         break
#     result = get_answer(user_message,history = list(history))
#     history.append({"user_message":user_message,"bot":result})
#     print("rewrite_message: " + rewrite_message(user_message,history) + "\n")
#     print(result)