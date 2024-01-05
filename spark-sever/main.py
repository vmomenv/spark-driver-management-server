import shutil

from fastapi import FastAPI, Form, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import configparser
from sqlalchemy_utils import database_exists, create_database
from fastapi import File, UploadFile
from fastapi.responses import JSONResponse
from pathlib import Path
import os
import json
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
from typing import List, Dict


@app.get("/api/user/getUser", response_model=List[dict])
async def get_users():
    db = SessionLocal()
    try:
        query = db.query(users).all()
        user_data = [{column: getattr(user, column) for column in users.columns.keys()} for user in query]
        return user_data
    finally:
        db.close()
@app.post("/api/permission/getMenu")
def get_menu() -> Dict:
    menu = [
        {
            "path": "/home",
            "name": "home",
            "label": "首页",
            "icon": "s-home",
            "url": "Home.vue"
        },
        {
            "path": "/file",
            "name": "file",
            "label": "文件管理",
            "icon": "files",
            "url": "File.vue"
        },
        {
            "path": "/user",
            "name": "user",
            "label": "用户管理",
            "icon": "s-custom",
            "url": "User.vue"
        },
        {
            "label": "其他",
            "icon": "location",
            "children": [
                {
                    "path": "/page1",
                    "name": "page1",
                    "label": "页面1",
                    "icon": "setting",
                    "url": "PageOne.vue"
                },
                {
                    "path": "/page2",
                    "name": "page2",
                    "label": "页面2",
                    "icon": "setting",
                    "url": "PageTwo.vue"
                }
            ]
        }
    ]

    response_data = {
        "code": 20000,
        "data": {
            "menu": menu,
            "token": "114514",  # Replace this with your actual token
            "message": "获取成功"
        }
    }

    return response_data
# 文件上传
@app.post("/api/upload_driver/")
async def upload_driver(
        driver_file: UploadFile = File(...),
        hardware_type: str = Form(...),
        package_name: str = Form(...),
        version: str = Form(None),
        size: int = Form(None),
        description: str = Form(None),
        applicable_devices: str = Form(None),
        system_version: str = Form(None)
):
    # Define the directory path based on hardware_type and package_name
    driver_dir = f"../spark-driver-repo/{hardware_type}/{package_name}/"
    json_file_path = f"{driver_dir}/data.json"

    # Create directories if they don't exist
    Path(driver_dir).mkdir(parents=True, exist_ok=True)

    try:
        # Save the uploaded file to the specified directory
        file_path = os.path.join(driver_dir, driver_file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(driver_file.file, buffer)

        # Optionally, create a JSON object to store metadata if needed
        metadata = {
            "hardware_type": hardware_type,
            "package_name": package_name,
            "version": version,
            "size": size,
            "description": description,
            "applicable_devices": applicable_devices,
            "system_version": system_version
        }

        # Save metadata to a JSON file in the same directory if needed
        if any(metadata.values()):
            with open(json_file_path, "w") as json_file:
                json.dump(metadata, json_file)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")

    return {
        "message": "File uploaded successfully",
        "filename": driver_file.filename,
        "hardware_type": hardware_type,
        "package_name": package_name,
        "version": version,
        "size": size,
        "description": description,
        "applicable_devices": applicable_devices,
        "system_version": system_version
    }


@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    return {"filename": file.filename}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
