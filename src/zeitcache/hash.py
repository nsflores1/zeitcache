import hashlib
import logging

logger = logging.getLogger(__name__)


# tiny helper that encodes a string
# TODO: maybe remove we don't call it anywhere anymore???
def _hash_string(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


# this is the simple, O(1) way of hashing a dataset, but it's absolutely
# inadequate for most complicated needs.
# TODO: allow the user to pass a hashing function instead of this
def _hash_dataset_naive(ds):
    h = hashlib.sha256()
    h.update(str(ds.name).encode())
    h.update(str(ds.shape).encode())
    h.update(str(ds.dtype).encode())
    h.update(str(ds.coords).encode())
    h.update(str(ds.attrs).encode())
    return h.hexdigest()
