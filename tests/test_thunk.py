import tempfile
from pathlib import Path

import xarray as xr

from zeitcache import zeitdelay


def create_dataset(dir):
    ds = xr.DataArray([1, 2, 3], dims="x")
    ds.name = "green eggs"
    return zeitdelay("green eggs", ds)


def test_thunk():
    with tempfile.TemporaryDirectory() as tempdir:
        temp_dir = Path(tempdir)
        thunk = create_dataset(temp_dir)
        thonk = lambda x: x.mean("x")
        assert thunk(thonk) == 2
