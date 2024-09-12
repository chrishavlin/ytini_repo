Welcome to Ytini!  Please enjoy!

Documentation, tutorials, sample data downloads, and more are available at www.ytini.com

## Installing vdbyt 

`vdbyt` is a helper package for export yt data in openvdb files, based on generalizations of 
the scripts in the `/AMR` and `/vdbConverters` directories of this repository. 

Installation depends on your environment and architecture, in particular, the availability of openvdb.

### Conda 

If you use conda and on one of the platforms for which openvdb has a build (https://anaconda.org/conda-forge/openvdb), 
you can create a new environment from the `environment.yml` file included in this repo and then 
install `vdbyt` with:

``` 
$ conda env create -f environment.yml
$ conda activate vdbyt
$ python -m pip install . 
```

## Using vdbyt 

For command line interface, 

``` 
$ vdbyt
```