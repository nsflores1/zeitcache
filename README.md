# zeitcache
*Stupid-fast functional-flavored caching for `xarray` pipelines*

## Introduction
`zeitcache` is a wrapper function for `xarray` methods that can automatically create and restore precomputed results for those methods, saving computing resources. It is especially useful for the following workflows:
- Reproducible scientific computing code, so you can write idiomatic code without having to worry about performance
- Rapid development, where there's no time for something more complicated like `snakemake` or `prefect`
- Improving performance of preexisting code, as `zeitcache` fits in transparently
- Situations where expensive reductions are commonplace in the code

If you have a `DataArray`, an immutable function to apply to it, and want to cut down on compute in the simplest way possible, `zeitcache` might be the library for you. It is similar to `joblib`, but significantly more optimized for scientific computing workflows and takes advantage of some unique advantages of `xarray` to make that possible. 

## Utilization
Simply take a call like this:
```python
from zeitcache import zeitcache

dataset = dataset.mean(dims=('lat', 'lon', 'time'))
```
And rewrite it as this:
```python
@zeitcache(name_hint="my_dataset")
def reduction_simple(ds):
    return ds.mean(dims=('lat', 'lon', 'time'))

dataset = reduction_simple(dataset)
```
Just like that, you now have automatic caching. You can also do something more imperative, if that's your style:
```python
def reduction_simple(ds):
    return ds.mean(dims=('lat', 'lon', 'time'))

dataset = zeitforce("my_dataset", dataset, reduction_simple) 
```
Alternatively, if you'd prefer not to do the caching immediately, or want to map functions onto thunks later on (maybe functional programming is more your style), you can use `zeitdelay` to do that:
```python
dataset_thunk = zeitdelay("my_dataset", dataset)
# some time later
def some_expensive_function(ds):
    ...
result = dataset_thunk(some_expensive_function)
```
Do note that this makes your code harder to read.

**Important:** you must remember to give each dataset a unique name, otherwise you risk collision! Also, `zeitcache`'s hashing algorithm doesn't actually check the data itself but rather its structure in order to make a hash. This works if and only if you make each name unique!

Please see the docstrings for more information on how to use each function.

## Future Work
These are roughly ordered from most to least important.
- Allow users to pass an alternative hashing function
- Ship a not-O(1) hashing function as an alternative
- Make the code even lazier internally
- Support more types of compression algorithms for different needs

## The Name
In German, "zeit" means time, and "cache" is the same thing as in English. That's what this software usually does: it caches time. A native speaker could also read it as "Zeitkasse", which means something like "time checkout" or "time cash register", and that's fitting too, since the cached data are things you can withdraw from later to save on time.

## License
This code is MIT licensed. Please follow the terms of that license. Also, if you end up using this in published work, please cite it. Even though it's small, attribution helps justify continued development. See `CITATION.cff` for details. 
