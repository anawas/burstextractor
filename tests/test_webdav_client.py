from radiospectra.sources import CallistoSpectrogram
import os
import sys
sys.path.insert(0, '..')
import webdav.WebdavConnector as wdav

BASE_DIR = "temp/"

if __name__ == "__main__":
    client = wdav.WebdavConnector()
    path = os.path.join(BASE_DIR, f"type_III")

    print("Searching file on server ...")
    client.get_file(os.path.join(path, "Arecibo-Observatory_20230203_1439_1443.fit.gz"), "downloaded.fit.gz")
    print("downloaded")

    spec = CallistoSpectrogram.read("downloaded.fit.gz")
    print(spec.header['snr'])
