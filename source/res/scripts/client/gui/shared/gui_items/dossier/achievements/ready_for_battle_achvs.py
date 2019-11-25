# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/dossier/achievements/ready_for_battle_achvs.py
from abstract import ClassProgressAchievement, getCompletedPersonalMissionsCount
from dossiers2.ui.achievements import ACHIEVEMENT_BLOCK as _AB
from nations import Alliances
from personal_missions import PM_BRANCH

class ReadyForBattleAchievement(ClassProgressAchievement):
    __slots__ = ('__name', '__classifier', '__branch', '__isCurrentUserAchievement')

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
    __slots__ = ()
    MIN_LVL = 3
    NO_LVL = 4


class ReadyForBattleALLAchievement(ReadyForBattleAchievement):
    __slots__ = ()

    def __init__(self, dossier, value=None):
        super(ReadyForBattleALLAchievement, self).__init__(name='readyForBattleALL', classifier='battleHeroes', branch=0, dossier=dossier, value=value)

    def _readCurrentProgressValue(self, dossier):
        pass


class ReadyForBattleAllianceFranceAchievement(ReadyForBattleAchievementSeason2):
    __slots__ = ()

    def __init__(self, dossier, value=None):
        super(ReadyForBattleAllianceFranceAchievement, self).__init__(name='readyForBattleAllianceFrance', classifier=Alliances.FRANCE, branch=PM_BRANCH.PERSONAL_MISSION_2, dossier=dossier, value=value)


class ReadyForBattleAllianceGermanyAchievement(ReadyForBattleAchievementSeason2):
    __slots__ = ()

    def __init__(self, dossier, value=None):
        super(ReadyForBattleAllianceGermanyAchievement, self).__init__(name='readyForBattleAllianceGermany', classifier=Alliances.GERMANY, branch=PM_BRANCH.PERSONAL_MISSION_2, dossier=dossier, value=value)


class ReadyForBattleAllianceUSAAchievement(ReadyForBattleAchievementSeason2):
    __slots__ = ()

    def __init__(self, dossier, value=None):
        super(ReadyForBattleAllianceUSAAchievement, self).__init__(name='readyForBattleAllianceUSA', classifier=Alliances.USA, branch=PM_BRANCH.PERSONAL_MISSION_2, dossier=dossier, value=value)


class ReadyForBattleAllianceUSSRAchievement(ReadyForBattleAchievementSeason2):
    __slots__ = ()

    def __init__(self, dossier, value=None):
        super(ReadyForBattleAllianceUSSRAchievement, self).__init__(name='readyForBattleAllianceUSSR', classifier=Alliances.USSR, branch=PM_BRANCH.PERSONAL_MISSION_2, dossier=dossier, value=value)


class ReadyForBattleATSPGAchievement(ReadyForBattleAchievement):
    __slots__ = ()

    def __init__(self, dossier, value=None):
        super(ReadyForBattleATSPGAchievement, self).__init__(name='readyForBattleATSPG', classifier='AT-SPG', branch=PM_BRANCH.REGULAR, dossier=dossier, value=value)


class ReadyForBattleHTAchievement(ReadyForBattleAchievement):
    __slots__ = ()

    def __init__(self, dossier, value=None):
        super(ReadyForBattleHTAchievement, self).__init__(name='readyForBattleHT', classifier='heavyTank', branch=PM_BRANCH.REGULAR, dossier=dossier, value=value)


class ReadyForBattleLTAchievement(ReadyForBattleAchievement):
    __slots__ = ()

    def __init__(self, dossier, value=None):
        super(ReadyForBattleLTAchievement, self).__init__(name='readyForBattleLT', classifier='lightTank', branch=PM_BRANCH.REGULAR, dossier=dossier, value=value)


class ReadyForBattleMTAchievement(ReadyForBattleAchievement):
    __slots__ = ()

    def __init__(self, dossier, value=None):
        super(ReadyForBattleMTAchievement, self).__init__(name='readyForBattleMT', classifier='mediumTank', branch=PM_BRANCH.REGULAR, dossier=dossier, value=value)


class ReadyForBattleSPGAchievement(ReadyForBattleAchievement):
    __slots__ = ()

    def __init__(self, dossier, value=None):
        super(ReadyForBattleSPGAchievement, self).__init__(name='readyForBattleSPG', classifier='SPG', branch=PM_BRANCH.REGULAR, dossier=dossier, value=value)
