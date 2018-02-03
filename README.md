# Paraview Python File Readers
This repository contains some tools and examples to build Python Programmable Filters for ParaView which can act as file readers.
It is based upon excellent work by Utkarsh and some tweaking by me.

The basic idea is simple. We make a Python programmable filter that can take a list of FileNames as an argument.
Then we instruct ParaView to treat it as a FileReader. We must implement the functionality for reading timeseries ourselves,
since using this with vtkFileSeriesReader is not supported. This turns out to be not so difficult.

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
3. Add `reader.xml` to your ParaView plugin list (Tools > Manage Plugins > Load New) (selecting autoload is handy)


### Local packages
Paraview automatically includes ~/.local/lib/python2.7/site-packages if it exists.
This is in disregard of the PYTHONNOUSERSITE environment variable (TODO create issue on paraview bug tracker) when running pvpython.
Be sure to not have numpy (or h5py) installed there, as that might cause problems.
```bash
pip2 uninstall numpy h5py
```


### Building h5py against python paraview
HDF5 is a common format for 

1. First install [https://github.com/pyenv/pyenv](pyenv)
2. Then run the following commands to install h5py with the same hdf5 as paraview

```bash
# run this script in ParaView-5.4.1-Qt5-OpenGL2-MPI-Linux-64bit or equivalent or set PV_DIR
export PV_DIR=$(pwd)

# Install python2 with ucs2 https://stackoverflow.com/questions/38928942/build-python-as-ucs-4-via-pyenv
export PYTHON_CONFIGURE_OPTS=--enable-unicode=ucs2
pyenv install -v 2.7.11
pyenv local 2.7.11

# Install pip
wget https://bootstrap.pypa.io/get-pip.py && ~/.pyenv/shims/python get-pip.py

# Install the same numpy paraview uses (as of writing)
~/.pyenv/versions/2.7.11/bin/pip install --user numpy==1.8.1

# Install hdf5 of the same version as paraview (not enough files included in binary paraview distribution to build against)
# Paraview 5.2 - 5.4.1 are using 1.8.13, I have not checked the rest
# We then take the install summary 
cd ~
wget https://support.hdfgroup.org/ftp/HDF5/releases/hdf5-1.8/hdf5-1.8.13/src/hdf5-1.8.13.tar.bz2
tar jxf hdf5-1.8.13.tar.bz2
cd hdf5-1.8.13
./configure
make -j
make install # in ~/hdf5-1.8.13/hdf5

# Install h5py against the paraview hdf5 libraries
export HDF5_DIR=~/hdf5-1.8.13/hdf5
~/.pyenv/versions/2.7.11/bin/pip install --no-binary=h5py --user h5py

# Copy it to your paraview folder to make a portable version, or leave it in your local site-packages
mv ~/.local/lib/python2.7/site-packages/h5py $PV_DIR/lib/python2.7/site-packages/
# Create symlinks to the paraview library files (since we built against slightly different hdf5 the name is different)
cd $PV_DIR/lib/paraview-*
ln -s libhdf5.so.8.0.2 libhdf5.so.8
ln -s libhdf5_hl.so.8.0.2 libhdf5_hl.so.8

# Clean up
rm -r ~/hdf5-1.8.13.tar.bz2 ~/hdf5-1.8.13
```



## Known issues

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
This work is licensed under the GPL v3 license. See the file LICENSE for more details.

## Contributing
Contributions are very welcome.
If you use this plugin to make a reader for a known filetype, please consider submitting it here as an example.
