from .base import Base

class_name = 'SqliteDb'

class SqliteDb(Base):
    def __init__(self, file_path) -> None:
        super().__init__(file_path)

    def get_db_url(self):
        # SQLite connection URI for a file-based database
        return f"sqlite:///{self.file_path}"
