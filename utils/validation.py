import numpy as np
from radiospectra.sources import CallistoSpectrogram


def calculate_snr(spectrogram: CallistoSpectrogram) -> float:
    """
    Calculates the signal to noise ratio of a spectrogram
    """
    signal = np.nanmean(spectrogram.data)
    noise = np.nanstd(spectrogram.data)
    return signal/noise


def has_burst_data(spectrogram: CallistoSpectrogram) -> bool:
    std = np.nanstd(spectrogram.data)
    time_mean = np.nanmean(spectrogram.data, axis=0)
    # print(f"{spectrogram.header['INSTRUME']}  std = {std}, max = {np.max(time_mean)}")
    if np.max(time_mean) >= 2.*std:
        return True
    return False


if __name__ == "__main__":
    import glob
    import shutil

    from tqdm import tqdm

    files = glob.glob("temp/*.fit.gz")
    files.sort()
    valid_files = []
    out = open("data.csv", "w")

    for i in tqdm(range(len(files)), ascii=True):
        s = CallistoSpectrogram.read(files[i])
        if has_burst_data(s):
            valid_files.append(files[i])
            out.write(f"{s.header['snr']}\n")
    print(f"Valid spectrograms: {len(files)}")

    for i in tqdm(range(len(valid_files)), ascii=True):
        fit_filename = valid_files[i].split("/")[1]
        jpg_filename = fit_filename.replace("fit.gz", "jpg")
        shutil.copy(valid_files[i], f"temp/valid/{fit_filename}")
        shutil.copy(f"temp/{jpg_filename}", f"temp/valid/{jpg_filename}")
