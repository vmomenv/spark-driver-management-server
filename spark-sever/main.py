import shutil
from itertools import groupby

from fastapi import FastAPI, Form, HTTPException,Header
from pydantic import BaseModel
from sqlalchemy import  select

from datetime import datetime
from self_db import *


from fastapi import File, UploadFile,Request
# from fastapi.responses import JSONResponse
# from pathlib import Path
from typing import Set
from fastapi import  HTTPException
# from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
import os
import json
# 创建 FastAPI 应用
app = FastAPI()





# 创建密码哈希上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 创建用于验证token的OAuth2PasswordBearer对象
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")



# 登录接口
# 用户密码加密校验采用bcrypt算法
@app.post("/api/token")

async def login_for_access_token(request:Request):
    form_data=await request.body()
    print('-----------',form_data)
    form_data=json.loads(form_data)
    user = authenticate_user(form_data['username'], form_data['password'])
    if not user:
        return {'code': 200001, "message": "登录失败"}

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": form_data['username']}, expires_delta=access_token_expires
    )
    return {'code':20000,"access_token": access_token, "token_type": "bearer"}

# 验证token的函数
def get_current_user(token ):
    # credentials_exception = HTTPException(
    #     status_code=status.HTTP_401_UNAUTHORIZED,
    #     detail="Could not validate credentials",
    #     headers={"WWW-Authenticate": "Bearer"},
    # )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
    except JWTError:
        return None

    return username

# 生成token的函数
def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# 根据用户名和密码验证用户
def authenticate_user(username: str, password: str):
    # 在数据库中查询用户信息
    db_user = get_user_by_username(username)

    # 校验密码是否匹配
    if db_user and verify_password(password, db_user['password']):
        print("pipei")
        return db_user
    print("bpipei")
    return None

# 在数据库中根据用户名获取用户信息
def get_user_by_username(username: str):
    db = SessionLocal()
    try:
        query = db.query(users).filter(users.c.username == username).first()
        if query:
            return {
                "username": query.username,
                "password": query.password,
                "role_id": query.role_id
            }
    finally:
        print('关闭连接')

# 校验密码是否匹配
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)



# 模型：用于输入数据验证
class UserCreate(BaseModel):
    username: str
    password: str
    roleid: int
    email: str


# API 路由：用于创建用户
@app.post("/api/user/add")
async def create_user(user: UserCreate):
    db = SessionLocal()
    try:
        db.execute(users.insert().values(
            username=user.username,
            password=user.password,
            role_id=user.roleid,
            email=user.email
        ))
        db.commit()
        return {"message": "User created successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create user: {str(e)}")
    finally:
        print('关闭连接')


# API 路由：用于编辑用户
@app.put("/api/user/edit/{user_id}")
async def edit_user(user_id: int, user: UserCreate,token=Header()):
    if token is None:
        # tongxia
        return {"message": "token is None1"}
    username=get_current_user(token)
    if username is None:
        # fanhui baocuo, chongdingxiang dengluye
        return {"message": "token is None2"}
    db = SessionLocal()
    try:
        db.execute(users.update().where(users.c.user_id == user_id).values(
            username=user.username,
            password=user.password,
            role_id=user.roleid,
            email=user.email
        ))
        db.commit()
        return {"message": "User updated successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update user: {str(e)}")
    finally:
        print('关闭连接')


# API 路由：用于删除用户
@app.delete("/api/user/del/{user_id}")
async def delete_user(user_id: int,token=Header()):
    if token is None:
        # tongxia
        return {"message": "token is None1"}
    username=get_current_user(token)
    if username is None:
        # fanhui baocuo, chongdingxiang dengluye
        return {"message": "token is None2"}
    db = SessionLocal()
    try:
        db.execute(users.delete().where(users.c.user_id == user_id))
        db.commit()
        return {"message": "User deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete user: {str(e)}")
    finally:
        print('关闭连接')


# API 路由：用于获取所有用户信息
from typing import List, Dict


@app.get("/api/user/getUser", response_model=List[dict])
async def get_users(token=Header()):
    if token is None:
        # tongxia
        return {"message": "token is None1"}
    username=get_current_user(token)
    if username is None:
        # fanhui baocuo, chongdingxiang dengluye
        return {"message": "token is None2"}
    db = SessionLocal()
    try:
        query = db.query(users).all()
        user_data = [{column: getattr(user, column) for column in users.columns.keys()} for user in query]
        return user_data
    finally:
        print('关闭连接')
