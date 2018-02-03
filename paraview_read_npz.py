"""
Example python file reader demonstrating some of the features available for
python programmable file readers.

This file does not actually provide any output, but is just here to show the options
available when using python_filter_generator.

Daan van Vugt <daanvanvugt@gmail.com>
"""
Name = 'PythonFileReader'
Label = 'Read a file in ParaView using python'
Help = 'Example file reader using a Python Programmable Filter to act as a vtk source'
Extension = 'npz'
FileDescription = 'Numpy arrays'

import numpy as np
import OrderedDict

NumberOfInputs = 0
OutputDataType = 'vtkUnstructuredGrid'

# Create a new class to distinguish the list to select
# Keys = string names
# Values = 1 or 0 (enabled by default or not)
class ArraySelectionDomain(OrderedDict):
    pass
class PropertyGroup(OrderedDict):
    pass

# These properties are put in a panel where you can tune the properties of your
# source. The first element of each tuple is the name of the variable available
# in your python script, the second is the default value.
# Top-level tuples are propertygroups. One level below is a list of dictionaries for the elements
# Names are converted to labels by '_' > ' ' and uppercasing the first letter
Properties = OrderedDict([
    # Which variables to read from the file
    ('variables', ArraySelectionDomain([
        ('Psi', 1), ('u', 1), ('j', 1), ('w', 1), ('rho', 1), ('T', 1),
    ])),
    ('interpolation_options', PropertyGroup([
        ('number_of_subdivisions', dict(value=3, min=2, max=6)),
        ('quadratic', False),
    ])),
])


# from paraview import vtk is done automatically in the reader
def RequestData(self):
    """Create a VTK output given the list of filenames and the current timestep.
    This script can access self and FileNames and should return an output of type
    OutputDataType above"""

    def GetUpdateTimestep(algorithm):
        """Returns the requested time value, or None if not present"""
        executive = algorithm.GetExecutive()
        outInfo = executive.GetOutputInformation(0)
        return outInfo.Get(executive.UPDATE_TIME_STEP()) \
                if outInfo.Has(executive.UPDATE_TIME_STEP()) else None
    # Get the current timestep
    req_time = GetUpdateTimestep(self)

    # Read the closest file
    xtime = np.asarray([get_time(file) for file in FileNames])
    i = np.argmin(xtime - req_time)

    # output variable
    output = self.GetUnstructuredGridOutput()

    # Implement the create_vtk function yourself. Testing this is easier without paraview
    # below line is just an example.
    output = create_vtk(FileNames[i], n_sub=number_of_subdivisions, output=output)
    return output

"""
Given a list of filenames this script should output how many timesteps are available.

See paraview guide 13.2.2
"""
def RequestInformation(self):
    def setOutputTimesteps(algorithm):
        executive = algorithm.GetExecutive()
        outInfo = executive.GetOutputInformation(0)

        # Calculate list of timesteps here
        xtime = [get_time(file) for file in FileNames]

        outInfo.Remove(executive.TIME_STEPS())
        for i in range(len(FileNames)):
            outInfo.Append(executive.TIME_STEPS(), xtime[i])

        # Remove and set time range info
        outInfo.Remove(executive.TIME_RANGE())
        outInfo.Append(executive.TIME_RANGE(), xtime[0])
        outInfo.Append(executive.TIME_RANGE(), xtime[-1])

    setOutputTimesteps(self)
