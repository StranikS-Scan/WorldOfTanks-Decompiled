# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/ny_level_helper.py
import logging
import typing
from gui.server_events.bonuses import SimpleBonus
from gui.server_events.recruit_helper import getRecruitInfo
from helpers import dependency
from items import new_year
from items.components.ny_constants import TOKEN_FREE_TALISMANS
from new_year.talismans import TalismanItem
from ny_common.GeneralConfig import GeneralConfig
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import INewYearController
_logger = logging.getLogger(__name__)

@dependency.replace_none_kwargs(lobbyCtx=ILobbyContext)
def getNYGeneralConfig(lobbyCtx=None):
    return lobbyCtx.getServerSettings().getNewYearGeneralConfig()


def getLevelIndexes():
    for index in xrange(new_year.CONSTS.MIN_ATMOSPHERE_LVL, new_year.CONSTS.MAX_ATMOSPHERE_LVL + 1):
        yield index


@dependency.replace_none_kwargs(itemsCache=IItemsCache, nyController=INewYearController)
def getTalismanIDByLevel(level, itemsCache=None, nyController=None):
    talismansData = itemsCache.items.festivity.getTalismans()
    talismanLevels = []
    for lvl in getLevelIndexes():
        levelInfo = nyController.getLevel(lvl)
        if levelInfo.hasTalisman():
            talismanLevels.append(lvl)

    if level in talismanLevels:
        ind = talismanLevels.index(level)
        if len(talismansData) > ind:
            return talismansData[ind]
    return None


class NewYearAtmospherePresenter(object):

    @staticmethod
    def getFloatLevelProgress():
        levelProgress, levelTotalPoints = NewYearAtmospherePresenter.getLevelProgress()
        return float(levelProgress) / levelTotalPoints

    @staticmethod
    def getLevelProgress():
        generalConfig = getNYGeneralConfig()
        levelProgress, levelTotalPoints = generalConfig.getAtmosphereProgress(NewYearAtmospherePresenter.getAmount())
        return (levelProgress, levelTotalPoints)

    @staticmethod
    def getLevel():
        generalConfig = getNYGeneralConfig()
        return generalConfig.calculateLevelByPoints(NewYearAtmospherePresenter.getAmount())

    @staticmethod
    @dependency.replace_none_kwargs(itemsCache=IItemsCache)
    def getAmount(itemsCache=None):
        slots = itemsCache.items.festivity.getSlots()
        generalConfig = getNYGeneralConfig()
        return generalConfig.calculateTotalAtmospherePoints(slots)


class LevelInfo(object):
    __slots__ = ('__level', '__bonuses', '__hasTalisman', '__questID', '__talismanInfo')
    _itemsCache = dependency.descriptor(IItemsCache)
    _eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, level, quest):
        self.__level = level
        self.__hasTalisman = False
        self.__talismanInfo = None
        self.__bonuses = []
        self.__questID = quest.getID()
        self.__bonusProccesing(quest)
        return

    def isCurrent(self):
        return self.__level == NewYearAtmospherePresenter.getLevel()

    def isAchieved(self):
        return self.__level <= self._itemsCache.items.festivity.getMaxLevel()

    def isMaxReachedLevel(self):
        return self.__level == self._itemsCache.items.festivity.getMaxLevel()

    def isLastLevel(self):
        return self.__level == new_year.CONSTS.MAX_ATMOSPHERE_LVL

    def isQuestCompleted(self):
        levelQuest = self._eventsCache.getQuestByID(self.__questID)
        return False if levelQuest is None else levelQuest.isCompleted()

    def hasTankSlot(self):
        return self.__level >= new_year.CONSTS.MIN_TANK_SLOTS_LVL

    def level(self):
        return self.__level

    def hasTalisman(self):
        return self.__hasTalisman

    def getTalismanInfo(self):
        if self.__hasTalisman and self.__talismanInfo is None and self.isQuestCompleted():
            talismanID = getTalismanIDByLevel(self.__level)
            if talismanID is not None:
                self.__talismanInfo = TalismanItem(talismanID)
        return self.__talismanInfo

    def tankmanIsRecruited(self):
        talismanInfo = self.getTalismanInfo()
        return talismanInfo.getTankmanToken() not in self._itemsCache.items.tokens.getTokens() if self.isAchieved() and self.isQuestCompleted() and talismanInfo is not None else False

    def getTankmanToken(self):
        talismanInfo = self.getTalismanInfo()
        return talismanInfo.getTankmanToken() if talismanInfo is not None else None

    def getTankmanInfo(self):
        talismanInfo = self.getTalismanInfo()
        return getRecruitInfo(talismanInfo.getTankmanToken()) if talismanInfo is not None else None

    def getBonuses(self):
        return self.__bonuses

    def updateBonuses(self):
        if not self.__bonuses:
            self.__bonusProccesing()

    def __bonusProccesing(self, quest=None):
        if quest is None:
            quest = self._eventsCache.getQuestByID(self.__questID)
        if quest is None:
            return
        else:
            for bonus in quest.getBonuses():
                if bonus.getName() == 'tokens' and TOKEN_FREE_TALISMANS in bonus.getTokens():
                    self.__hasTalisman = True
                self.__bonuses.append(bonus)

            return
