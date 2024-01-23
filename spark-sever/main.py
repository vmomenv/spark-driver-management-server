import shutil
from itertools import groupby

from fastapi import FastAPI, Form, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime,select
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

pci_hardware = Table(
    'pci_hardware',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('vendor', String(50)),
    Column('vendor_name', String(255)),
    Column('device_id', String(50)),
    Column('device_name', String(255)),
    Column('sub_vendor', String(50)),
    Column('sub_device', String(50)),
    Column('sub_system_name', String(255)),
    Column('entry_id', String(50)),
)

# 将数据库查询结果转为 JSON 格式

# 标准解析逻辑
def parse_pci_hardware_data(rows):
    grouped_data = groupby(rows, key=lambda x: (x["vendor"], x["sub_device"]))
    result = []

    for (vendor, sub_device), vendor_rows in grouped_data:
        vendor_rows = list(vendor_rows)

        entry = {
            "value": vendor,
            "label": vendor_rows[0]["vendor_name"],
        }

        device_entries = []

        for row in vendor_rows:
            if row["device_id"]:
                device_entry = {
                    "value": row["device_id"],
                    "label": row["device_name"],
                }

                if row["sub_device"]:
                    sub_entries = device_entry.get("children", [])
                    sub_entries.append({
                        "value": row["sub_device"],
                        "label": row["sub_system_name"],
                    })
                    device_entry["children"] = sub_entries

                device_entries.append(device_entry)

        if device_entries:
            entry["children"] = device_entries

        result.append(entry)

    # 合并相同 vendor 的数据
    grouped_by_vendor = groupby(result, key=lambda x: x["value"])
    final_result = []

    for vendor, vendor_entries in grouped_by_vendor:
        vendor_entries = list(vendor_entries)

        if len(vendor_entries) == 1:
            final_result.append(vendor_entries[0])
        else:
            combined_entry = {
                "value": vendor,
                "label": vendor_entries[0]["label"],
                "children": []
            }

            for entry in vendor_entries:
                combined_entry["children"].extend(entry.get("children", []))

            final_result.append(combined_entry)

    return final_result

# 将数据库查询结果转为标准解析逻辑的 JSON 格式
@app.get("/api/pci_hardware/get", response_model=list)
async def get_pci_hardware():
    db = SessionLocal()
    try:
        query = db.query(pci_hardware).all()
        hardware_data = parse_pci_hardware_data([
            {
                "vendor": row.vendor,
                "vendor_name": row.vendor_name,
                "device_id": row.device_id,
                "device_name": row.device_name,
                "sub_vendor": row.sub_vendor,
                "sub_device": row.sub_device,
                "sub_system_name": row.sub_system_name,
                "entry_id": row.entry_id
            }
            for row in query
        ])
        return hardware_data
    finally:
        db.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