@app.post("/api/permission/getMenu")
def get_menu(token=Header())-> Dict:
    print('**********',token)
    if token is None:
        # tongxia
        return {"message": "token is None1"}
    username=get_current_user(token)
    if username is None:
        # fanhui baocuo, chongdingxiang dengluye
        return {"message": "token is None2"}
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
            "label": "硬件列表",
            "icon": "location",
            "children": [
                {
                    "path": "/pcilist",
                    "name": "pcilist",
                    "label": "PCI列表",
                    "icon": "setting",
                    "url": "PciList.vue"
                },
                {
                    "path": "/usblist",
                    "name": "usblist",
                    "label": "USB列表",
                    "icon": "setting",
                    "url": "UsbList.vue"
                }
            ]
        }
    ]

    response_data = {
        "code": 20000,
        "data": {
            "menu": menu,
            "message": "获取成功"
        }
    }

    return response_data


@app.post("/api/upload_driver")
async def upload_driver(
    driver_file: UploadFile = File(...),
    file_name: str = Form(...),
    package_name: str = Form(...),
    version: str = Form(...),
    file_size: int = Form(...),
    description: str = Form(...),
hardware_type_id: str = Form(...),
    hardware_id: int = Form(...),
    # usb_device: str = Form(...),
    pci_usb_key:str = Form(...),
):
    try:
        # 将上传的文件保存到指定的文件夹
        upload_folder = f"../spark-driver-repo/{package_name}"
        os.makedirs(upload_folder, exist_ok=True)  # 如果不存在则创建目录
        file_path = f"{upload_folder}/{driver_file.filename}"

        with open(file_path, "wb") as f:
            f.write(driver_file.file.read())

        # 将数据插入数据库
        db = SessionLocal()
        hardwareId=hardware_id
        # if pci_usb_key=='pci':
        #     pass
        # else:
        #     pass
        try:
            # 拿到自增id
            ret=db.execute(driver.insert().values(
                file_name=file_name,
                package_name=package_name,
                version=version,
                file_size=file_size,
                description=description,
                # pci_device=pci_device,
                # usb_device=usb_device,
                # system_version=system_version,
            ))
            insertId=ret.inserted_primary_key[0]
            db.execute(hardware_driver.insert().values(
                hardware_id=hardwareId,# 这个是硬件id，是usb、pci——hardware里的id
                driver_id=insertId,
                hardware_type_id=hardware_type_id,# 这个是前端选择的硬件类型
                pci_usb_key=pci_usb_key,#这个是前端选择的usb和pci
                # system_version=system_version,
            ))

            db.commit()
        except Exception as e:
            db.rollback()
            return {"message": f"将数据保存到数据库时出错: {str(e)}"}
        finally:
            print('关闭连接')

        # 返回响应
        return {"message": "文件和数据上传成功", "file_path": file_path}
    except Exception as e:
        # 处理文件上传或处理过程中可能发生的任何错误
        return {"message": f"上传文件或保存数据时出错: {str(e)}"}


@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    return {"filename": file.filename}



# 将数据库查询结果转为 JSON 格式

