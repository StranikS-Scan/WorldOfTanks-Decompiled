# Embedded file name: scripts/client/gui/shared/gui_items/dossier/achievements/abstract/ClassProgressAchievement.py
import BigWorld
from SimpleProgressAchievement import SimpleProgressAchievement
from helpers import i18n
from dossiers2.custom.config import RECORD_CONFIGS

class ClassProgressAchievement(SimpleProgressAchievement):
    MIN_LVL = 4
    NO_LVL = 5

    def __init__(self, name, block, dossier, value = None):
        if dossier is not None:
            self._currentProgressValue = self._readCurrentProgressValue(dossier)
        else:
            self._currentProgressValue = 0
        super(ClassProgressAchievement, self).__init__(name, block, dossier, value)
        return

    def getUserName(self):
        i18nRank = i18n.makeString('#achievements:achievement/rank%d' % (self._value or self.MIN_LVL))
        return super(ClassProgressAchievement, self).getUserName() % {'rank': i18nRank}

    def getValue(self):
        return self._value or self.NO_LVL

    def getI18nValue(self):
        return BigWorld.wg_getIntegralFormat(self._value)

    def getProgressValue(self):
        if self._progressValue == 1:
            return 1.0
        elif self._lvlUpTotalValue == 0:
            return 1.0
        else:
            return 1 - float(self._lvlUpValue) / float(self._lvlUpTotalValue)

    def isInNear(self):
        return self.getProgressValue() >= 0.95 or self._lvlUpValue == 1

    def getNotificationInfo(self):
        notificationKey = '#achievements:%s_notification%d' % (self._getActualName(), self._value)
        if i18n.doesTextExist(notificationKey):
            return i18n.makeString(notificationKey)
        return ''

    def _readLevelUpTotalValue(self, dossier):
        if self._name not in RECORD_CONFIGS:
            return 0
        progressValue = self._progressValue or self.NO_LVL
        medalCfg = RECORD_CONFIGS[self._name]
        maxMedalClass = len(medalCfg)
        nextMedalClass = progressValue - 1
        nextMedalClassIndex = maxMedalClass - nextMedalClass
        if nextMedalClass <= 0:
            return 0.0
        elif nextMedalClass <= maxMedalClass:
            return medalCfg[nextMedalClassIndex]
        else:
            return 1.0

    def _readLevelUpValue(self, dossier):
        if self._progressValue == 1:
            return 0.0
        else:
            return max(float(self._lvlUpTotalValue) - float(self._currentProgressValue), 0.0)

    def _readCurrentProgressValue(self, dossier):
        return 0

    def _getIconName(self):
        return '%s%d' % (self._name, self._value or self.MIN_LVL)
