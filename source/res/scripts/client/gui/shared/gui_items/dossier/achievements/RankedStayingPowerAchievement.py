# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/dossier/achievements/RankedStayingPowerAchievement.py
from abstract import ClassProgressAchievement
from dossiers2.custom.config import RECORD_CONFIGS
from dossiers2.ui.achievements import ACHIEVEMENT_BLOCK as _AB

class RankedStayingPowerAchievement(ClassProgressAchievement):
    __ACHIEVEMENT_NAME = 'rankedStayingPower'
    __DEFAULT_LEVEL = 0

    def __init__(self, dossier, value=None):
        ClassProgressAchievement.__init__(self, self.__ACHIEVEMENT_NAME, _AB.TOTAL, dossier, value)

    def getNextLevelInfo(self):
        return ('stepsLeft', self._lvlUpValue)

    def _readValue(self, dossier):
        return self.__getRankValue(self._readCurrentProgressValue(dossier))

    def _readCurrentProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TOTAL, self.__ACHIEVEMENT_NAME)

    @classmethod
    def checkIsInDossier(cls, block, name, dossier):
        if dossier is not None:
            currentValue = dossier.getRecordValue(_AB.TOTAL, cls.__ACHIEVEMENT_NAME)
            return cls.__getRankValue(currentValue) > cls.__DEFAULT_LEVEL
        else:
            return False

    def _readProgressValue(self, dossier):
        return self.__getRankValue(self._readCurrentProgressValue(dossier))

    @classmethod
    def __getRankValue(cls, currentValue):
        medalCfg = RECORD_CONFIGS[cls.__ACHIEVEMENT_NAME]
        values = [ cls.MIN_LVL - i for i, values in enumerate(medalCfg) if values <= currentValue ]
        return min(values) if values else cls.__DEFAULT_LEVEL
