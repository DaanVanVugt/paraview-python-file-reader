#!/usr/bin/env python2

import os
import sys
import inspect
import textwrap


def escapeForXmlAttribute(s):
  # http://www.w3.org/TR/2000/WD-xml-c14n-20000119.html#charescaping
  # In character data and attribute values, the character information items "<" and "&" are represented by "&lt;" and "&amp;" respectively.
  # In attribute values, the double-quote character information item (") is represented by "&quot;".
  # In attribute values, the character information items TAB (#x9), newline (#xA), and carriage-return (#xD) are represented by "&#x9;", "&#xA;", and "&#xD;" respectively.

  s = s.replace('&', '&amp;') # Must be done first!
  s = s.replace('<', '&lt;')
  s = s.replace('>', '&gt;')
  s = s.replace('"', '&quot;')
  s = s.replace('\r', '&#xD;')
  s = s.replace('\n', '&#xA;')
  s = s.replace('\t', '&#x9;')
  return s



def getScriptPropertiesXml(info):
  e = escapeForXmlAttribute
  requestData = e(info['RequestData'])
  requestInformation = e(info['RequestInformation'])
  requestUpdateExtent = e(info['RequestUpdateExtent'])

  if requestData:
    requestData = '''
    <StringVectorProperty
    name="Script"
    command="SetScript"
    number_of_elements="1"
    default_values="%s"
    panel_visibility="advanced">
    <Hints>
    <Widget type="multi_line"/>
    </Hints>
    <Documentation>This property contains the text of a python program that
    the programmable source runs.</Documentation>
    </StringVectorProperty>''' % requestData

  if requestInformation:
    requestInformation = '''
    <StringVectorProperty
    name="InformationScript"
    label="RequestInformation Script"
    command="SetInformationScript"
    number_of_elements="1"
    default_values="%s"
    panel_visibility="advanced">
    <Hints>
    <Widget type="multi_line" />
    </Hints>
    <Documentation>This property is a python script that is executed during
    the RequestInformation pipeline pass. Use this to provide information
    such as WHOLE_EXTENT to the pipeline downstream.</Documentation>
    </StringVectorProperty>''' % requestInformation

  if requestUpdateExtent:
    requestUpdateExtent = '''
    <StringVectorProperty
    name="UpdateExtentScript"
    label="RequestUpdateExtent Script"
    command="SetUpdateExtentScript"
    number_of_elements="1"
    default_values="%s"
    panel_visibility="advanced">
    <Hints>
    <Widget type="multi_line" />
    </Hints>
    <Documentation>This property is a python script that is executed during
    the RequestUpdateExtent pipeline pass. Use this to modify the update
    extent that your filter ask up stream for.</Documentation>
    </StringVectorProperty>''' % requestUpdateExtent

  return '\n'.join([requestData, requestInformation, requestUpdateExtent])



def getPythonPathProperty(paths=[]):
  return '''
    <StringVectorProperty command="SetPythonPath"
    name="PythonPath"
    number_of_elements="1"
    default_values="'%s'"
    panel_visibility="advanced">
    <Documentation>A semi-colon (;) separated list of directories to add to
    the python library search path.</Documentation>
    </StringVectorProperty>'''%"';'".join(paths)


def nameToLabel(name):
  s = name.replace('_', ' ')
  return s[0].upper() + s[1:]

def getArraySelectionXml(prop, propertyName):
  e = escapeForXmlAttribute
  propertyName = e(propertyName)
  propertyLabel = nameToLabel(propertyName)
  l=[]
  [l.extend([e(str(k)),e(str(v))]) for k,v in prop.items()]
  numberOfElements = len(prop)*2
  defaultValues = ','.join(l)

  return '''
  <StringVectorProperty name="%s"
  command="SetParameter"
  number_of_elements="%s" 
  repeat_command="1" number_of_elements_per_command="2"
  element_types="2 0"
  default_values="%s"
  default_values_delimiter=","
  label="%s">
  <ArraySelectionDomain name="array_list">
  %s
  </ArraySelectionDomain>
  </StringVectorProperty>''' % (propertyName, numberOfElements, defaultValues, propertyLabel,
                                '\n'.join(['    <String name="%s" value="%s" />'%(k,k) for k in prop]))


