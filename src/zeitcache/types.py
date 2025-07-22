import logging

logger = logging.getLogger(__name__)

import xarray as xr


# determines if we're looking at a dataset or a dataarray, and then passes back
# the correct type and a hint that we're looking at the right one.
# make sure that you use a multiple assignment when unpacking!
def _da_or_ds(ds):
    if isinstance(ds, xr.DataArray):
        if ds.name is None:
            raise ValueError(
                "Resulting DataArray has no name, can't serialize cleanly."
            )
        logging.debug("Data passed in is a DataArray")
        return ("DataArray", ds)
    if isinstance(ds, xr.Dataset):
        if not ds.data_vars:
            raise ValueError("Dataset has no data_vars to cache.")
        logging.debug("Data passed in is a Dataset")
        return ("Dataset", ds)

    raise TypeError("Refusing to cache non-xarray object: got %s", type(ds))
