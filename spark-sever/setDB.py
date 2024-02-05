# setDB.py

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
from sqlalchemy_utils import database_exists, create_database
import configparser
import urllib.request

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

# 创建新的 engine 连接到新创建的数据库 sparkdriver
sparkdriver_db_name = 'sparkdriver'
sparkdriver_db_uri = f"mysql+pymysql://{db_user}:{db_pass}@{db_host}:{db_port}/{sparkdriver_db_name}"
sparkdriver_engine = create_engine(sparkdriver_db_uri)

# 如果连接的 sparkdriver 数据库不存在，则创建
if not database_exists(sparkdriver_engine.url):
    create_database(sparkdriver_engine.url)

# 创建元数据对象
metadata = MetaData()

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
    Column('hardware_device', String(255)),
    Column('hardware_type', String(255)),
    Column('system_version', String(255))
)

# 定义硬件驱动关联表
hardware_driver = Table(
    'hardware_driver',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('hardware_id', Integer),
    Column('driver_id', Integer)
)



# 创建表格
metadata.create_all(sparkdriver_engine)