def getFilterPropertyXml(prop, propertyName):
  e = escapeForXmlAttribute
  propertyName = e(propertyName)
  propertyLabel = nameToLabel(propertyName)
  if not isinstance(prop, dict):
    prop = dict(value=prop)

  if isinstance(prop['value'], list):
    numberOfElements = len(prop['value'])
    assert numberOfElements > 0
    propertyType = type(prop['value'][0])
    defaultValues = ' '.join([e(str(v)) for v in prop['value']])
  else:
    numberOfElements = 1
    propertyType = type(prop['value'])
    defaultValues = e(str(prop['value']))

  if propertyType is bool:
    defaultValues = defaultValues.replace('True', '1').replace('False', '0')

    return '''
      <IntVectorProperty
      name="%s"
      label="%s"
      initial_string="%s"
      command="SetParameter"
      animateable="1"
      default_values="%s"
      number_of_elements="%s">
      <BooleanDomain name="bool" />
      <Documentation></Documentation>
      </IntVectorProperty>''' % (propertyName, propertyLabel, propertyName, defaultValues, numberOfElements)


  if propertyType is int:
    if 'min' in prop and 'max' in prop:
      domain = '<IntRangeDomain name="range" min="%s" max="%s" />'%(prop['min'], prop['max'])
    else:
      domain = ''

    return '''
      <IntVectorProperty
      name="%s"
      label="%s"
      initial_string="%s"
      command="SetParameter"
      animateable="1"
      default_values="%s"
      number_of_elements="%s">
      <Documentation></Documentation>
      %s
      </IntVectorProperty>''' % (propertyName, propertyLabel, propertyName, defaultValues, numberOfElements, domain)

  if propertyType is float:
    if 'min' in prop and 'max' in prop:
      domain = '<DoubleRangeDomain name="range" min="%s" max="%s" />'%(prop['min'], prop['max'])
    else:
      domain = ''
    if 'widget' in prop:
      widget = 'panel_widget="%s"'%(prop['widget'])
    else:
      widget = ''
    return '''
    <DoubleVectorProperty
    name="%s"
    label="%s"
    initial_string="%s"
    command="SetParameter"
    animateable="1"
    default_values="%s"
    %s
    number_of_elements="%s">
    <Documentation></Documentation>
    %s
    </DoubleVectorProperty>''' % (propertyName, propertyLabel, propertyName, defaultValues, widget, numberOfElements, domain)

  if propertyType is str:
    return '''
    <StringVectorProperty
    name="%s"
    label="%s"
    initial_string="%s"
    command="SetParameter"
    animateable="1"
    default_values="%s"
    number_of_elements="%s">
    <Documentation></Documentation>
    </StringVectorProperty>''' % (propertyName, propertyLabel, propertyName, defaultValues, numberOfElements)

  raise Exception('Unknown property type: %r' % propertyType)


def getFilterPropertiesXml(prop):
  """Walk through an OrderedDict converting it to XML"""
  all_xml = ''
  for k in prop:
    v = prop[k]
    # bit hacky
    if v.__class__.__name__ is 'PropertyGroup':
      xml = [getFilterPropertyXml(v[name], name) for name in v]
      # Add properties
      all_xml += '\n\n'.join(xml)
      # Create a propertygroup
      all_xml += '\n\n' + getPropertyGroupXml(k, v.keys())
    elif v.__class__.__name__ is 'ArraySelectionDomain':
      all_xml += '\n\n' + getArraySelectionXml(v, propertyName=k)
    else:
      all_xml += '\n\n' + getFilterPropertyXml(v, propertyName=k) 
  return all_xml

def getPropertyGroupXml(name, propnames):
  s = '<PropertyGroup label="%s">\n' % (nameToLabel(name),)
  for propname in propnames:
    s += '  <Property name="%s" />\n' % (propname,)
  s += '</PropertyGroup>\n'
  return s


def getNumberOfInputs(info):
  return info.get('NumberOfInputs', 1)


def getInputPropertyXml(info):
  numberOfInputs = getNumberOfInputs(info)
  if not numberOfInputs:
    return ''


  inputDataType = info.get('InputDataType', 'vtkDataObject')

  inputDataTypeDomain = ''
  if inputDataType:
    inputDataTypeDomain = '''
    <DataTypeDomain name="input_type">
    <DataType value="%s"/>
    </DataTypeDomain>''' % inputDataType

  inputPropertyAttributes = 'command="SetInputConnection"'
  if numberOfInputs > 1:
    inputPropertyAttributes = '''\
        clean_command="RemoveAllInputs"
    command="AddInputConnection"
    multiple_input="1"'''

  inputPropertyXml = '''
  <InputProperty
  name="Input"
  %s>
  <ProxyGroupDomain name="groups">
  <Group name="sources"/>
  <Group name="filters"/>
  </ProxyGroupDomain>
  %s
  </InputProperty>''' % (inputPropertyAttributes, inputDataTypeDomain)

  return inputPropertyXml


