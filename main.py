from fastapi import FastAPI, HTTPException, Request
from typing import Annotated
from pydantic import BaseModel
import pyodbc
import pandas as pd
import connectData
from vector_db.query_answer import get_answer
from vector_db.rewrite_message import rewrite_message_func
from collections import deque



app = FastAPI()
conn = connectData.get_connect()  # kết nối tới cơ sở dữ liệu
# app.include_router(connectData)

# @app.get("/sinhvien/{id}")
# async def readSinhVien(id : int):
#     query = f"SELECT * FROM SinhVien WHERE MaSV = {id}"
#     conn = connectData.get_connect()
#     df_read = pd.read_sql(query,conn)
#     if not df_read.empty:
#         return {"message": "có", "data": df_read.to_dict(orient="records")}
#     else:
#         return {"message": "không"}


class registerRequest(BaseModel):
    user_name : str
    pass_word : str

class loginRequest(BaseModel):
    user_name : str
    pass_word : str

import hashlib
def md5_password(pass_word : str) -> str:
    return hashlib.md5(pass_word.encode()).hexdigest()

@app.post("/register")
async def register_user(user:registerRequest):
    hash_pass = md5_password(user.pass_word)
    user_name = user.user_name
    query = f"INSERT INTO users(user_name,pass_word) VALUES(N'{user_name}','{hash_pass}')"
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()
    return {
        "message" : "Đăng ký thành công",
        "user_name" : user.user_name,
        "pass_word" : hash_pass
    }

from starlette.middleware.sessions import SessionMiddleware
app.add_middleware(SessionMiddleware, secret_key = "quang-123")
@app.post("/login")
async def login(user:loginRequest, request:Request):
    # conn = connectData.get_connect()
    cursor = conn.cursor()
    hash_password = md5_password(user.pass_word)
    user_name = user.user_name
    query = f"SELECT pass_word,user_id FROM users WHERE user_name = '{user_name}'"
    cursor.execute(query)
    result = cursor.fetchone()
    if not result[0]:
        raise HTTPException(status_code=400, detail="User này không tồn tại")
    if hash_password != result[0]:
        raise HTTPException(status_code=400,detail=f"Mật khẩu không đúng: {result[0]}")
    else:
        request.session["user"] = result[1]
    return {
        "message" : "Đăng nhập thành công",
        "user_name" : user_name,
        "session" : request.session.get("user")
    }
@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return {"message" : "Đã logout thành công"}
        

# history = deque(maxlen=3)
from collections import deque
import pandas as pd
from fastapi import Request

# history = deque(maxlen=3)

@app.get("/question-answer/{question}")
async def ask(question: str, request: Request):
    session_user_id = request.session.get("user")
    if not session_user_id:
        return {"message": "Bạn cần đăng nhập mới có thể sử dụng"}

    # lấy 6 bản ghi mới nhất từ DB của user_id hiện tại
    query = f"""
    SELECT user_id, role, message
    FROM (
        SELECT TOP 6 user_id, role, message, create_at
        FROM history
        WHERE user_id = {session_user_id}
        ORDER BY create_at DESC
    ) AS sub
    ORDER BY create_at ASC
    """
    df_read = pd.read_sql(query, conn)
    history_q = df_read.to_dict()

    role = history_q.get("role", {})
    message = history_q.get("message", {})

    # build lịch sử thành dạng list[dict]
    history_list = []
    temp = {}
    for i in range(len(role)):
        r = role.get(i)     # key trong dict là int
        m = message.get(i)
        if r == "user":
            temp = {"user": m}
        elif r == "agent" and temp:
            temp["agent"] = m
            history_list.append(temp)
            temp = {}
    if temp:  # tránh sót nếu cuối cùng là user chưa có agent
        history_list.append(temp)

    # lưu câu hỏi & câu trả lời vào DB
        # lấy lịch sử tạm trong bộ nhớ
    # history_list = list(history)
    rewrite, answer = get_answer(question, history_list)
    # history.append({"user_message": rewrite, "bot": answer})


    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO history(user_id, role, message) VALUES (?, ?, ?)",
        (session_user_id, "user", rewrite)
    )
    cursor.execute(
        "INSERT INTO history(user_id, role, message) VALUES (?, ?, ?)",
        (session_user_id, "agent", answer)
    )
    conn.commit()  # commit trên connection, không phải cursor

    return {
        "user_question": rewrite,
        "bot_answer": answer,
        "history": history_list
    }