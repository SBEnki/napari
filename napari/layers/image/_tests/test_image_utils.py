import dask.array as da
import numpy as np
import pytest
from skimage.transform import pyramid_gaussian
from napari.layers.image._image_utils import (
    guess_pyramid,
    guess_rgb,
)


data_dask = da.random.random(
    size=(100_000, 1000, 1000), chunks=(1, 1000, 1000)
)


def test_guess_rgb():
    shape = (10, 15)
    assert not guess_rgb(shape)

    shape = (10, 15, 6)
    assert not guess_rgb(shape)

    shape = (10, 15, 3)
    assert guess_rgb(shape)

    shape = (10, 15, 4)
    assert guess_rgb(shape)


def test_guess_pyramid():
    data = np.random.random((10, 15))
    assert not guess_pyramid(data)

    data = np.random.random((10, 15, 6))
    assert not guess_pyramid(data)

    data = [np.random.random((10, 15, 6))]
    assert not guess_pyramid(data)

    data = [np.random.random((10, 15, 6)), np.random.random((10, 15, 6))]
    assert not guess_pyramid(data)

    data = [np.random.random((10, 15, 6)), np.random.random((5, 7, 3))]
    assert guess_pyramid(data)

    data = [np.random.random((10, 15, 6)), np.random.random((10, 7, 3))]
    assert guess_pyramid(data)

    data = tuple(data)
    assert guess_pyramid(data)

    data = tuple(
        pyramid_gaussian(np.random.random((10, 15)), multichannel=False)
    )
    assert guess_pyramid(data)

    data = np.asarray(
        tuple(pyramid_gaussian(np.random.random((10, 15)), multichannel=False))
    )
    assert guess_pyramid(data)

    # Check for integer overflow with big data
    s = 8192
    data = [da.ones((s,) * 3), da.ones((s // 2,) * 3), da.ones((s // 4,) * 3)]
    assert guess_pyramid(data)


@pytest.mark.timeout(2)
def test_timing_is_pyramid_big():
    assert not guess_pyramid(data_dask)
