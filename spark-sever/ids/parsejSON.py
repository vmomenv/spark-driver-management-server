import json
import sqlite3

# 读取JSON文件
file_path = 'pci_parsed.json'
with open(file_path, 'r') as file:
    data = json.load(file)

# 连接到SQLite数据库
conn = sqlite3.connect('your_database.db')
cursor = conn.cursor()

# 创建表格（如果不存在）
cursor.execute('''
    CREATE TABLE IF NOT EXISTS pci_data (
        vendor TEXT,
        vendor_name TEXT,
        device_id TEXT,
        device_name TEXT,
        sub_vendor TEXT,
        sub_device TEXT,
        sub_system_name TEXT,
        entry_id TEXT
    )
''')

# 插入数据
for entry in data:
    vendor = entry['vendor']
    vendor_name = entry['vendor_name']

    if entry['device_list']:
        for device in entry['device_list']:
            device_id = device['device_id']
            device_name = device['device_name']
            entry_id = f"{vendor}:{device_id}"

            cursor.execute('''
                INSERT INTO pci_data
                VALUES (?, ?, ?, ?, NULL, NULL, NULL, ?)
            ''', (vendor, vendor_name, device_id, device_name, entry_id));

            if device['sub_vendor']:
                for sub_vendor in device['sub_vendor']:
                    sub_vendor_id = f"{vendor}:{device_id}:{sub_vendor['sub_vendor']} {sub_vendor['sub_device']}"
                    cursor.execute('''
                        INSERT INTO pci_data
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (vendor, vendor_name, device_id, device_name, sub_vendor['sub_vendor'], sub_vendor['sub_device'], sub_vendor['sub_system_name'], sub_vendor_id))

# 提交更改并关闭连接
conn.commit()
conn.close()
