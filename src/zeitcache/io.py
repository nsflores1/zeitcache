import io
import logging
import os
import tempfile

logger = logging.getLogger(__name__)

import xarray as xr
import zstandard as zstd

from .types import _da_or_ds


# paranoid directory creation
def _setup_directory(path):
    try:
        os.makedirs(path, exist_ok=True)
    except PermissionError as e:
        raise RuntimeError(
            "Cannot create cache directory, permission denied: %s" % e
        ) from e
    except OSError as e:
        raise RuntimeError("Failed to create cache directory: %s" % e) from e
    else:
        logging.debug("Path %s successfully created", path)
        return True


# put a filename in, read dataset from disk
# TODO: make a lazy rewrite of this
def _eager_read_buffer(path):
    dctx = zstd.ZstdDecompressor()
    with open(path + ".zstd", "rb") as file_in:
        with dctx.stream_reader(file_in) as reader:
            # this read is eager! might exhaust RAM!
            buffer = io.BytesIO(reader.read())
    logging.debug("Path %s successfully read in", path)
    ds = xr.load_dataset(buffer)
    # from when we cached it before
    if "_zeitcache_type" in ds.attrs and ds.attrs["_zeitcache_type"] == "DataArray":
        if len(ds.data_vars) != 1:
            raise ValueError("Expected single-variable Dataset for cached DataArray.")
        item = next(iter(ds.data_vars.values()))
        logger.debug("DataArray loaded from cache with var %s", item.name)
        return item
    # it's not a DataArray
    logger.debug("Dataset loaded from cache")
    return ds


# put a filename in, write dataset to disk
def _eager_write_buffer(ds, ds_name, cache_path):
    with tempfile.NamedTemporaryFile(suffix=".nc", delete=False) as tmp_file:
        tmp_path = tmp_file.name
        # note to our future selves what we're looking at
        if isinstance(ds, xr.DataArray):
            ds.attrs["_zeitcache_type"] = "DataArray"
        # catch a bunch of errors
        info_string, ds = _da_or_ds(ds)
        ds.to_dataset(name=ds_name).to_netcdf(tmp_file, engine="netcdf4")
        logging.debug(
            "Data %s of type %s saved to temp file successfully"
            % (ds_name, info_string)
        )
    try:
        with open(tmp_path, "rb") as file_in:
            cctx = zstd.ZstdCompressor()
            compressed = cctx.compress(file_in.read())
        with open(cache_path + ".zstd", "wb") as file_out:
            file_out.write(compressed)
            logging.debug(
                "Data %s of type %s compressed to disk successfully"
                % (ds_name, info_string)
            )
    finally:
        os.remove(tmp_path)
        logging.debug("Temp file at %s successfully deleted", tmp_path)
        return ds
