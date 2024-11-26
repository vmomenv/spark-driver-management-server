import json
import configparser
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
from sqlalchemy_utils import database_exists, create_database

# 读取JSON文件
file_path = 'usb_parsed.json'
with open(file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

# 读取配置文件
config = configparser.ConfigParser()
config.read('../config.ini')

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

# 创建元数据对象
metadata = MetaData()

# 定义硬件表
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

#定义usb厂商表
usb_vendor = Table(
    'usb_vendor',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('vendor', String(50)),
    Column('vendor_name', String(255)),
    Column('combined_column', String(255)),  # 合并的列
)

# 保证在这之前定义了 default_engine
# 创建数据库连接
conn = default_engine.connect()

# 开始事务
trans = conn.begin()

try:
    # 缓存所有数据
    all_data = []

    # 构建数据
    for entry in data:
        vendor = entry['vendor']
        vendor_name = entry['vendor_name']
        entry_id = f"{vendor}"

        # 保存供应商数据到 vendor_table
        vendor_data_entry = {
            'vendor': vendor,
            'vendor_name': vendor_name,
            'combined_column': f"[{vendor} {vendor_name}]",
        }
        vendor_insert = usb_vendor.insert().values(vendor_data_entry)
        conn.execute(vendor_insert)

        # 保存硬件数据到 usb_hardware
        data_entry = {
            'vendor': vendor,
            'vendor_name': vendor_name,
            'device_id': None,
            'device_name': None,
            'entry_id': entry_id
        }

        all_data.append(data_entry)

        if entry['device_list']:
            for device in entry['device_list']:
                device_id = device['device_id']
                device_name = device['device_name']
                entry_id = f"{vendor}:{device_id}"

                data_entry = {
                    'vendor': vendor,
                    'vendor_name': vendor_name,
                    'device_id': device_id,
                    'device_name': device_name,
                    'entry_id': entry_id
                }

                all_data.append(data_entry)


    # 一次性批量插入硬件数据到 usb_hardware
    conn.execute(usb_hardware.insert(), all_data)

    # 提交事务
    trans.commit()

except Exception as e:
    # 回滚事务
    trans.rollback()
    raise e

finally:
    # 关闭连接
    conn.close()
