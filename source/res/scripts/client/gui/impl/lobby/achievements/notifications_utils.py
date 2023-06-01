# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/achievements/notifications_utils.py
import logging
import weakref
from abc import ABCMeta, abstractmethod
from constants import AchievementsLayoutStates
from achievements20.WTRStageChecker import WTRStageChecker
from gui.impl.lobby.achievements.profile_utils import isSummaryEnabled, isWTREnabled, getStagesOfWTR, getNormalizedValue, isEditingEnabled, isLayoutEnabled
from helpers import dependency
from skeletons.gui.game_control import IAchievements20Controller
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)

class FLAG_STATUS(object):
    UNSET = 0
    SET = 1
    VISITED = 2


def buildRules(ctrl):
    initialRules = [_NotificationNewSummaryPage(ctrl),
     _NotificationAchievementEditingEnabled(ctrl),
     _NotificationNewMedal(ctrl),
     _NotificationChangeRank(ctrl),
     _NotificationRatingEnabled(ctrl)]
    return [ rule for rule in initialRules if rule.prereq() ]


class NotificationsRuleProcessor(object):
    __slot__ = ('__rules', '__ctrl')

    def __init__(self, ctrl):
        self.__rules = []
        self.__ctrl = weakref.proxy(ctrl)

    def fini(self):
        self.stop()
        self.__ctrl = None
        return

    def start(self):
        self.__rules = buildRules(self.__ctrl)

    def stop(self):
        self.__rules = []

    def process(self):
        for rule in self.__rules:
            if rule.req():
                rule.do()


class _NotificationRule(object):
    __metaclass__ = ABCMeta
    _lobbyContext = dependency.descriptor(ILobbyContext)
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, achievementsCtrl):
        self._achievementsCtrl = achievementsCtrl

    @abstractmethod
    def prereq(self):
        pass

    @abstractmethod
    def req(self):
        pass

    @abstractmethod
    def do(self):
        pass


class _NotificationNewSummaryPage(_NotificationRule):

    def prereq(self):
        return self._achievementsCtrl.getFirstEntryStatus() == FLAG_STATUS.UNSET and isSummaryEnabled()

    def req(self):
        achievements20GeneralConfig = self._lobbyContext.getServerSettings().getAchievements20GeneralConfig()
        requiredCountOfBattles = achievements20GeneralConfig.getRequiredCountOfBattles()
        battlesLeftCountBeforeFeature = requiredCountOfBattles - self._achievementsCtrl.getInitialBattleCount()
        return self.prereq() and battlesLeftCountBeforeFeature <= 0

    def do(self):
        self._achievementsCtrl.showNewSummaryEnabled()
        self._achievementsCtrl.setFirstEntryStatus(FLAG_STATUS.SET)
        self._achievementsCtrl.setRatingCalculatedStatus(FLAG_STATUS.SET)
        cRating = getNormalizedValue(self._itemsCache.items.sessionStats.getAccountWtr())
        self._achievementsCtrl.setMaxWtrPoints(cRating)
        self._achievementsCtrl.setWtrPrevPointsNotification(cRating)


class _NotificationRatingEnabled(_NotificationRule):

    def prereq(self):
        return isWTREnabled() and isSummaryEnabled() and self._achievementsCtrl.getRatingCalculatedStatus() == FLAG_STATUS.UNSET and self._achievementsCtrl.getFirstEntryStatus() != FLAG_STATUS.SET

    def req(self):
        stats = self._itemsCache.items.getAccountDossier().getRandomStats()
        cRating = getNormalizedValue(self._itemsCache.items.sessionStats.getAccountWtr())
        achievements20GeneralConfig = self._lobbyContext.getServerSettings().getAchievements20GeneralConfig()
        requiredCountOfBattles = achievements20GeneralConfig.getRequiredCountOfBattles()
        battlesLeftCount = requiredCountOfBattles - stats.getBattlesCount()
        battlesLeftCountBeforeFeature = requiredCountOfBattles - self._achievementsCtrl.getInitialBattleCount()
        return self.prereq() and battlesLeftCount <= 0 and cRating and battlesLeftCountBeforeFeature > 0

    def do(self):
        self._achievementsCtrl.showRankedComplete()
        self._achievementsCtrl.setRatingCalculatedStatus(FLAG_STATUS.SET)
        cRating = getNormalizedValue(self._itemsCache.items.sessionStats.getAccountWtr())
        self._achievementsCtrl.setWtrPrevPointsNotification(cRating)
        self._achievementsCtrl.setMaxWtrPoints(cRating)


