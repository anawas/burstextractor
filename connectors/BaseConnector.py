from abc import abstractmethod, ABC

class BaseConnector(ABC):
    def __init__(self) -> None:
        pass

        @abstractmethod
        def list_dir(self, dir_name:str = None) -> list:
            pass

        @abstractmethod
        def get_file(self, file_name:str, local_file_name:str=None):
            pass

        @abstractmethod
        def put_file(self, file_name:str, local_file_name:str=None, overwrite:bool=False):
            pass

        @abstractmethod
        def make_dir(self, dir_name:str):
            pass

        @abstractmethod
        def check_dir_exists(self, dir_name):
            pass