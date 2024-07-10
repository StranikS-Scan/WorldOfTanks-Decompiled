# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_modifiers/scripts/common/battle_modifiers_ext/remappings_cache.py
from typing import Any, Dict, TYPE_CHECKING, Optional
from battle_modifiers_ext.constants_ext import REMAPPING_XML_PATH, RemappingNames
from remapping.remapping_readers import ERR_TEMPLATE, readComposers, readConditions
from extension_utils import ResMgr
from ResMgr import DataSection
from soft_exception import SoftException
_ERR_TEMPLATE = "[Remapping] {} for remapping '{}'"
if TYPE_CHECKING:
    from battle_modifiers_common import ModifiersContext
    from battle_modifiers_ext.remapping.remapping_composers import IComposer
g_cache = None

class RemappingCache(object):
    __slots__ = ('__remapping',)

    def __init__(self):
        self.__readConfig()

    def __repr__(self):
        return 'RemappingCache({})'.format(self.__remapping)

    def getValue(self, modifierName, remappingName, oldValue, ctx):
        composer = self.__remapping.get(remappingName, {}).get(modifierName)
        return composer.getValue(ctx, oldValue) if composer is not None else None

    def getValues(self, modifierName, remappingName, oldValue):
        composer = self.__remapping.get(remappingName, {}).get(modifierName)
        return composer.getValues(oldValue) if composer is not None else None

    def reloadCache(self, configPath=''):
        self.__readConfig(configPath)

    def __readConfig(self, configPath=''):
        configPath = configPath or REMAPPING_XML_PATH
        config = ResMgr.openSection(configPath)
        if config is None:
            raise SoftException("[Remapping] Cannot open or read '{}'".format(configPath))
        self.__remapping = {}
        for remappingName, remappingSection in config.items():
            if remappingName == 'xmlns:xmlref':
                continue
            if remappingName not in RemappingNames.ALL:
                raise SoftException("[Remapping] Invalid remapping name '{}'".format(remappingName))
            self.__remapping[remappingName] = self.__readRemappingSection(remappingSection)

        return

    def __readRemappingSection(self, config):
        remappingName = config.name
        if not config.has_key('conditions'):
            raise SoftException(ERR_TEMPLATE.format('Missing conditions', remappingName))
        conditions = readConditions(config['conditions'], remappingName)
        if not config.has_key('composers'):
            raise SoftException(ERR_TEMPLATE.format('Missing composers', remappingName))
        return readComposers(config['composers'], remappingName, conditions)


def init():
    global g_cache
    g_cache = RemappingCache()
