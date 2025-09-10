import json, requests, os
from dotenv import load_dotenv
load_dotenv()
URL = os.getenv("URL")
KEY = os.getenv("KEY")

def rewrite_message_func(user_message,history):
    prompt = f"""
# TUTORIAL
You are an expert in rewriting the latest user question based on the conversation history between the user and the assistant. The rewritten question will be used in the retrieval system. This field is mainly related to the promotion program of a nationwide Shogun restaurant chain.
Follow these steps to ensure that the rewritten question is semantically correct and complete:
- Step 1: Check if the question contains abbreviations, missing punctuation, spelling errors or grammatical errors.
+ Expand or correct only commonly used abbreviations or spelling-related abbreviations (e.g. "toi" → "me", "k" → "no", "dc" → "okay", "tvv" -> "consultant").
- Step 2: Analyze the conversation history to understand the context of previous questions.
- Step 3: Rewrite the user's most recent question as:
+ Completely independent (include context if necessary).
+ Keep the user's original **intention**, **no clarification** or **confirmation**.
+ Avoid ambiguity.

# EXAMPLES
## Example 1
U: Bên mik co những ctkm nào?
A: Chúng tôi có các chương trình khuyến mãi... Quý khách muốn tìm hiểu về loại chương trình khuyến mãi nào?
U: chương trình sinh nhật
Rewritten question: Có những chương trình khuyến mãi nào ở Shogun?

## Example 2
U: Cho mik xem tt menu bên bạn
Rewritten question: Bên bạn có những loại menu nào?

## Notes:
- "hnay" is hôm nay.

# START
* Strict rules:
- Do not answer user questions.
- Do not rewrite user questions as clarifying questions (e.g. "Are you asking about...?").

- Only rephrase the question when necessary to clarify or add missing context. If the latest question is unrelated to the previous conversation, leave it as is.

- If the latest user's question is a greeting (e.g. "hi", "hello", "hi", "alo", "hello", etc.), do not rephrase. Return the question as is.

Rephrase the most recent user's question in the language of the latest user's question, following the GUIDE and EXAMPLE provided above:
-- start_chat_history --
{history}
-- end_chat_history --
Latest user's question: "{user_message}"
Rephrased question:
"""
    url = URL
    headers = {
        "Authorization" : KEY,
        "Content-Type" : "application/json"
    }
    payload = json.dumps({
        "model" : "Llama-3.3-70B-Instruct",
        "messages" : [{
            "role" : "user",
            "content" : prompt
        }],
        "max_tokens" : 100,
        "temperature" : 0.1,
        "top_p" : 0.95
    })
    response = requests.post(url=url, headers=headers, data=payload)
    result = response.json().get("choices", [])[0]["message"]["content"].strip()
    return result