# 标准解析逻辑
def parse_pci_hardware_data(data_list: List[dict]) -> List[dict]:
    vendors = []
    sub_device_set: Set[str] = set()

    for data in data_list:
        vendor_value = data["vendor"]
        vendor_label = data["vendor_name"]

        # 检查 vendor 是否已存在
        vendor_exists = any(vendor["value"] == vendor_value for vendor in vendors)

        if not vendor_exists:
            vendor_object = {"value": vendor_value, "label": f"{vendor_value} - {vendor_label}"}

            if data["device_id"]:
                device_object = {"value": data["device_id"], "label": f"{data['entry_id']} - {data['device_name']}"}

                if data["sub_device"]:
                    sub_device_key = f"{data['sub_device']}_{data['sub_system_name']}"

                    if sub_device_key not in sub_device_set:
                        sub_device_set.add(sub_device_key)

                        sub_device_object = {"value": data["sub_device"],
                                             "label": f"{data['sub_device']} - {data['sub_system_name']}"}
                        device_object["children"] = [sub_device_object]

                vendor_object["children"] = [device_object]

            vendors.append(vendor_object)
        else:
            # 如果 vendor 已存在，查找并添加 device 数据
            existing_vendor = next(vendor for vendor in vendors if vendor["value"] == vendor_value)

            if data["device_id"]:
                device_exists = any(
                    device["value"] == data["device_id"] for device in existing_vendor.get("children", []))

                if not device_exists:
                    device_object = {"value": data["device_id"],
                                     "label": f"{data['entry_id']} - {data['device_name']}"}

                    if data["sub_device"]:
                        sub_device_key = f"{data['sub_device']}_{data['sub_system_name']}"

                        if sub_device_key not in sub_device_set:
                            sub_device_set.add(sub_device_key)

                            sub_device_object = {"value": data["sub_device"],
                                                 "label": f"{data['entry_id']} - {data['sub_system_name']}"}
                            device_object["children"] = [sub_device_object]

                    if "children" not in existing_vendor:
                        existing_vendor["children"] = []

                    existing_vendor["children"].append(device_object)

            # 添加 sub_device 数据
            if data["sub_device"]:
                sub_device_key = f"{data['sub_device']}_{data['sub_system_name']}"

                device_exists = any(
                    device["value"] == data["device_id"] for device in existing_vendor.get("children", []))

                if device_exists:
                    existing_device = next(
                        device for device in existing_vendor["children"] if device["value"] == data["device_id"])

                    if "children" not in existing_device:
                        existing_device["children"] = []

                    if sub_device_key not in sub_device_set:
                        sub_device_set.add(sub_device_key)

                        sub_device_object = {"value": data["sub_device"],
                                             "label": f"{data['entry_id']} - {data['sub_system_name']}"}
                        existing_device["children"].append(sub_device_object)

    return vendors


def parse_usb_hardware_data(data_list: List[dict]) -> List[dict]:
    vendors = []

    for data in data_list:
        vendor_value = data["vendor"]
        vendor_label = data["vendor_name"]

        # 检查 vendor 是否已存在
        vendor_exists = any(vendor["value"] == vendor_value for vendor in vendors)

        if not vendor_exists:
            vendor_object = {"value": vendor_value, "label": f"{vendor_value} - {vendor_label}"}

            if data["device_id"]:
                device_object = {"value": data["device_id"], "label": f"{data['entry_id']} - {data['device_name']}"}
                vendor_object["children"] = [device_object]

            vendors.append(vendor_object)
        else:
            # 如果 vendor 已存在，查找并添加 device 数据
            existing_vendor = next(vendor for vendor in vendors if vendor["value"] == vendor_value)

            if data["device_id"]:
                device_exists = any(
                    device["value"] == data["device_id"] for device in existing_vendor.get("children", []))

                if not device_exists:
                    device_object = {"value": data["device_id"],
                                     "label": f"{data['entry_id']} - {data['device_name']}"}

                    if "children" not in existing_vendor:
                        existing_vendor["children"] = []

                    existing_vendor["children"].append(device_object)

    return vendors

def save_to_local(data, filename):
    with open(filename, "w") as file:
        json.dump(data, file, indent=2)

# 将数据库查询结果转为标准解析逻辑的 JSON 格式
@app.get("/api/pci_hardware/get", response_model=list)
async def get_pci_hardware():
    # 如果文件存在，直接返回文件内容
    if os.path.exists("pci.json"):
        with open("pci.json", "r") as file:
            file_content = json.load(file)
            print("直接推送数据")
        return file_content

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
        save_to_local(hardware_data, "pci.json")
        return hardware_data
    finally:
        print('关闭连接')


@app.get("/api/usb_hardware/get", response_model=list)
async def get_pci_hardware():
    if os.path.exists("pci.json"):
        with open("usb.json", "r") as file:
            file_content = json.load(file)
            print("直接推送数据")
        return file_content
    db = SessionLocal()
    try:
        query = db.query(usb_hardware).all()
        hardware_data = parse_usb_hardware_data([
            {
                "vendor": row.vendor,
                "vendor_name": row.vendor_name,
                "device_id": row.device_id,
                "device_name": row.device_name,
                "entry_id": row.entry_id
            }
            for row in query
        ])
        save_to_local(hardware_data, "usb.json")
        return hardware_data
    finally:
        print('关闭连接')
# 将数据库查询结果转为标准解析逻辑的 JSON 格式


