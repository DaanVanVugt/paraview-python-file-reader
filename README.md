# Paraview Python File Readers
This repository contains some tools and examples to build Python Programmable Filters for ParaView which can act as file readers.

The basic idea is simple. We make a Python programmable filter that can take a list of `FileNames` as an argument.
Then we instruct ParaView to treat it as a `FileReader`. We must implement the functionality for reading timeseries ourselves,
since using this with `vtkFileSeriesReader` is not supported. This turns out to be not so difficult.

### References
- https://blog.kitware.com/easy-customization-of-the-paraview-python-programmable-filter-property-panel
- https://www.paraview.org/Wiki/Python_calculator_and_programmable_filter
- https://public.kitware.com/pipermail/paraview-developers/2017-January/005051.html

## Installation

1. Clone this repository
2. Run the python filter generator on your input file
```bash
./python_filter_generator paraview_read_npz.py reader.xml
```
3. Add `reader.xml` to your ParaView plugin list (Tools > Manage Plugins > Load New) (selecting autoload is useful)


### Local packages
Paraview automatically includes ~/.local/lib/python2.7/site-packages if it exists.
This is in disregard of the PYTHONNOUSERSITE environment variable when running `pvpython`.
Be sure to not have numpy (or h5py) installed there, as that might cause problems.
```bash
pip2 uninstall numpy h5py
```


### Building h5py against python paraview
HDF5 is a common format for

1. First install [https://github.com/pyenv/pyenv](pyenv)
2. Then run the following commands to install h5py with the same hdf5 as paraview

```bash
export PV_PY_VER=2.7.11
export PV_NP_VER=1.8.1
export PV_H5_VER=1.8.13
export PV_PY_UCS=2

export PYTHON_CONFIGURE_OPTS=--enable-unicode=ucs$PV_PY_UCS
# Install python2 with ucs2 https://stackoverflow.com/questions/38928942/build-python-as-ucs-4-via-pyenv
pyenv install -v $PV_PY_VER
pyenv local $PV_PY_VER

# Install pip
wget https://bootstrap.pypa.io/get-pip.py && ~/.pyenv/versions/$PV_PY_VER/python get-pip.py

# Install the same numpy paraview uses
~/.pyenv/versions/$PV_PY_VER/bin/pip install --user numpy==$PV_NP_VER cython==0.29

# Install hdf5 of the same version as paraview (not enough files included in binary paraview distribution to build against)
export PV_H5_MJ_VER=${PV_H5_VER%.*}
wget https://support.hdfgroup.org/ftp/HDF5/releases/hdf5-$PV_H5_MJ_VER/hdf5-$PV_H5_VER/src/hdf5-$PV_H5_VER.tar.bz2
tar jxf hdf5-$PV_H5_VER.tar.bz2
cd hdf5-$PV_H5_VER
./configure
make -j
make install

# Install h5py against theis hdf5 library
export HDF5_DIR=`pwd`/hdf5
~/.pyenv/versions/$PV_PY_VER/bin/pip install --no-binary=h5py --user h5py
```

## Known version numbers
You can fill in the version numbers below for your specific version of ParaView.

| ParaView version | Python version | Python UCS status | Numpy version | HDF5 version |
| ---------------- | -------------- | ----------------- | ------------- | ------------ |
| 5.4.1            | 2.7.11         | 2                 | 1.8.1         | 1.8.13       |
| 5.5.2            | 2.7.14         | 2                 | 1.8.1         | 1.8.13       |
| 5.6.0            | 2.7.??         | 4                 | 1.15.1        | 1.8.13       |


## Known issues

### Mismatch in library and header version
Sometimes the h5py installer does not correctly find the hdf5 version number. In that case you can set the HDF5_VERSION enviroment variable (to something like 1.8.13 depending on your version)

### ImportError
If you get an error like
```
ImportError:
Importing the multiarray numpy extension module failed.  Most
likely you are trying to import a failed build of numpy.
If you're working with a numpy git repo, try `git clean -xdf` (removes all
files not under version control).  Otherwise reinstall numpy.

Original error was: /home/daan/.local/lib/python2.7/site-packages/numpy/core/multiarray.so: undefined symbol: PyUnicodeUCS4_FromObject
```
you still have a numpy installed in .local/lib/python2.7/site-packages or some other directory in your PYTHONPATH

### Undefined symbol: PyUnicodeUCS4_DecodeUTF8
This error occurs when loading a python module which has binary extensions and is compiled for python with Unicode UCS4 support.
Trying to run it with the ParaView python interpreter (which has UCS2) will fail with an error like
```
ImportError: /home/daan/.local/lib/python2.7/site-packages/h5py/_errors.so: undefined symbol: PyUnicodeUCS4_DecodeUTF8
```
Follow the steps above to install a python with UCS2 and use that to compile your extensions.


## License
This work is licensed under the GPLv3 license. See the file LICENSE for more details.

## Contributing
Contributions are very welcome.
If you use this plugin to make a ParaView reader, please consider submitting it here as an example.
