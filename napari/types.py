from functools import wraps
from typing import Any, Callable, Dict, List, Tuple, Union, Type
from types import TracebackType

import numpy as np
import dask.array as da

try:
    import zarr
except ImportError:
    zarr = None

# This is a WOEFULLY inadequate stub for a duck-array type.
# Mostly, just a placeholder for the concept of needing an ArrayLike type.
# Ultimately, this should come from https://github.com/napari/image-types
# and should probably be replaced by a typing.Protocol
if zarr:
    ArrayLike = Union[np.ndarray, da.Array, zarr.Array]
else:
    ArrayLike = Union[np.ndarray, da.Array]

# layer data may be: (data,) (data, meta), or (data, meta, layer_type)
# using "Any" for the data type until ArrayLike is more mature.
LayerData = Union[Tuple[Any], Tuple[Any, Dict], Tuple[Any, Dict, str]]

PathLike = Union[str, List[str]]
ReaderFunction = Callable[[PathLike], List[LayerData]]

ExcInfo = Union[
    Tuple[Type[BaseException], BaseException, TracebackType],
    Tuple[None, None, None],
]


def image_reader_to_layerdata_reader(
    func: Callable[[PathLike], ArrayLike]
) -> ReaderFunction:
    """Convert a PathLike -> ArrayLike function to a PathLike -> LayerData.

    Parameters
    ----------
    func : Callable[[PathLike], ArrayLike]
        A function that accepts a string or list of strings, and returns an
        ArrayLike.

    Returns
    -------
    reader_function : Callable[[PathLike], List[LayerData]]
        A function that accepts a string or list of strings, and returns data
        as a list of LayerData: List[Tuple[ArrayLike]]
    """

    @wraps(func)
    def reader_function(*args, **kwargs) -> List[LayerData]:
        result = func(*args, **kwargs)
        return [(result,)]

    return reader_function
