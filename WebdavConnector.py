from webdav3.client import Client, RemoteResourceNotFound
from dotenv import load_dotenv
import os

"""
Offers basic functionality to interact with webdav server
Uses a .env file for configuration
"""
class WebdavConnector:
    def __init__(self) -> None:
        load_dotenv()
        options = {
            'webdav_hostname': os.environ.get('HOST_URL'),
            'webdav_login': os.environ.get('USERNAME'),
            'webdav_password': os.environ.get('PASSWORD'),
            'verbose': True
        }
        self.client = Client(options)


    def put_file(self, remote_name=None, local_name=None):
        """
        Uploads a local file to webdav server
        Arguments:
        remote_name: full path of file on the server
        local_name: name of the file to upload. Add path if necessary.
        """
        assert remote_name is not None
        assert local_name is not None
        
        self.client.upload_sync(remote_path=remote_name, local_path=local_name)
    
    def put_file_async(self, remote_name=None, local_name=None, callback=None):
        """
        Uploads a file to webdav server asynchronously
        Arguments:
        remote_name: full path of file on the server
        local_name: name of the file to upload. Add path if necessary.
        callback: reference to function that is called after upload is completed
        """
        kwargs = {
            'remote_path': remote_name,
            'local_path': local_name,
            'callback': callback
        }
        self.client.upload_async(**kwargs)

    def make_dir(self, dir_name):
        """
        Creates a directory in the webdav server.
        Does nothing if folder already exists
        Arguments:
        dir_name: name of the folder
        """
        self.client.mkdir(dir_name)

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


