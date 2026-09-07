# burstextractor
## Usage
Code for the Citizen Science project "Raumschiff" from FHNW. It downloads the manually compiled solar radio burst list (compiled by C. Monstein) and extracts the bursts from e-Callisto data files.

## Setup
The project is managed with [uv](https://docs.astral.sh/uv/). It pins Python 3.12
via `.python-version` and locks all dependencies in `uv.lock`.

```sh
uv sync                     # create .venv and install the locked dependencies
uv run main.py --year 2023 --month 6
uv run pytest
```

`uv sync` downloads the interpreter if it is missing, so no separate Python or
conda install is needed. Add dependencies with `uv add <package>`; commit the
resulting `uv.lock` so everyone builds the same environment.

The `ecallisto` dependency group is only needed by `utils/ecallisto_handler.py`:

```sh
uv sync --group ecallisto
```

## Links
- The Citizen Science Project: https://raumschiff.org/project/sonnenforschung/
- The above mentioned list: http://soleil.i4ds.ch/solarradio/data/BurstLists/2010-yyyy_Monstein/
  
## Citation
[The FITS files in e-Callisto] (https://doi.org/10.48322/pmwd-mk15)
