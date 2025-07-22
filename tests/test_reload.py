import tempfile
import os
from pathlib import Path

import xarray as xr

from zeitcache import zeitforce


def create_dataset(dir):
    ds = xr.DataArray([1, 2, 3], dims="x")
    ds.name = "spam"

    def reduce(ds):
        return ds.mean("x")

    return zeitforce("spam", ds, reduce, log_level=10, cache_dir=dir)


def create_dataset_again(dir):
    ds = xr.DataArray([1, 2, 3], dims="x")
    ds.name = "spam"

    def reduce(ds):
        return ds.mean("x")

    return zeitforce("spam", ds, reduce, log_level=10, cache_dir=dir)


def test_reload():
    with tempfile.TemporaryDirectory() as tempdir:
        temp_dir = Path(tempdir)
        thing1 = create_dataset(temp_dir)
        thing2 = create_dataset_again(temp_dir)
        assert len(os.listdir(temp_dir)) == 1
