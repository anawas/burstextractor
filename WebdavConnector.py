from webdav3.client import Client, RemoteResourceNotFound
from dotenv import load_dotenv
import os

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
        assert remote_name is not None
        assert local_name is not None
        
        self.client.upload_sync(remote_path=remote_name, local_path=local_name)
    
    def put_file_async(self, remote_name=None, local_name=None, callback=None):
        kwargs = {
            'remote_path': remote_name,
            'local_path': local_name,
            'callback': callback
        }
        self.client.upload_async(**kwargs)

    def make_dir(self, dir_name):
        self.client.mkdir(dir_name)

    def check_dir_exists(self, dir_name):
        try:
            self.client.info(dir_name)
            return True
        except RemoteResourceNotFound as ex:
            return False