def getOutputDataSetTypeXml(info):
  outputDataType = info.get('OutputDataType', '')

  typeMap = {

    '' : 8, # same as input
    'vtkPolyData' : 0,
    'vtkStructuredGrid' : 2,
    'vtkRectilinearGrid' : 3,
    'vtkUnstructuredGrid' : 4,
    'vtkImageData' : 6,
    'vtkUniformGrid' : 10,
    'vtkMultiblockDataSet' : 13,
    'vtkHierarchicalBoxDataSet' : 15,
    'vtkTable' : 19
  }

  typeValue = typeMap[outputDataType]

  return '''
  <!-- Output data type: "%s" -->
  <IntVectorProperty command="SetOutputDataSetType"
  default_values="%s"
  name="OutputDataSetType"
  number_of_elements="1"
  panel_visibility="never">
  <Documentation>The value of this property determines the dataset type
  for the output of the programmable filter.</Documentation>
  </IntVectorProperty>''' % (outputDataType or 'Same as input', typeValue)


def getProxyGroup(info):
  return 'sources' if getNumberOfInputs(info) == 0 else 'filters'

def getFileReaderXml(info):
  extension = info.get('Extension', '')
  fileDescription = info.get('FileDescription', '')
  return '''
    <StringVectorProperty
    name="FileNames"
    initial_string="FileNames"
    animateable="0"
    number_of_elements="0" 
    command="AddParameter"
    clean_command="ClearParameter"
    repeat_command="1"
    panel_visibility="advanced">
    <FileListDomain name="files"/>
    <Documentation>
    The list of files to be read by the reader.
    </Documentation>
    </StringVectorProperty>

    <DoubleVectorProperty 
    name="TimestepValues"
    repeatable="1"
    information_only="1">
    <TimeStepsInformationHelper/>
    <Documentation>
    Available timestep values.
    </Documentation>
    </DoubleVectorProperty>
    <Hints>
    <ReaderFactory extensions="%s"
    file_description="%s" />
    </Hints>
    '''%(extension, fileDescription)


def generatePythonFilter(info):
  e = escapeForXmlAttribute

  proxyName = info['Name']
  proxyLabel = info['Label']
  shortHelp = e(info['Help'])
  longHelp = e(info['Help'])
  extraXml = info.get('ExtraXml', '')

  proxyGroup = getProxyGroup(info)
  inputPropertyXml = getInputPropertyXml(info)
  outputDataSetType = getOutputDataSetTypeXml(info)
  scriptProperties = getScriptPropertiesXml(info)
  if 'Properties' in info:
    filterProperties = getFilterPropertiesXml(info['Properties'])
  else:
    filterProperties = ''
  fileReaderProperties = getFileReaderXml(info)

  # Get paths to put in the file by default
  pathProperty     = getPythonPathProperty(info.get('PythonPaths',[]))

  outputXml = '''\
<ServerManagerConfiguration>
  <ProxyGroup name="%s">
  <SourceProxy name="%s" class="vtkPythonProgrammableFilter" label="%s">
  <Documentation
  long_help="%s"
  short_help="%s">
  </Documentation>


%s

%s

%s

%s

%s

%s

%s

  </SourceProxy>
  </ProxyGroup>
</ServerManagerConfiguration>
    ''' % (proxyGroup, proxyName, proxyLabel, longHelp, shortHelp,
           inputPropertyXml, fileReaderProperties,
           filterProperties, extraXml, pathProperty, outputDataSetType,
           scriptProperties)

  return textwrap.dedent(outputXml)




def replaceFunctionWithSourceString(namespace, functionName, allowEmpty=False):
  func = namespace.get(functionName)
  if not func:
    if allowEmpty:
      namespace[functionName] = ''
      return
    else:
      raise Exception('Function %s not found in input source code.' % functionName)

  if not inspect.isfunction(func):
    raise Exception('Object %s is not a function object.' % functionName)

  lines = inspect.getsourcelines(func)[0]

  if len(lines) <= 1:
    raise Exception('Function %s must not be a single line of code.' % functionName)

  # skip first line (the declaration) and then dedent the source code
  sourceCode = textwrap.dedent(''.join(lines[1:]))

  # Loop for any include statements
  newCode = ""
  for line in sourceCode.split("\n"):
    if (line.startswith("#include")):
      file = line.split("'")[1]
      newCode = newCode + "\n" + open(file, 'r').read()
    else:
      newCode = newCode + "\n" + line

  namespace[functionName] = newCode


def generatePythonFilterFromFiles(scriptFile, outputFile):
  namespace = {}
  execfile(scriptFile, namespace)

  replaceFunctionWithSourceString(namespace, 'RequestData')
  replaceFunctionWithSourceString(namespace, 'RequestInformation', allowEmpty=True)
  replaceFunctionWithSourceString(namespace, 'RequestUpdateExtent', allowEmpty=True)

  xmlOutput = generatePythonFilter(namespace)

  open(outputFile, 'w').write(xmlOutput)


def main():
  if len(sys.argv) != 3:
    print 'Usage: %s <python input filename> <xml output filename>' % sys.argv[0]
    sys.exit(1)

  inputScript = sys.argv[1]
  outputFile = sys.argv[2]

  generatePythonFilterFromFiles(inputScript, outputFile)


if __name__ == '__main__':
  main()
