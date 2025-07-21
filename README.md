# zeitcache
*Stupid-fast functional caching for `xarray` pipelines*

## Introduction
`zeitcache` is a wrapper function for `xarray` methods that can automatically create and restore precomputed results for those methods, saving computing resources. It is especially useful for the following workflows:
- Reproducible scientific computing code, as you can write idiomatic code without having to worry about performance
- Rapid development, where there's no time for something more complicated like `snakemake` or `prefect`
- Improving performance of preexisting code, as `zeitcache` fits in transparently
- Situations where expensive reductions are commonplace in the code

If you have a `DataArray`, an immutable function to apply to it, and want to cut down on compute in the simplest way possible, `zeitcache` might be the library for you. It is similar to `joblib`, but significantly more optimized for scientific computing workflows and takes advantage of some unique advantages of `xarray` to make that possible. 

## Utilization
Simply take a call like this:
```python
dataset = dataset.mean(dims=('lat', 'lon', 'time'))
```
And rewrite it as this:
```python
@zeitcache(name_hint="my_dataset")
def reduction_simple(ds):
    return ds.mean(dims=('lat', 'lon', 'time'))

dataset = reduction_simple(dataset)
```
Just like that, you now have automatic caching. See the documentation for more information on how this works, and how to change `zeitcache`'s default settings. 

**Important:** you must remember to give each dataset a unique name, otherwise you risk collision! Also, `zeitcache`'s hashing algorithm doesn't actually check the data itself but rather its structure in order to make a hash. This works if and only if you make each name unique!

## License
This code is MIT licensed. Please follow the terms of that license. Also, if you end up using this in published work, please cite it. Even though it's small, attribution helps justify continued development. See `CITATION.cff` for details. 
