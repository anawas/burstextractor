import os
import shutil
from pathlib import Path

from connectors.baseconnector import BaseConnector


class DefaultConnector(BaseConnector):
    """
    This class implements the default connector, which connects to the local
    file system.
    version 1.0
    author: Andreas Wassmer
    project: Raumschiff
    """

    def __init__(self) -> None:
        self.base_dir = ""

    def list_dir(self, dir_name: str = None) -> list:
        dir = Path(dir_name)
        return [p for p in dir.glob("**/*")]

    def get_file(self, file_name: str, local_file_name: str = None) -> None:
        """
        Gets the file with name file_name. Raises an exception if the file
        doesn't exist.
        If local_file_name is None, nothing happens. This is because the file
        already exists on the file system. If local_file_name is given, then the
        file is copied to the new location. The original file is unchanged.
        """
        if local_file_name is not None:
            if not Path(file_name).exists:
                raise FileNotFoundError
            shutil.copy(local_file_name, file_name)

    def put_file(self, remote_name: str = None, local_name: str = None, overwrite: bool = False):
        """
        Puts the file with on the file system with name file_name . Raises an exception if
        the file cannot be written.
        If local_file_name is None, nothing happens. This is because the file
        already exists on the file system. If local_name is given, then the
        file is copied to the new location. The original file is unchanged.
        For local file systems this method works the same as get_file.
        """
        path = os.path.join(self.base_dir, remote_name)
        self.get_file(path, local_name)

    def make_dir(self, dir_name: str):
        """
        Makes the directory given by dir_name. It does nothing if the dir exists.
        """
        if self.check_dir_exists(dir_name):
            return
        os.makedirs(dir_name)

    def check_dir_exists(self, dir_name: str) -> bool:
        subdir = Path(dir_name)
        if subdir.exists():
            return True
        return False


if __name__ == "__main__":
    con = DefaultConnector()
    files = con.list_dir(".")
    for f in files:
        if f.is_dir():
            print(f)
    assert Path("connectors") in files
    assert con.check_dir_exists("temp") is True
    try:
        con.get_file("temp/ALASKA-ANCHORAGE.fit.gz", "test.fit.gz")
    except FileNotFoundError as err:
        print(f"ERROR -- {err.strerror}")
    con.make_dir("dir1/dir2/dir3")
