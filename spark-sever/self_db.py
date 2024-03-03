from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime,select
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm import sessionmaker
import configparser
from sqlalchemy.pool import SingletonThreadPool
import os
import shutil
from unit import *
import importlib

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

# 创建默认数据库连接引擎
default_engine = create_engine(default_db_uri,
                               poolclass=SingletonThreadPool,# 线程池
                               echo_pool=False,# 线程池输出
                                echo=False)# 是否输出sql

# 如果连接的默认数据库不存在，则创建
if not database_exists(default_engine.url):
    create_database(default_engine.url)
# 读取secretkey

config.read('secretkey.ini')
# 获取数据
SECRET_KEY = config['secretkey']['secret_key']
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
metadata = MetaData()
# 创建数据库会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=default_engine)

# 创建数据库表
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


# 文件上传
driver = Table(
    'driver',
    metadata,
    Column('driver_id', Integer, primary_key=True, autoincrement=True),
    Column('file_name', String(255)),
    Column('package_name', String(255)),
    Column('version', String(50)),
    Column('file_size', Integer),
    Column('description', String(500)),
    Column('pci_device', String(255)),
    Column('usb_device', String(255)),
    Column('system_version', String(255))
)

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
pci_vendor = Table(
    'pci_vendor',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('vendor', String(50)),
    Column('vendor_name', String(255)),
    Column('combined_column', String(255)),
)
usb_vendor =Table(
    'usb_vendor',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('vendor', String(50)),
    Column('vendor_name', String(255)),
    Column('combined_column', String(255)),  # 合并的列
)