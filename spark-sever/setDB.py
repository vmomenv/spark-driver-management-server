import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG  # 导入数据库配置

def initialize_database():
    try:
        # 连接到 MySQL 数据库
        db = mysql.connector.connect(**DB_CONFIG)
        cursor = db.cursor()

        # 检查数据库是否存在
        cursor.execute("SHOW DATABASES")
        databases = [db[0] for db in cursor.fetchall()]

        # 如果 'sparkdriver' 数据库不存在，则创建
        if 'sparkdriver' not in databases:
            create_db_query = "CREATE DATABASE sparkdriver CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            cursor.execute(create_db_query)
            print("Database 'sparkdriver' created successfully")
        else:
            print("Database 'sparkdriver' already exists")

        # 关闭连接
        cursor.close()
        db.close()
    except Error as e:
        print(f"Error initializing database: {e}")
        if 'db' in locals() and db.is_connected():
            cursor.close()
            db.close()

def create_users_table():
    try:
        # 连接到 MySQL 数据库
        db = mysql.connector.connect(**DB_CONFIG)
        cursor = db.cursor()

        # 切换到 'sparkdriver' 数据库
        cursor.execute("USE sparkdriver")

        # 创建用户表
        create_table_query = """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) NOT NULL,
            password VARCHAR(255) NOT NULL
        )
        """
        cursor.execute(create_table_query)
        print("Users table created successfully")

        # 关闭连接
        cursor.close()
        db.close()
    except Error as e:
        print(f"Error creating users table: {e}")
        if 'db' in locals() and db.is_connected():
            cursor.close()
            db.close()

# 创建接口表
def create_interfaces_table():
    try:
        db = mysql.connector.connect(**DB_CONFIG)
        cursor = db.cursor()

        cursor.execute("USE sparkdriver")

        create_table_query = """
        CREATE TABLE IF NOT EXISTS interfaces (
            id INT AUTO_INCREMENT PRIMARY KEY,
            path VARCHAR(255) NOT NULL
        )
        """
        cursor.execute(create_table_query)
        print("Interfaces table created successfully")

        cursor.close()
        db.close()
    except Error as e:
        print(f"Error creating interfaces table: {e}")
        if 'db' in locals() and db.is_connected():
            cursor.close()
            db.close()

# 创建角色表
def create_roles_table():
    try:
        db = mysql.connector.connect(**DB_CONFIG)
        cursor = db.cursor()

        cursor.execute("USE sparkdriver")

        create_table_query = """
        CREATE TABLE IF NOT EXISTS roles (
            id INT AUTO_INCREMENT PRIMARY KEY,
            role_name VARCHAR(50) NOT NULL
        )
        """
        cursor.execute(create_table_query)
        print("Roles table created successfully")

        cursor.close()
        db.close()
    except Error as e:
        print(f"Error creating roles table: {e}")
        if 'db' in locals() and db.is_connected():
            cursor.close()
            db.close()

# 创建角色接口表
def create_role_interfaces_table():
    try:
        db = mysql.connector.connect(**DB_CONFIG)
        cursor = db.cursor()

        cursor.execute("USE sparkdriver")

        create_table_query = """
        CREATE TABLE IF NOT EXISTS role_interfaces (
            id INT AUTO_INCREMENT PRIMARY KEY,
            role_id INT,
            interface_id INT,
            FOREIGN KEY (role_id) REFERENCES roles(id),
            FOREIGN KEY (interface_id) REFERENCES interfaces(id)
        )
        """
        cursor.execute(create_table_query)
        print("Role Interfaces table created successfully")

        cursor.close()
        db.close()
    except Error as e:
        print(f"Error creating role_interfaces table: {e}")
        if 'db' in locals() and db.is_connected():
            cursor.close()
            db.close()

# 创建用户角色表
def create_user_roles_table():
    try:
        db = mysql.connector.connect(**DB_CONFIG)
        cursor = db.cursor()

        cursor.execute("USE sparkdriver")

        create_table_query = """
        CREATE TABLE IF NOT EXISTS user_roles (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            role_id INT,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (role_id) REFERENCES roles(id)
        )
        """
        cursor.execute(create_table_query)
        print("User Roles table created successfully")

        cursor.close()
        db.close()
    except Error as e:
        print(f"Error creating user_roles table: {e}")
        if 'db' in locals() and db.is_connected():
            cursor.close()
            db.close()

# 创建页面表
def create_pages_table():
    try:
        db = mysql.connector.connect(**DB_CONFIG)
        cursor = db.cursor()

        cursor.execute("USE sparkdriver")

        create_table_query = """
        CREATE TABLE IF NOT EXISTS pages (
            id INT AUTO_INCREMENT PRIMARY KEY,
            page_name VARCHAR(100) NOT NULL
        )
        """
        cursor.execute(create_table_query)
        print("Pages table created successfully")

        cursor.close()
        db.close()
    except Error as e:
        print(f"Error creating pages table: {e}")
        if 'db' in locals() and db.is_connected():
            cursor.close()
            db.close()

# 创建页面接口表
def create_page_interfaces_table():
    try:
        db = mysql.connector.connect(**DB_CONFIG)
        cursor = db.cursor()

        cursor.execute("USE sparkdriver")

        create_table_query = """
        CREATE TABLE IF NOT EXISTS page_interfaces (
            id INT AUTO_INCREMENT PRIMARY KEY,
            page_id INT,
            interface_id INT,
            FOREIGN KEY (page_id) REFERENCES pages(id),
            FOREIGN KEY (interface_id) REFERENCES interfaces(id)
        )
        """
        cursor.execute(create_table_query)
        print("Page Interfaces table created successfully")

        cursor.close()
        db.close()
    except Error as e:
        print(f"Error creating page_interfaces table: {e}")
        if 'db' in locals() and db.is_connected():
            cursor.close()
            db.close()


#
def create_roles_table():
    try:
        db = mysql.connector.connect(**DB_CONFIG)
        cursor = db.cursor()

        cursor.execute("USE sparkdriver")

        create_table_query = """
        CREATE TABLE IF NOT EXISTS roles (
            id INT AUTO_INCREMENT PRIMARY KEY,
            role_name VARCHAR(50) NOT NULL
        )
        """
        cursor.execute(create_table_query)
        print("Roles table created successfully")

        # 添加初始化数据
        initial_roles = [
            ("admin",),
            ("auditor",),
            ("delivery",)
        ]
        add_roles_query = "INSERT INTO roles (role_name) VALUES (%s)"

        cursor.executemany(add_roles_query, initial_roles)
        db.commit()
        print("Initial roles added successfully")

        cursor.close()
        db.close()
    except Error as e:
        print(f"Error creating roles table: {e}")
        if 'db' in locals() and db.is_connected():
            cursor.close()
            db.close()
if __name__ == "__main__":
    initialize_database()          # 初始化数据库
    create_users_table()           # 创建用户表
    create_interfaces_table()      # 创建接口表
    create_roles_table()           # 创建角色表
    create_role_interfaces_table() # 创建角色接口表
    create_user_roles_table()      # 创建用户角色表
    create_pages_table()           # 创建页面表
    create_page_interfaces_table() # 创建页面接口表
