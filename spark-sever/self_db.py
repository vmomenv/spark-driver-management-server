from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime,select
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import configparser
from sqlalchemy.pool import SingletonThreadPool
import os
import shutil
from unit import *
import importlib

import random
import string
 
def generate_random_string(length):
    letters = string.ascii_letters + string.digits # 包含大小写字母和数字
    return ''.join([random.choice(letters) for _ in range(length)])
# 读取配置文件
config = configparser.ConfigParser()

if not os.path.exists(CONFIG_FILE):
    # 复制文件
    shutil.copy(CONFIG_EXAMPLE_FILE, CONFIG_FILE)
    
config.read(CONFIG_FILE)
# 根据配置文件的数据库类型去导入对应的模块
dbFactoryModule=importlib.import_module(f".{config['database']['type']}",package='db_factory')
#  利用反射获取类名
cls = getattr(dbFactoryModule,dbFactoryModule.class_name)
# 实例化
dbFactory=cls(config)

# 构建数据库连接 URI
default_db_uri =dbFactory.get_db_url()
connectArgs={}
if config['database']['type']=='sqlite':
    connectArgs['check_same_thread']=True
# 创建默认数据库连接引擎
default_engine = create_engine(default_db_uri,
                               poolclass=SingletonThreadPool,# 线程池
                               echo_pool=False,# 线程池输出
                               connect_args=connectArgs,# 多线程
                                echo=True)# 是否输出sql

# 如果连接的默认数据库不存在，则创建
if not database_exists(default_engine.url):
    create_database(default_engine.url)
secretConfig = configparser.ConfigParser()
# 读取secretkey
if not os.path.exists(CONFIG_SECRET_KEY_FILE):
    shutil.copy(CONFIG_SECRET_KEY_EXAMPLE_FILE,CONFIG_SECRET_KEY_FILE)
    
    secretConfig.read(CONFIG_SECRET_KEY_FILE)
    secretKey=generate_random_string(72)
    print(secretKey)
    secretConfig.set('secretkey','secret_key',secretKey)
    secretConfig.write(open(CONFIG_SECRET_KEY_FILE,'wt'))
secretConfig.read(CONFIG_SECRET_KEY_FILE)
# 获取数据
SECRET_KEY = secretConfig['secretkey']['secret_key']
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
Base = declarative_base()
metadata = Base.metadata



# 定义用户表格
users = Table(
    'users',
    metadata,
    Column('user_id', Integer, primary_key=True, autoincrement=True),
    Column('username', String(50), unique=True),
    Column('password', String(255)),
    Column('email', String(100), unique=True),
    Column('created_at', String(50)),
    Column('role_id', Integer),
    Column('last_login', String(50))
)


# 定义硬件表
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
usb_hardware = Table(
    'usb_hardware',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('vendor', String(50)),
    Column('vendor_name', String(255)),
    Column('device_id', String(50)),
    Column('device_name', String(255)),
    Column('entry_id', String(50)),

)
#定义厂商表
pci_vendor = Table(
    'pci_vendor',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('vendor', String(50)),
    Column('vendor_name', String(255)),
    Column('combined_column', String(255)),  # 合并的列
)
usb_vendor =Table(
    'usb_vendor',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('vendor', String(50)),
    Column('vendor_name', String(255)),
    Column('combined_column', String(255)),  # 合并的列
)
# 定义驱动表
driver = Table(
    'driver',
    metadata,
    Column('driver_id', Integer, primary_key=True, autoincrement=True),
    Column('file_name', String(255)),
    Column('package_name', String(255)),
    Column('version', String(50)),
    Column('file_size', Integer),
    Column('description', String(500)),
)
# 定义硬件驱动关联表
hardware_driver = Table(
    'hardware_driver',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('hardware_id', Integer),
    Column('driver_id', Integer),
    Column('hardware_type_id', String(50)),
    Column('pci_usb_key', String(50))
)

system_table = Table(
    'system_table',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('system_name', String(50))
)

system_version_driver = Table(
    'system_version_driver',
    metadata,
    Column('system_version_id', Integer, primary_key=True),
    Column('driver_id', Integer)
)
system_version_table = Table(
    'system_version_table',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('system_table_id', Integer),
    Column('system_version_id', String(50))
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=default_engine)
Base.metadata.create_all(default_engine, checkfirst=True)