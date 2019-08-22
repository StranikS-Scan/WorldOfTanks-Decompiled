# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/doc_loaders/battle_royale_settings_loader.py
import logging
from collections import namedtuple
from typing import Dict
from ResMgr import DataSection
import nations
import resource_helper
from gui.battle_royale.constants import ParamTypes
from gui.impl import backport
from gui.impl.gen import R
_BATTLE_ROYALE_CONFIG_XML_PATH = 'gui/battle_royale_settings.xml'
_BATTLE_ROYALE_SETTINGS = None
_logger = logging.getLogger(__name__)
ModuleData = namedtuple('ModuleData', ('titleText', 'icon', 'deltaParams', 'priorityParams', 'params', 'constParams'))
_PriorityParameter = namedtuple('PriorityParameter', ('name', 'type'))

def _getModuleText(txtPath):
    treeTxt = R.strings.battle_royale.techtree.dyn(txtPath, None)
    if treeTxt is None:
        _logger.warning('Could not find text for %s', txtPath)
        return ''
    else:
        return backport.text(treeTxt())


def _readBattleRoyaleSettings():
    settings = {'radar': {},
     'airdrop': {},
     'spawn': {},
     'techTree': {}}
    _, section = resource_helper.getRoot(_BATTLE_ROYALE_CONFIG_XML_PATH)
    _readRadarSettings(section['radar'], settings['radar'])
    _readAirdropSettings(section['airdrop'], settings['airdrop'])
    _readSpawnSettings(section['spawn'], settings['spawn'])
    _readTechTreeSettings(section['techTree'], settings['techTree'])
    settings['upgradeAttentionTime'] = section['upgradeAttentionTime'].asFloat
    resource_helper.purgeResource(_BATTLE_ROYALE_CONFIG_XML_PATH)
    return settings


def _readRadarSettings(section, settings):
    settings.update({'marker': {name:subsection.asFloat for name, subsection in section['marker'].items()}})


def _readAirdropSettings(section, settings):
    settings.update({'marker': {name:subsection.asFloat for name, subsection in section['marker'].items()}})


def _readSpawnSettings(section, settings):
    settings.update({'selectEndingSoonTime': section['selectEndingSoonTime'].asFloat})


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


def _readTechTreeSettings(section, settings):
    result = {}
    for nation, modules in section['modules'].items():
        nationID = nations.INDICES[nation]
        for m in modules.values():
            mId = m['id'].asInt
            mTitleText = m['titleText'].asString
            mIcon = m['icon'].asString
            priorityParams = []
            deltaParameters = _readModuleParams(m['deltaParameters'], priorityParams, ParamTypes.DELTA) if m['deltaParameters'] is not None else tuple()
            params = tuple(_readModuleParams(m['parameters'], priorityParams, ParamTypes.SIMPLE)) if m['parameters'] is not None else tuple()
            constParams = _readConstModuleParams(m['constantParams'], priorityParams) if m['constantParams'] is not None else {}
            result[nationID, mId] = ModuleData(titleText=_getModuleText(mTitleText), icon=mIcon, deltaParams=deltaParameters, priorityParams=priorityParams, params=params, constParams=constParams)

    settings['modules'] = result
    settings['vehicleParams'] = [ subsection.asString for subsection in section['vehicleParams'].values() ]
    return


def getTreeModuleSettings(descriptorId):
    data = getBattleRoyaleSettings()['techTree']['modules'].get(descriptorId)
    if not data:
        _logger.warning('Data for module (nationID=%s, innationID=%s) has not been found', descriptorId[0], descriptorId[1])
        return None
    else:
        return data


def getTreeVehicleParams():
    data = getBattleRoyaleSettings()['techTree']['vehicleParams']
    return None if not data else data


def getTreeModuleHeader(mID):
    mData = getTreeModuleSettings(mID)
    return mData.titleText if mData is not None else ''


def getTreeModuleIcon(descriptorID):
    data = getTreeModuleSettings(descriptorID)
    return data.icon if data is not None else ''


def getBattleRoyaleSettings():
    global _BATTLE_ROYALE_SETTINGS
    if _BATTLE_ROYALE_SETTINGS is None:
        _BATTLE_ROYALE_SETTINGS = _readBattleRoyaleSettings()
    return _BATTLE_ROYALE_SETTINGS


def reloadBattleRoyaleSettings():
    global _BATTLE_ROYALE_SETTINGS
    if _BATTLE_ROYALE_SETTINGS:
        _BATTLE_ROYALE_SETTINGS = _readBattleRoyaleSettings()
