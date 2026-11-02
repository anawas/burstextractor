"""
Compatibility shim for radiospectra @ fe514c8, whose Spectrogram.plot calls
matplotlib.cm.get_cmap(). That function was removed in matplotlib 3.9.

Importing this module restores it. Import it before plotting a spectrogram.
It can go once radiospectra is unpinned.
"""
import matplotlib
import matplotlib.cm
import matplotlib.colors


def _get_cmap(name=None, lut=None):
    if name is None:
        name = matplotlib.rcParams["image.cmap"]
    if isinstance(name, matplotlib.colors.Colormap):
        return name
    cmap = matplotlib.colormaps[name]
    # Return a copy. The caller mutates the result via set_bad and must not
    # alter the globally registered colormap.
    return cmap.resampled(lut) if lut is not None else cmap.copy()


if not hasattr(matplotlib.cm, "get_cmap"):
    matplotlib.cm.get_cmap = _get_cmap
