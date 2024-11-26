import configparser
import secrets

# 生成一个包含随机字节的字符串，每个字节由两个十六进制字符表示
SECRET_KEY = secrets.token_hex(32)  # 32字节的十六进制字符，每字节2个字符

# 将生成的密钥写入到配置文件
config = configparser.ConfigParser()
config['secretkey'] = {'SECRET_KEY': SECRET_KEY}

# 写入到文件
with open('secretkey.ini', 'w') as configfile:
    config.write(configfile)

print("密钥已成功写入 secretkey.ini 文件")
