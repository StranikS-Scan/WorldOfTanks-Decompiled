# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/dossier/achievements/abstract/class_progress.py
from simple_progress import SimpleProgressAchievement
from gui.impl import backport
from helpers import i18n
from dossiers2.custom.config import RECORD_CONFIGS

class ClassProgressAchievement(SimpleProgressAchievement):
    __slots__ = ('_currentProgressValue',)
    MIN_LVL = 4
    NO_LVL = 5

    def __init__(self, name, block, dossier, value=None):
        if dossier is not None:
            self._currentProgressValue = self._readCurrentProgressValue(dossier)
        else:
            self._currentProgressValue = 0
        super(ClassProgressAchievement, self).__init__(name, block, dossier, value)
        return

    def getUserName(self):
        return super(ClassProgressAchievement, self).getUserName() % self._getUserNameCtx()

    def getValue(self):
        return self._value or self.NO_LVL

    def getI18nValue(self):
        return backport.getIntegralFormat(self._value)

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
        return i18n.makeString(notificationKey) if i18n.doesTextExist(notificationKey) else ''

    def getIconName(self):
        return '%s%d' % (self._name, self._value or self.MIN_LVL)

    def _getUserNameCtx(self):
        return {'rank': i18n.makeString('#achievements:achievement/rank%d' % (self._value or self.MIN_LVL))}

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
        pass
