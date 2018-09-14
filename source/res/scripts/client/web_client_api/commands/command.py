# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web_client_api/commands/command.py
from types import FunctionType, MethodType
from functools import partial
from collections import namedtuple
from .. import WebCommandException

class SchemeValidator(object):
    """
    Validates whether the command valid according to the scheme.
    Rises WebCommandException if command is not valid.
    Child classes should pass scheme to __init__ during initialization.
    
    Parameters validation performs using scheme.
    
    Every parameter in scheme represents as tuple with two values:
        - parameter name
        - parameter type
        examples:
            ('some_string', basestring)
            ('some_number', (int, long))
    
    Scheme is a dictionary with next keys:
        'required' - list of required parameters
        'unions' - list of parameters one of which must exist
    
    Example of scheme:
    
    _ExampleScheme = {
        'required': (('parameter1', basestring),    # 'parameter1' should exist
                     ('parameter2', int)),          # 'parameter2' should exist
    
        'unions': (('parameter3', basestring),      # 'parameter3' or 'parameter4' should exist
                   ('parameter4', long))
    }
    """

    def __init__(self, scheme):
        self.__scheme = scheme

    def validateCurrentScheme(self):
        self.__validate(self.__scheme)

    def validateScheme(self, scheme):
        self.__validate(scheme)

    def __validate(self, availableScheme):

        def validateSection(sectionName, required):
            requiredFields = availableScheme.get(sectionName, [])
            for field in requiredFields:
                name, type = field
                value = getattr(self, name, None)
                if value is None:
                    if required:
                        raise WebCommandException("Command validation failed: '%s' parameter is missing!" % name)
                    else:
                        continue
                if not isinstance(value, type):
                    raise WebCommandException("Command validation failed: Value '%s' for parameter '%s' is wrong!" % (value, name))

            return

        validateSection('required', True)
        validateSection('optional', False)
        requiredUnionsFields = availableScheme.get('unions', [])
        if len(requiredUnionsFields) > 0:
            unionFound = False
            for field in requiredUnionsFields:
                name, type = field
                value = getattr(self, name)
                if value is not None and isinstance(value, type):
                    unionFound = True

            if not unionFound:
                raise WebCommandException('Command validation failed: Not found suitable parameters!')
        return


def instantiateObject(objClass, data):
    """
    Creates and validates instance of object class using dictionary
    :param cmdClass: - class of object to create
    :param data: - data dictionary for initialization
    :return: - instance of objClass
    """
    customParameters = set(data) - set(objClass._fields)
    parameters = {}
    if 'custom_parameters' in objClass._fields:
        parameters['custom_parameters'] = {}
        for name in customParameters:
            parameters['custom_parameters'][name] = data[name]

    for key, value in data.iteritems():
        if key not in customParameters:
            parameters[key] = value

    cmdInstance = objClass(**parameters)
    cmdInstance.validateCurrentScheme()
    return cmdInstance


_WebCommand = namedtuple('_WebCommand', 'command, params')
_WebCommand.__new__.__defaults__ = (None, None)
_WebCommandScheme = {'required': (('command', basestring), ('params', dict))}

class WebCommand(_WebCommand, SchemeValidator):
    """
    Common class for web commands representation.
    """

    def __init__(self, *args, **kwargs):
        super(WebCommand, self).__init__(_WebCommandScheme)


_CommandHandler = namedtuple('_CommandHandler', 'name, cls, handler')
_CommandHandler.__new__.__defaults__ = (None, None, None)
_CommandHandlerScheme = {'required': (('name', basestring), ('cls', type), ('handler', (MethodType, FunctionType, partial)))}

class CommandHandler(_CommandHandler, SchemeValidator):
    """
    Command handler class
    """

    def __init__(self, *args, **kwargs):
        super(CommandHandler, self).__init__(_CommandHandlerScheme)
