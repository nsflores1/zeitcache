import tempfile

import xarray as xr

from zeitcache import zeitcache


def test_cache_basic():
    ds = xr.DataArray([3, 4, 5], dims="x")
    ds.name = "eggs"
    with tempfile.TemporaryDirectory() as scratch:

        @zeitcache("eggs", log_level=10, cache_dir=scratch)
        def mean_it(x):
            return x.mean("x")

        assert mean_it(ds).item() == 4
