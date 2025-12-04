# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/common/new_year_common/objects_config.py
from new_year_common.settings import NyObjectsConsts

class ObjectsConfig(object):
    __slots__ = ('_config',)

    def __init__(self, config=None):
        self._config = config or {}

    def getObjectToken(self, objectName):
        return self._config.get(objectName, {}).get(NyObjectsConsts.OBJECT_TOKEN, '')

    def getLevelConfig(self, objectName, levelId):
        return self._config.get(objectName, {}).get(NyObjectsConsts.OBJECT_LEVELS, {}).get(levelId, {})

    def getLevelPrice(self, objectName, levelId):
        return self.getLevelConfig(objectName, levelId).get(NyObjectsConsts.OBJECT_LEVEL_PRICE, 0)

    def getNextLevelPrice(self, objectName, levelId):
        return self.getLevelConfig(objectName, levelId + 1).get(NyObjectsConsts.OBJECT_LEVEL_PRICE, 0)

    def getBonusForLevel(self, objectName, levelId):
        return self.getLevelConfig(objectName, levelId).get(NyObjectsConsts.OBJECT_LEVEL_BONUS, {})
