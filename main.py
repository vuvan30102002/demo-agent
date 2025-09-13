from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import pandas as pd
import connectData
from vector_db.query_answer import get_answer
from vector_db.rewrite_message import rewrite_message_func
from starlette.middleware.sessions import SessionMiddleware
import hashlib

app = FastAPI()
conn = connectData.get_connect()  # kết nối MySQL

class registerRequest(BaseModel):
    user_name: str
    pass_word: str

class loginRequest(BaseModel):
    user_name: str
    pass_word: str

def md5_password(pass_word: str) -> str:
    return hashlib.md5(pass_word.encode()).hexdigest()

@app.post("/register")
async def register_user(user: registerRequest):
    hash_pass = md5_password(user.pass_word)
    cursor = conn.cursor()
    query = "INSERT INTO users(user_name, pass_word) VALUES (%s, %s)"
    cursor.execute(query, (user.user_name, hash_pass))
    conn.commit()
    return {
        "message": "Đăng ký thành công",
        "user_name": user.user_name,
        "pass_word": hash_pass
    }

app.add_middleware(SessionMiddleware, secret_key="quang-123")

@app.post("/login")
async def login(user: loginRequest, request: Request):
    cursor = conn.cursor()
    hash_password = md5_password(user.pass_word)
    query = "SELECT pass_word, user_id FROM users WHERE user_name = %s"
    cursor.execute(query, (user.user_name,))
    result = cursor.fetchone()

    if not result:
        raise HTTPException(status_code=400, detail="User này không tồn tại")

    if hash_password != result[0]:
        raise HTTPException(status_code=400, detail="Mật khẩu không đúng")
    else:
        request.session["user"] = result[1]

    return {
        "message": "Đăng nhập thành công",
        "user_name": user.user_name,
        "session": request.session.get("user")
    }

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return {"message": "Đã logout thành công"}

@app.get("/question-answer/{question}")
async def ask(question: str, request: Request):
    session_user_id = request.session.get("user")
    if not session_user_id:
        return {"message": "Bạn cần đăng nhập mới có thể sử dụng"}

    # Lấy 6 bản ghi mới nhất
    query = f"""
        SELECT user_id, role, message
        FROM history
        WHERE user_id = {session_user_id}
        ORDER BY create_at DESC
        LIMIT 6
    """
    df_read = pd.read_sql(query, conn)

    # đảo ngược để ASC theo create_at
    df_read = df_read.iloc[::-1]

    role = df_read["role"].to_dict()
    message = df_read["message"].to_dict()

    history_list = []
    temp = {}
    for i in range(len(role)):
        r = role.get(i)
        m = message.get(i)
        if r == "user":
            temp = {"user": m}
        elif r == "agent" and temp:
            temp["agent"] = m
            history_list.append(temp)
            temp = {}
    if temp:
        history_list.append(temp)

    # lấy câu trả lời
    rewrite, answer = get_answer(question, history_list)

    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO history(user_id, role, message) VALUES (%s, %s, %s)",
        (session_user_id, "user", rewrite)
    )
    cursor.execute(
        "INSERT INTO history(user_id, role, message) VALUES (%s, %s, %s)",
        (session_user_id, "agent", answer)
    )
    conn.commit()

    return {
        "user_question": rewrite,
        "bot_answer": answer,
        "history": history_list
    }
