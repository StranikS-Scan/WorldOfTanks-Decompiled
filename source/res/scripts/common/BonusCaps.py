# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/BonusCaps.py
from typing import Dict, Optional, Set, FrozenSet

class BonusCapsConst(object):
    CONFIG_NAME = 'bonus_caps_override_config'
    REMOVE = 'remove'
    ADD = 'add'
    OVERRIDE = 'override'


class BonusCapsConfig(object):
    __slots__ = {'__config'}
    __OPERATIONS = {BonusCapsConst.REMOVE: lambda x, y: x - y,
     BonusCapsConst.ADD: lambda x, y: x | y,
     BonusCapsConst.OVERRIDE: lambda x, y: y}

    def __init__(self, config=None):
        if not config:
            config = dict()
        self.__config = config

    def __performOperations(self, arenaBonusType, defaultBonusCaps):
        configBonusCaps = self.__config[arenaBonusType]
        resultBonusCaps = set(defaultBonusCaps)
        for operation in configBonusCaps.iterkeys():
            resultBonusCaps = self.__OPERATIONS[operation](resultBonusCaps, configBonusCaps[operation])

        return resultBonusCaps

    def getModifiedBonusCaps(self, arenaBonusType, defaultBonusCaps):
        return defaultBonusCaps if self.__config.get(arenaBonusType, None) is None else frozenset(self.__performOperations(arenaBonusType, defaultBonusCaps))
