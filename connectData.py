import pyodbc
import pandas as pd
server = "DESKTOP-2O4N45Q\\SQLEXPRESS"
database = "Agent"
username = "quang"
password = "30102002"
connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}"
# try:
#     conn = pyodbc.connect(connection_string)
#     # query = "SELECT * FROM SinhVien"
#     # df_account = pd.read_sql(query,conn)
#     # print(df_account.head())
# except pyodbc.Error as e:
#     print(e)
# finally:
#     if conn:
#         conn.close()
def get_connect():
    try:
        conn = pyodbc.connect(connection_string)
        # query = "SELECT * FROM SinhVien"
        # df_account = pd.read_sql(query,conn)
        # print(df_account.head())
        return conn
    except pyodbc.Error as e:
        print(e)