class _NotificationAchievementEditingEnabled(_NotificationRule):

    def prereq(self):
        return self._achievementsCtrl.getAchievementEditingEnabledStatus() == FLAG_STATUS.UNSET and self._achievementsCtrl.getFirstEntryStatus() != FLAG_STATUS.SET

    def req(self):
        return self.prereq() and isSummaryEnabled() and isEditingEnabled() and isLayoutEnabled()

    def do(self):
        self._achievementsCtrl.showEditAvailable()
        self._achievementsCtrl.setAchievementEditingEnabledStatus(FLAG_STATUS.SET)


class _NotificationNewMedal(_NotificationRule):

    def prereq(self):
        return True

    def req(self):
        items = self._itemsCache.items
        if items.getLayoutState() == AchievementsLayoutStates.MANUAL:
            return False
        prevLayoutList = self._achievementsCtrl.getPrevAchievementsList()
        achievements20GeneralConfig = self._lobbyContext.getServerSettings().getAchievements20GeneralConfig()
        layoutLength = achievements20GeneralConfig.getLayoutLength()
        mainRules = achievements20GeneralConfig.getAutoGeneratingMainRules()
        extraRules = achievements20GeneralConfig.getAutoGeneratingExtraRules()
        newLayoutList = items.getAccountDossier().getTotalStats().getSignificantAchievements(mainRules, extraRules, layoutLength)
        for achievement in newLayoutList:
            if achievement.getName() not in prevLayoutList:
                return True

        return False

    def do(self):
        self._achievementsCtrl.setMedalAddedStatus(FLAG_STATUS.SET)


class _NotificationChangeRank(_NotificationRule):

    def prereq(self):
        return isWTREnabled() and isSummaryEnabled() and self._achievementsCtrl.getFirstEntryStatus() != FLAG_STATUS.SET and self._achievementsCtrl.getRatingCalculatedStatus() != FLAG_STATUS.UNSET

    def req(self):
        checker = WTRStageChecker(getStagesOfWTR())
        cGroup = 0
        cStage = 0
        pGroup = 0
        pStage = 0
        cRating = getNormalizedValue(self._itemsCache.items.sessionStats.getAccountWtr())
        if cRating:
            cGroup, cStage, _ = checker.getStage(cRating)
        pRating = self._achievementsCtrl.getWtrPrevPointsNotification()
        if pRating:
            pGroup, pStage, _ = checker.getStage(pRating)
        hasChange = cGroup != pGroup or cStage != pStage
        stats = self._itemsCache.items.getAccountDossier().getRandomStats()
        achievements20GeneralConfig = self._lobbyContext.getServerSettings().getAchievements20GeneralConfig()
        requiredCountOfBattles = achievements20GeneralConfig.getRequiredCountOfBattles()
        battlesLeftCount = requiredCountOfBattles - stats.getBattlesCount()
        return self.prereq() and battlesLeftCount <= 0 and cRating and hasChange

    def do(self):
        checker = WTRStageChecker(getStagesOfWTR())
        cRating = getNormalizedValue(self._itemsCache.items.sessionStats.getAccountWtr())
        cGroup, cStage, _ = checker.getStage(cRating)
        mGroup = 0
        mStage = 0
        mRating = self._achievementsCtrl.getMaxWtrPoints()
        if mRating:
            mGroup, mStage, _ = checker.getStage(mRating)
        if cGroup > mGroup or cGroup == mGroup and cStage > mStage:
            self._achievementsCtrl.showRatingUpgrade()
            self._achievementsCtrl.setMaxWtrPoints(cRating)
        else:
            self._achievementsCtrl.showRatingChanged()
        self._achievementsCtrl.setRatingChangedStatus(FLAG_STATUS.SET)
        self._achievementsCtrl.setWtrPrevPointsNotification(cRating)