@app.get("/api/searchPciVendor")
async def search_pci_vendor(query: str):
    db = SessionLocal()

    try:
        stmt = select([pci_vendor.c.id, pci_vendor.c.vendor_name]).where(
            pci_vendor.c.vendor_name.ilike(f"%{query}%")
        )
        results = db.execute(stmt).all()

        options = [
            {"value": result.id, "label": result.vendor_name}
            for result in results
        ]

        return options

    finally:
        print('关闭连接')


@app.get("/api/searchUsbVendor")
async def search_usb_vendor(query: str):
    db = SessionLocal()

    try:
        stmt = select([usb_vendor.c.id, usb_vendor.c.vendor_name]).where(
            usb_vendor.c.vendor_name.ilike(f"%{query}%")
        )
        results = db.execute(stmt).all()

        options = [
            {"value": result.id, "label": result.vendor_name}
            for result in results
        ]

        return options
    finally:
        print('关闭连接')

@app.get("/api/getPciHardwareByVendor")
async def get_pcihardware_by_vendor(vendor: str):
    # 执行查询
    db = SessionLocal()
    query = pci_hardware.select().where(pci_hardware.c.vendor == vendor)
    result = db.execute(query).fetchall()
    print('关闭连接')

    # 处理结果
    if not result:
        raise HTTPException(status_code=404, detail="Vendor not found")

    # 将结果转换为字典形式
    return [{'id': row.id, 'vendor': row.vendor, 'vendor_name': row.vendor_name, 'device_id': row.device_id,
             'device_name': row.device_name, 'sub_vendor': row.sub_vendor, 'sub_device': row.sub_device,
             'sub_system_name': row.sub_system_name, 'entry_id': row.entry_id} for row in result]

@app.get("/api/getUsbHardwareByVendor")
async def get_usbhardware_by_vendor(vendor: str):
    # 执行查询
    db = SessionLocal()
    query =usb_hardware.select().where(usb_hardware.c.vendor == vendor)
    result = db.execute(query).fetchall()
    print('关闭连接')

    # 处理结果
    if not result:
        raise HTTPException(status_code=404, detail="Vendor not found")

    # 将结果转换为字典形式
    return [{'id': row.id, 'vendor': row.vendor, 'vendor_name': row.vendor_name, 'device_id': row.device_id,
             'device_name': row.device_name, 'entry_id': row.entry_id} for row in result]

@app.get("/api/FileDisplayByType")
#根据硬件类型选文件如打印机驱动，网卡驱动等(看驱动属性）
async def get_driver_list_by_type(driver_type,request:Request):
    # driver_type，驱动属性，printer/network/VGA/camera
    # hardId 硬件id
    # driver_name 驱动名称
    # vendor 厂商名
    # form_data=await request.body()
    print('-------------',driver_type)
    # form_data=json.loads(form_data)
    db = SessionLocal()
    # select * from hardware_driver left join driver on driver.driver.id=hardware_driver.driver_id where type in ('','common')
    query=select(driver.c.driver_id,driver.c.file_name,driver.c.package_name,driver.c.version,driver.c.file_size,driver.c.description) \
        .select_from(hardware_driver) \
        .join(driver,driver.c.driver_id==hardware_driver.c.driver_id) \
        .where(hardware_driver.c.hardware_type_id==driver_type) \
        .group_by(driver.c.driver_id)
    result = db.execute(query).fetchall()
    print(result)
    driverList=[]
    for i in result:
        package_name=i.package_name
        upload_folder = f"/download/{package_name}"
        driverList.append({'driver_id': i.driver_id,'file_name':i.file_name,
             'package_name':i.package_name,
             'version':i.version,'file_size':i.file_size,
             'description':i.description,
             'file_path':os.path.join(upload_folder,i.file_name)
        })
    # XXX 返回数据结构
    return driverList


