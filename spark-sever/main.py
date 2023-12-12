from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import configparser
from sqlalchemy_utils import database_exists, create_database

# 创建 FastAPI 应用
app = FastAPI()

# 读取配置文件
config = configparser.ConfigParser()
config.read('config.ini')

# 获取数据库连接信息
db_host = config['database']['host']
db_port = config['database']['port']
db_user = config['database']['username']
db_pass = config['database']['password']
default_db_name = config['database']['database_name']

# 构建数据库连接 URI
default_db_uri = f"mysql+pymysql://{db_user}:{db_pass}@{db_host}:{db_port}/{default_db_name}"

# 创建默认数据库连接引擎
default_engine = create_engine(default_db_uri)

# 如果连接的默认数据库不存在，则创建
if not database_exists(default_engine.url):
    create_database(default_engine.url)

metadata = MetaData()

# 创建数据库表
users = Table(
    'users',
    metadata,
    Column('user_id', Integer, primary_key=True, autoincrement=True),
    Column('username', String(50), unique=True),
    Column('password', String(255)),
    Column('email', String(100), unique=True),
    Column('created_at', DateTime, default=datetime.now),
    Column('last_login', DateTime, default=datetime.now)
)

# 创建数据库会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=default_engine)


# 模型：用于输入数据验证
class UserCreate(BaseModel):
    username: str
    password: str
    email: str


# API 路由：用于创建用户
@app.post("/api/user/add")
async def create_user(user: UserCreate):
    db = SessionLocal()
    try:
        db.execute(users.insert().values(
            username=user.username,
            password=user.password,
            email=user.email
        ))
        db.commit()
        return {"message": "User created successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create user: {str(e)}")
    finally:
        db.close()


# API 路由：用于编辑用户
@app.put("/api/user/edit/{user_id}")
async def edit_user(user_id: int, user: UserCreate):
    db = SessionLocal()
    try:
        db.execute(users.update().where(users.c.user_id == user_id).values(
            username=user.username,
            password=user.password,
            email=user.email
        ))
        db.commit()
        return {"message": "User updated successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update user: {str(e)}")
    finally:
        db.close()


# API 路由：用于删除用户
@app.delete("/api/user/del/{user_id}")
async def delete_user(user_id: int):
    db = SessionLocal()
    try:
        db.execute(users.delete().where(users.c.user_id == user_id))
        db.commit()
        return {"message": "User deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete user: {str(e)}")
    finally:
        db.close()


# API 路由：用于获取所有用户信息
@app.get("/api/user/getUser")
async def get_users():
    db = SessionLocal()
    query = db.query(users).all()
    db.close()
    return query

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
