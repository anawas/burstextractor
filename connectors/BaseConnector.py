from abc import abstractmethod, ABC

class BaseConnector(ABC):
    """
     The base class for every connector. A connector is used to put and get files
     to different file systems, i.e. local hard drive or remote drives. Depending on
     where you want to save the file(s) you provide a connector that implements the
     required functionality.
    """
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