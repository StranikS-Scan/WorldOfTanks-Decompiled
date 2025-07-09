# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/doc_loaders/vehicle_gui_parameters_reader.py
import logging
import typing
import ResMgr
from fun_random.gui.doc_loaders import VehicleParameters, VehicleParametersConfig
from soft_exception import SoftException
_logger = logging.getLogger(__name__)
_CONFIG_PATH = 'fun_random/gui/configs/vehicle_gui_parameters.xml'
_VEHICLE_GUI_PARAMETERS = None

def getVehicleParametersConfig():
    global _VEHICLE_GUI_PARAMETERS
    if _VEHICLE_GUI_PARAMETERS is None:
        _VEHICLE_GUI_PARAMETERS = _readConfig(_CONFIG_PATH)
    return _VEHICLE_GUI_PARAMETERS


def _readConfig(configPath):
    config = ResMgr.openSection(configPath)
    if config is None:
        raise SoftException('Cannot open or read config {}'.format(configPath))
    if not config.has_key('vehicleParameters'):
        raise SoftException('Missing vehicleParameters section in config {}'.format(configPath))
    config = config['vehicleParameters']
    parameters = _readAvailableParameters(config)
    vehicles = _readVehicles(config, parameters)
    return VehicleParametersConfig(parameters, vehicles)


def _readAvailableParameters(config):
    if not config.has_key('parameters'):
        raise SoftException('Missing parameters section in config')
    parameters = {}
    section = config['parameters']
    for name, section in section.items():
        if name != 'parameter':
            raise SoftException('Missing parameter section')
        if not section.has_key('name'):
            raise SoftException('Missing parameter name')
        parameterName = section['name'].asString
        if not section.has_key('icon'):
            raise SoftException('Missing icon name for parameter {}'.format(parameterName))
        icon = section['icon'].asString
        parameters[parameterName] = icon

    return parameters


def _readVehicles(config, parameters):
    if not config.has_key('vehicles'):
        raise SoftException('Missing vehicles section in config')
    section = config['vehicles']
    result = {}
    for subSection in section.values():
        vehicle = subSection['name'].asString
        description = subSection['description'].asString
        result[vehicle] = VehicleParameters(strengths=_readVehicleParameters(subSection['strengths'], parameters), weaknesses=_readVehicleParameters(subSection['weaknesses'], parameters), description=description)

    return result


def _readVehicleParameters(section, allParameters):
    parameters = section.asString.split(' ')
    for parameter in parameters:
        if parameter not in allParameters:
            raise SoftException('Incorrect vehicle property {} in the config'.format(parameter))

    return parameters