@app.get("/api/FindFilesByHardwareId")
# # 根据硬件ID选驱动文件（给出entry_id)
async def get_driver_list_by_hardware_id(driver_type,device_id):
    db=SessionLocal()
    if driver_type not in ['usb','pci']:
        return '类型错误'
    query=select(driver.c.driver_id,driver.c.file_name,driver.c.package_name,driver.c.version,driver.c.file_size,driver.c.description) \
        .select_from(hardware_driver) \
           .join(driver,driver.c.driver_id==hardware_driver.c.driver_id).where(hardware_driver.c.pci_usb_key==driver_type) \
    .group_by(driver.c.driver_id)
    if driver_type=='usb':
        query=query.join(usb_hardware,hardware_driver.c.hardware_id==usb_hardware.c.id) \
            .where(usb_hardware.c.entry_id==device_id)
    else:
        query=query.join(pci_hardware,hardware_driver.c.hardware_id==pci_hardware.c.id) \
            .where(pci_hardware.c.entry_id==device_id)
    result=db.execute(query).fetchall()
    print(result)

    driverList = []
    for i in result:
        package_name = i.package_name
        upload_folder = f"/download/{package_name}"
        driverList.append({'driver_id': i.driver_id, 'file_name': i.file_name,
                           'package_name': i.package_name,
                           'version': i.version, 'file_size': i.file_size,
                           'description': i.description,
                           'file_path': os.path.join(upload_folder, i.file_name)
                           })
    # XXX 返回数据结构
    return driverList


@app.get("/api/FindFilesByDeviceName")
# 根据设备商品名找驱动

async def get_driver_list_by_driver_name(device_name):
    db=SessionLocal()
    # 查usb，查pci，然后根据对应的类型去中间表去查，最后合并数据
    usbQuery=select(driver.c.driver_id,driver.c.file_name,driver.c.package_name,driver.c.version,driver.c.file_size,driver.c.description) \
    .select_from(usb_hardware) \
        .join(hardware_driver,hardware_driver.c.hardware_id==usb_hardware.c.id) \
        .join(driver, driver.c.driver_id == hardware_driver.c.driver_id) \
        .where(usb_hardware.c.device_name.like(f'%{device_name}%')) \
        .where(hardware_driver.c.pci_usb_key=='usb')


    usbResult=db.execute(usbQuery).fetchall()
    pciQuery=select(driver.c.driver_id,driver.c.file_name,driver.c.package_name,driver.c.version,driver.c.file_size,driver.c.description) \
    .select_from(pci_hardware) \
        .where(pci_hardware.c.device_name.like(f'%{device_name}%')) \
        .join(hardware_driver,hardware_driver.c.hardware_id==pci_hardware.c.id) \
        .where(hardware_driver.c.pci_usb_key=='pci') \
        .join(driver,driver.c.driver_id==hardware_driver.c.driver_id)
    pciResult=db.execute(pciQuery).fetchall()
    # 合并两个结果，根据driver_id去重
    # print(pciResult)
    driverDict={}
    for i in usbResult:
        if driverDict.get(i.driver_id) is None:
            driverDict[i.driver_id]=i
    for i in pciResult:
        if driverDict.get(i.driver_id) is None:
            driverDict[i.driver_id]=i
    driverList=[]
    for i in driverDict:
        package_name = driverDict[i].package_name
        upload_folder = f"/download/{package_name}"
        driverList.append({'driver_id': driverDict[i].driver_id, 'file_name': driverDict[i].file_name,
                           'package_name': driverDict[i].package_name,
                           'version': driverDict[i].version, 'file_size': driverDict[i].file_size,
                           'description': driverDict[i].description,
                           'file_path': os.path.join(upload_folder, driverDict[i].file_name)
                           })
    print(driverList)
    return driverList



@app.get("/api/FindHardwareByVendor")
# 根据厂商名与PCI/USB信息 选硬件名（前端）
async def get_driver_list(driver_type,vendor_name):
    db=SessionLocal()
    masterTable=None
    if driver_type not in ['usb','pci']:
        return '类型错误'
    if driver_type=='usb':
        masterTable=(select(usb_hardware.c.id,usb_hardware.c.device_name)
             .select_from(usb_vendor)
                .join(usb_hardware,usb_hardware.c.vendor==usb_vendor.c.vendor)
                .where(usb_vendor.c.vendor_name.like(f'%{vendor_name}%'))
                )
    else:
        masterTable=(select(pci_hardware.c.id,pci_hardware.c.device_name)
             .select_from(pci_vendor)
                .join(pci_hardware,pci_hardware.c.vendor==pci_vendor.c.vendor)
                .where(pci_vendor.c.vendor_name.like(f'%{vendor_name}%'))
                )


    result=db.execute(masterTable).fetchall()
    hardwareList=[]
    for i in result:
        hardwareList.append({'hardware_id':i.id,'device_name':i.device_name})
    print(result)
    return hardwareList
if __name__ == "__main__":
    import uvicorn
    uvicorn.run('main:app', host="127.0.0.1", port=8000,reload=True)
