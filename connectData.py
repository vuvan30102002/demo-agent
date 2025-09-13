# import pyodbc
# import pandas as pd
# server = "DESKTOP-2O4N45Q\\SQLEXPRESS"
# database = "Agent"
# username = "quang"
# password = "30102002"
# connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}"
# def get_connect():
#     try:
#         conn = pyodbc.connect(connection_string)
#         return conn
#     except pyodbc.Error as e:
#         print(e)

import mysql.connector

# Thông tin kết nối
config = {
    "host": "localhost",     # Địa chỉ server MySQL (VD: "127.0.0.1")
    "user": "root",          # Tên user MySQL
    "password": "",  # Mật khẩu user MySQL
    "database": "agent_promotion"   # Tên database cần kết nối
}
def get_connect():
    try:
        # Kết nối tới MySQL
        conn = mysql.connector.connect(**config)
        return conn
    except mysql.connector.Error as err:
        print(f"Lỗi: {err}")

    finally:
        # Đóng kết nối
        if 'conn' in locals() and conn:
            conn.close()