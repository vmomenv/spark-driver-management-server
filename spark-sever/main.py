from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from setDB import users, metadata  # 导入已定义的数据库表和元数据
import configparser

app = FastAPI()

# 读取数据库配置信息
config = configparser.ConfigParser()
config.read('config.ini')

db_host = config['database']['host']
db_port = config['database']['port']
db_user = config['database']['username']
db_pass = config['database']['password']
default_db_name = config['database']['database_name']

# 构建数据库连接 URI
DATABASE_URL = f"mysql+pymysql://{db_user}:{db_pass}@{db_host}:{db_port}/{default_db_name}"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 模型：用于输入数据验证
class UserCreate(BaseModel):
    username: str
    password: str
    email: str

# API 路由：用于创建用户
@app.post("/users/")
async def create_user(user: UserCreate):
    db = SessionLocal()
    try:
        # 插入用户数据到数据库表中
        db.execute(users.insert().values(
            username=user.username,
            password=user.password,
            email=user.email,
            created_at='timestamp_here',
            last_login='timestamp_here'
        ))
        db.commit()
        return {"message": "User created successfully"}
    except Exception as e:
        db.rollback()
        return {"message": f"Failed to create user: {str(e)}"}
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)