import functools
import logging
import os

logger = logging.getLogger(__name__)

from .hash import _hash_dataset_naive
from .io import _eager_read_buffer, _eager_write_buffer, _setup_directory


# the imperative non-decorator version. always does something NOW
def zeitforce(name_hint, data, fn, *, log_level=30, cache_dir="./cache", kwargs=None):
    """
    Directly cache the result of applying a function to a DataArray or Dataset, saving to disk with a ZSTD-compressed netCDF.

    parameters
    ----------
    name_hint: str
        A user-provided name for identifying the cached dataset. Must be unique.
    data: DataArray or Dataset
        The data that you wish to cache.
    fn: function
        Function that will be applied to the data.
    log_level: int, optional
        Python logging level. Default is 30 (WARNING).
    cache_dir: str, optional
        Path to a cache directory. Default is './cache'.
    kwargs: dict, optional
        Keyword arguments passed to the function.

    returns
    -------
    DataArray or Dataset
        This depends on what your passed datatype is.
    """
    return _invoke(name_hint, data, fn, kwargs or {}, log_level, cache_dir)


# the imperative decorator version. always does something NOW
def zeitcache(name_hint, *, log_level=30, cache_dir="./cache", kwargs=None):
    """
    Cache the result of applying a function to a DataArray or Dataset, saving to disk with a ZSTD-compressed netCDF.

    parameters
    ----------
    name_hint: str
        A user-provided name for identifying the cached dataset. Must be unique.
    log_level: int, optional
        Python logging level. Default is 30 (WARNING).
    cache_dir: str, optional
        Path to a cache directory. Default is './cache'.
    kwargs: dict, optional
        Keyword arguments passed to the function.

    returns
    -------
    function
        A wrapped function that transparently caches its results.
    """

    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(data):
            return _invoke(name_hint, data, fn, kwargs or {}, log_level, cache_dir)

        return wrapper

    # case 1: used as a decorator, zeitcache(...) returns a decorator
    if name_hint is not None and not callable(name_hint):
        return decorator

    # case 2: used as @zeitcache, shift args around
    elif callable(name_hint):
        raise TypeError(
            "You must use `@zeitcache(...)` with parameters, not bare `@zeitcache`."
        )

    # fallback / broken
    raise TypeError(
        "Invalid usage of `zeitcache`. Use as either a decorator or as a function."
    )


# the lazy FP way. always does something later and returns a thunk
# this is made explicit since thunks are rare in python
def zeitdelay(name_hint, data, **opts):
    """
    Creates a thunk to call zeitcache() at a later time with a curried function.

    parameters
    ----------
    name_hint: str
        A user-provided name for identifying the cached dataset. Must be unique.
    data: DataArray or Dataset
        The data that you wish to cache.
    **opts: named arguments, optional
        Any further arguments you wish to pass to zeitcache().

    returns
    -------
    DataArray or Dataset
        This depends on what your passed datatype is.
    """
    return lambda fn: zeitforce(name_hint, data, fn, **opts)


# the thing that actually does all the heavy lifting
def _invoke(name_hint, data, fn=None, kwargs=None, log_level=30, cache_dir="./cache"):
    logging.basicConfig(
        level=log_level, format="%(asctime)s %(name)s [%(levelname)s] %(message)s"
    )
    # sanity fix
    kwargs = {} if kwargs is None else kwargs
    # we are ready to go!
    logger.info("Checking cache for %s...", name_hint)
    # make it if it doesn't exist, or exit now
    _setup_directory(cache_dir)

    hash_key = "".join(_hash_dataset_naive(data))
    cache_path = os.path.join(cache_dir, f"{name_hint}_{hash_key}.nc")
    logger.debug("Hash: %s", (name_hint + "_" + hash_key))

    if os.path.exists(cache_path + ".zstd"):
        logger.debug("Cache hit for %s!", name_hint)
        cache_data = _eager_read_buffer(cache_path)
        logger.info("Successfully loaded cache for %s", name_hint)
        return cache_data

    logger.debug("No cache, calculating...")
    result = fn(data, **kwargs) if fn is not None else data
    cache_data = _eager_write_buffer(result, name_hint, cache_path)
    logger.info("Successfully created cache for %s", name_hint)
    return cache_data
