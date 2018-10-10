# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/dossier/achievements/ReadyForBattleAchievement.py
from abstract import ClassProgressAchievement, getCompletedPersonalMissionsCount
from dossiers2.ui.achievements import ACHIEVEMENT_BLOCK as _AB

class ReadyForBattleAchievement(ClassProgressAchievement):

    def __init__(self, name, classifier, branch, dossier, value=None):
        self.__name = name
        self.__classifier = classifier
        self.__branch = branch
        self.__isCurrentUserAchievement = dossier.isCurrentUser() if dossier is not None else False
        super(ReadyForBattleAchievement, self).__init__(self.__name, _AB.TOTAL, dossier, value)
        return

    def getNextLevelInfo(self):
        return ('questsLeft', self._lvlUpValue if self.__isCurrentUserAchievement else 0)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TOTAL, self.__name)

    def _readCurrentProgressValue(self, dossier):
        return getCompletedPersonalMissionsCount(self.__branch, {self.__classifier})


class ReadyForBattleAchievementSeason2(ReadyForBattleAchievement):
    MIN_LVL = 3
    NO_LVL = 4
