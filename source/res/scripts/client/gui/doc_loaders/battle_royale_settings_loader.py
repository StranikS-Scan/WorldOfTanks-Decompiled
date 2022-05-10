# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/doc_loaders/battle_royale_settings_loader.py
import logging
from collections import namedtuple
import typing
from ResMgr import DataSection
import resource_helper
from battle_royale.gui.constants import ParamTypes
from gui.impl import backport
from gui.impl.gen import R
from soft_exception import SoftException
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.vehicle_modules import VehicleModule
_BATTLE_ROYALE_CONFIG_XML_PATH = 'gui/battle_royale_settings.xml'
_BATTLE_ROYALE_SETTINGS = None
_logger = logging.getLogger(__name__)
ModuleData = namedtuple('ModuleData', ('titleText', 'icon', 'deltaParams', 'priorityParams', 'params', 'constParams'))
VehicleProperties = namedtuple('VehicleParameters', ('strengths', 'weaknesses'))
_PriorityParameter = namedtuple('PriorityParameter', ('name', 'type'))
_BRSettings = namedtuple('_BRSettings', ('radar', 'spawn', 'techTree', 'vehicleProperties', 'upgradeAttentionTime', 'sounds'))
_SpawnSettings = namedtuple('_SpawnSettings', ('selectEndingSoonTime',))
_SoundsSettings = namedtuple('_SoundsSettings', ('finalEnemiesCount', 'middleAverageLevel'))
_TechTreeSettings = namedtuple('_TechTreeSettings', ('modules', 'vehicleParams'))
_MarkerLifetimeSettings = namedtuple('_MarkerLifetimeSettings', ('fadeIn', 'fadeOut', 'lifeTime'))
_RadarSettings = namedtuple('_RadarSettings', ('marker',))
_AirdropSettings = namedtuple('_AirdropSettings', ('marker',))

def _getModuleText(txtPath):
    treeTxt = R.strings.battle_royale.techtree.dyn(txtPath, None)
    if treeTxt is None:
        _logger.warning('Could not find text for %s', txtPath)
        return ''
    else:
        return backport.text(treeTxt())


def _readBattleRoyaleSettings():
    _, section = resource_helper.getRoot(_BATTLE_ROYALE_CONFIG_XML_PATH)
    result = _BRSettings(_readRadarSettings(section['radar']), _readSpawnSettings(section['spawn']), _readTechTreeSettings(section['techTree']), _readVehicleProperties(section['vehicleProperties']), section['upgradeAttentionTime'].asFloat, _readSoundSettings(section['sounds']))
    resource_helper.purgeResource(_BATTLE_ROYALE_CONFIG_XML_PATH)
    return result


def _readRadarSettings(section):
    return _RadarSettings(_readMarkerSettings(section))


def _readMarkerSettings(section):
    airdropSection = section['marker']
    return _MarkerLifetimeSettings(airdropSection['fadeIn'].asFloat, airdropSection['fadeOut'].asFloat, airdropSection['lifeTime'].asFloat)


def _readSpawnSettings(section):
    return _SpawnSettings(section['selectEndingSoonTime'].asFloat)


def _readSoundSettings(section):
    phases = section['battlePhases']
    return _SoundsSettings(phases['final']['enemiesCount'].asFloat, phases['middle']['averageLevel'].asFloat)


def _readVehicleProperties(section):
    allProperties = frozenset([ subsection.asString for subsection in section['properties'].values() ])
    vehicleProperties = {}
    for nation, properties in section['vehicles'].items():
        vehicleProperties[nation] = VehicleProperties(strengths=_parseProperties(properties['strengths'], allProperties), weaknesses=_parseProperties(properties['weaknesses'], allProperties))

    return vehicleProperties


def _parseProperties(section, allProperties):
    properties = section.asString.split(' ')
    for vehProperty in properties:
        if vehProperty not in allProperties:
            raise SoftException('There is incorrect vehicle property "%s" in the battle royale settings' % vehProperty)

    return properties


def _readModuleParams(section, priorityParams, paramTypes):
    params = []
    for innerBlock in section.values():
        paramName = innerBlock.asString
        params.append(paramName)
        for attributeValue in innerBlock.values():
            if attributeValue.asString == '1':
                priorityParams.append(_PriorityParameter(paramName, paramTypes))

    return params


def _readConstModuleParams(section, priorityParams):
    params = {}
    for innerBlock in section.values():
        isPriority = False
        innerTag = ''
        for innerTag, value in innerBlock.items():
            param = value.asString
            if innerTag != 'priority':
                params[innerTag] = param
            if param == '1':
                isPriority = True

        if isPriority:
            priorityParams.append(_PriorityParameter(innerTag, ParamTypes.CONST))

    return params


def _readTechTreeSettings(section):
    result = {}
    for _, modules in section['modules'].items():
        for m in modules.values():
            mId = m['id'].asString
            mTitleText = m['titleText'].asString
            mIcon = m['icon'].asString
            priorityParams = []
            deltaParameters = _readModuleParams(m['deltaParameters'], priorityParams, ParamTypes.DELTA) if m['deltaParameters'] is not None else tuple()
            params = tuple(_readModuleParams(m['parameters'], priorityParams, ParamTypes.SIMPLE)) if m['parameters'] is not None else tuple()
            constParams = _readConstModuleParams(m['constantParams'], priorityParams) if m['constantParams'] is not None else {}
            result[mId] = ModuleData(titleText=_getModuleText(mTitleText), icon=mIcon, deltaParams=deltaParameters, priorityParams=priorityParams, params=params, constParams=constParams)

    return _TechTreeSettings(result, [ subsection.asString for subsection in section['vehicleParams'].values() ])


def getTreeModuleSettings(vModule):
    descriptorId = vModule.name
    data = getBattleRoyaleSettings().techTree.modules.get(descriptorId)
    if not data:
        _logger.warning('Data for module "%s" has not been found', descriptorId)
        return None
    else:
        return data


def getTreeVehicleParams():
    data = getBattleRoyaleSettings().techTree.vehicleParams
    return None if not data else data


def getTreeModuleHeader(vModule):
    mData = getTreeModuleSettings(vModule)
    return mData.titleText if mData is not None else ''


def getTreeModuleIcon(vModule):
    data = getTreeModuleSettings(vModule)
    return data.icon if data is not None else ''


def getVehicleProperties(nationName):
    data = getBattleRoyaleSettings().vehicleProperties.get(nationName)
    if data is None:
        _logger.error('There is not vehicle properties for the nation=%s', nationName)
        return VehicleProperties(strengths=(), weaknesses=())
    else:
        return data


def getBattleRoyaleSettings():
    global _BATTLE_ROYALE_SETTINGS
    if _BATTLE_ROYALE_SETTINGS is None:
        _BATTLE_ROYALE_SETTINGS = _readBattleRoyaleSettings()
    return _BATTLE_ROYALE_SETTINGS


def reloadBattleRoyaleSettings():
    global _BATTLE_ROYALE_SETTINGS
    if _BATTLE_ROYALE_SETTINGS:
        _BATTLE_ROYALE_SETTINGS = _readBattleRoyaleSettings()
