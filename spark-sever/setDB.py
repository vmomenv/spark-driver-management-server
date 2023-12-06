import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG  # 假设你的配置文件在这里

def initialize_database():
    try:
        # 连接到 MySQL 数据库
        db = mysql.connector.connect(**DB_CONFIG)
        cursor = db.cursor()

        # 检查数据库是否存在
        cursor.execute("SHOW DATABASES")
        databases = [db[0] for db in cursor.fetchall()]
        print(databases)
        # 如果 'sparkdriver' 数据库不存在，则创建
        if 'spark-driver' not in databases:
            create_db_query = "CREATE DATABASE sparkdriver CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            cursor.execute(create_db_query)
            print("Database 'sparkdriver' created successfully")
        else:
            print("Database 'sparkdriver' already exists")

        # 关闭连接
        cursor.close()
        db.close()
    except Error as e:
        print(f"Error connecting to MySQL: {e}")

if __name__ == "__main__":
    initialize_database()
