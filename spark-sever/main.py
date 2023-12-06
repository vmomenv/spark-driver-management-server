from fastapi import FastAPI
from config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME, DB_PORT
import mysql.connector

app = FastAPI()


# 连接到 MySQL 数据库
db = mysql.connector.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME,
    port=DB_PORT
)
cursor = db.cursor()

@app.get("/")
async def read_root():
    return {"Hello": "World"}

# 在这里添加其他路由和逻辑来处理用户表、驱动表等操作

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
