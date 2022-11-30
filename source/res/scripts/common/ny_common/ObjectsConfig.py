# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/ny_common/ObjectsConfig.py
from ny_common.settings import ObjectsConsts
from typing import Optional, List, Dict

class ObjectsConfig(object):

    def __init__(self, config):
        self._config = config

    def getObjectByID(self, objectID):
        return ObjectDescriptor(self._config[objectID]) if objectID in self._config else None


class ObjectDescriptor(object):

    def __init__(self, levels):
        self._levels = levels

    def getLevels(self):
        return map(ObjectLevelDescriptor, self._levels)

    def getNextLevel(self, currentLevel):
        return ObjectLevelDescriptor(self._levels[currentLevel + 1]) if currentLevel + 1 < len(self._levels) else None


class ObjectLevelDescriptor(object):

    def __init__(self, config):
        self._config = config

    def getLevelID(self):
        return self._config.get(ObjectsConsts.OBJECT_LEVEL_ID, 0)

    def getLevelPrice(self):
        return self._config.get(ObjectsConsts.OBJECT_LEVEL_PRICE, {})

    def getLevelPoints(self):
        return self._config.get(ObjectsConsts.OBJECT_LEVEL_POINTS, 0)

    def getDefaultToysCountPerSlot(self):
        return self._config.get(ObjectsConsts.OBJECT_LEVEL_DEFAULT_TOYS_COUNT, 0)

    def getCustomToysCountPerSlot(self):
        return self._config.get(ObjectsConsts.OBJECT_LEVEL_CUSTOM_TOYS_COUNT, {})

    def getToyCountBySlotType(self, slotType):
        return self.getCustomToysCountPerSlot().get(slotType, self.getDefaultToysCountPerSlot())

    def getLevelToken(self):
        return self._config.get(ObjectsConsts.OBJECT_LEVEL_TOKEN, None)
