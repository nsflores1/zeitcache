import tempfile

import xarray as xr

from zeitcache import zeitforce


def test_imperative():
    ds = xr.DataArray([1, 2, 3], dims="x")
    ds.name = "spam"

    def reduce(ds):
        return ds.mean("x")

    with tempfile.TemporaryDirectory() as scratch:
        result = zeitforce("spam", ds, reduce, log_level=10, cache_dir=scratch)
        assert result == reduce(ds)
