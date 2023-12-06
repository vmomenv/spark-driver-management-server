# main.py
from fastapi import FastAPI, HTTPException
import mysql.connector
from config import DB_CONFIG

app = FastAPI()

# 连接到 MySQL 数据库
db = mysql.connector.connect(**DB_CONFIG)
cursor = db.cursor()

# 示例路由 - 获取用户信息
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    query = "SELECT * FROM users WHERE id = %s"
    cursor.execute(query, (user_id,))
    user = cursor.fetchone()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user": user}

# 示例路由 - 创建新用户
@app.post("/users/")
async def create_user(name: str):
    query = "INSERT INTO users (name) VALUES (%s)"
    cursor.execute(query, (name,))
    db.commit()
    return {"message": "User created successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
