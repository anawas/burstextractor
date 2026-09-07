import os

from radiospectra.sources import CallistoSpectrogram

from connectors.webdavconnector import WebdavConnector

BASE_DIR = "temp/"

if __name__ == "__main__":
    client = WebdavConnector()
    path = os.path.join(BASE_DIR, "type_III")

    print("Searching file on server ...")
    client.get_file(os.path.join(path, "Arecibo-Observatory_20230203_1439_1443.fit.gz"), "downloaded.fit.gz")
    print("downloaded")

    spec = CallistoSpectrogram.read("downloaded.fit.gz")
    print(spec.header['snr'])
