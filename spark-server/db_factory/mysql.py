from .base import Base
class_name='MysqlDb'
class MysqlDb(Base):
    def __init__(self, filePath) -> None:
        super().__init__(filePath)
    def get_db_url(self):
        return f"mysql+pymysql://{self.db_user}:{self.db_pass}@{self.db_host}:{self.db_port}/{self.default_db_name}"