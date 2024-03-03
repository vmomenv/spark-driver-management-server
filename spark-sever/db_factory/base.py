from abc import ABC, abstractmethod

class Base(ABC):
    def __init__(self,config) -> None:
        
        self.db_host = config['database']['host']
        self.db_port = config['database']['port']
        self.db_user = config['database']['username']
        self.db_pass = config['database']['password']
        self.default_db_name = config['database']['database_name']
    @abstractmethod
    def get_db_url(self):
        pass