from webdav3.client import Client, RemoteResourceNotFound
from dotenv import load_dotenv
import os
from connectors.baseconnector import BaseConnector

"""
Offers basic functionality to interact with webdav server
Uses a .env file for configuration
version 1.0
author: Andreas Wassmer
project: Raumschiff
"""
class WebdavConnector (BaseConnector):
    def __init__(self) -> None:
        load_dotenv()
        options = {
            'webdav_hostname': os.environ.get('HOST_URL'),
            'webdav_login': os.environ.get('USERNAME'),
            'webdav_password': os.environ.get('PASSWORD'),
            'webdav_timeout': 120,
            'verbose': True
        }
        self.client = Client(options)
        self.base_dir = ""

    def list_dir(self, remote_dir_name=None):
        """
        Returns the names of the files in the remote folder
        Arguments:
        remote_dir_name: the name of the folder
        """
        assert remote_dir_name is not None
        files = self.client.list(remote_dir_name)
        return files

    def get_file(self, remote_name=None, local_name=None):
        """
        Downloads a file from webdav server to local folder
        Arguments:
        remote_name: full path of file on the server
        local_name: name of the file after download. Add path if necessary.
        """
        assert remote_name is not None
        assert local_name is not None
        path = os.path.join(self.base_dir, remote_name)
        # only download the file if it exists
        if self.client.check(path):
            self.client.download_sync(remote_path=path, local_path=local_name)

    def put_file(self, remote_name=None, local_name=None, overwrite=False):
        """
        Uploads a local file to webdav server
        Arguments:
        remote_name: full path of file on the server
        local_name: name of the file to upload. Add path if necessary.
        """
        assert remote_name is not None
        assert local_name is not None

        path = os.path.join(self.base_dir, remote_name)
        # only write the file if it doesn't exist
        if not self.client.check(path) or overwrite:
            self.client.upload_sync(remote_path=path, local_path=local_name)

    
    def put_file_async(self, remote_name=None, local_name=None, callback=None):
        """
        Uploads a file to webdav server asynchronously
        Arguments:
        remote_name: full path of file on the server
        local_name: name of the file to upload. Add path if necessary.
        callback: reference to function that is called after upload is completed
        """
        kwargs = {
            'remote_path': os.path.join(self.base_dir, remote_name),
            'local_path': local_name,
            'callback': callback
        }
        self.client.upload_async(**kwargs)

    def make_dir(self, dir_name) -> bool:
        """
        Creates a directory in the webdav server.
        Does nothing if folder already exists
        Arguments:
        dir_name: name of the folder
        Return:
        True if successful, False otherwise
        """
        return self.client.mkdir(dir_name)

    def check_dir_exists(self, dir_name):
        """
        Check if a folder exists on the webdav server
        Arguments:
        dir_name: name of the folder to check.
        """
        try:
            self.client.info(dir_name)
            return True
        except RemoteResourceNotFound as ex:
            return False

if __name__ == "__main__":
    con = WebdavConnector()
    files = con.check_dir_exists("eCallisto")
