# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/ny_level_helper.py
import logging
import typing
from gui.server_events.recruit_helper import getRecruitInfo
from helpers import dependency
from items.components.ny_constants import MIN_ATMOSPHERE_LVL, MAX_ATMOSPHERE_LVL, MIN_TANK_SLOTS_LVL
from new_year.ny_constants import NY_LEVEL_PREFIX
from ny_common.GeneralConfig import GeneralConfig
from shared_utils import first
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.server_events.bonuses import SimpleBonus
    from gui.server_events.recruit_helper import _BaseRecruitInfo
_logger = logging.getLogger(__name__)

@dependency.replace_none_kwargs(lobbyCtx=ILobbyContext)
def getNYGeneralConfig(lobbyCtx=None):
    return lobbyCtx.getServerSettings().getNewYearGeneralConfig()


def parseNYLevelToken(token):
    if token.startswith(NY_LEVEL_PREFIX):
        try:
            level = int(token.split(':')[-1])
            return level
        except ValueError:
            return None

    return None


def getLevelIndexes():
    for index in xrange(MIN_ATMOSPHERE_LVL, MAX_ATMOSPHERE_LVL + 1):
        yield index


class NewYearAtmospherePresenter(object):
    __itemsCache = dependency.descriptor(IItemsCache)

    @classmethod
    def getFloatLevelProgress(cls):
        levelProgress, levelTotalPoints = cls.getLevelProgress()
        return float(levelProgress) / levelTotalPoints

    @classmethod
    def getLevelProgress(cls):
        generalConfig = getNYGeneralConfig()
        levelProgress, levelTotalPoints = generalConfig.getAtmosphereProgress(cls.__getTotalAtmospherePoints())
        return (levelProgress, levelTotalPoints)

    @classmethod
    def getLevel(cls):
        generalConfig = getNYGeneralConfig()
        return generalConfig.calculateLevelByPoints(cls.__getTotalAtmospherePoints())

    @classmethod
    def __getTotalAtmospherePoints(cls):
        return cls.__itemsCache.items.festivity.getAtmPoints()


class LevelInfo(object):
    __slots__ = ('__level', '__bonuses', '__questID', '__tankmanToken', '__tankmanInfo')
    __itemsCache = dependency.descriptor(IItemsCache)
    __eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, level, quest):
        self.__level = level
        self.__tankmanToken = None
        self.__tankmanInfo = None
        self.__bonuses = []
        self.__questID = quest.getID()
        self.__bonusProcessing(quest)
        return

    def isCurrent(self):
        return self.__level == NewYearAtmospherePresenter.getLevel()

    def isAchieved(self):
        return self.__level <= self.__itemsCache.items.festivity.getMaxLevel()

    def isMaxReachedLevel(self):
        return self.__level == self.__itemsCache.items.festivity.getMaxLevel()

    def isLastLevel(self):
        return self.__level == MAX_ATMOSPHERE_LVL

    def isQuestCompleted(self):
        levelQuest = self.__eventsCache.getCachedQuestByID(self.__questID)
        return False if levelQuest is None else levelQuest.isCompleted()

    def hasTankSlot(self):
        return self.__level >= MIN_TANK_SLOTS_LVL

    def level(self):
        return self.__level

    def hasTankman(self):
        return self.__tankmanToken is not None

    def isTankmanRecruited(self):
        tankmanToken = self.getTankmanToken()
        return tankmanToken not in self.__itemsCache.items.tokens.getTokens() if self.isAchieved() and self.isQuestCompleted() and tankmanToken is not None else False

    def getTankmanToken(self):
        return self.__tankmanToken

    def getTankmanInfo(self):
        tankmanToken = self.getTankmanToken()
        return getRecruitInfo(tankmanToken) if tankmanToken is not None else None

    def getBonuses(self):
        return self.__bonuses

    def updateBonuses(self):
        if not self.__bonuses:
            self.__bonusProcessing()

    def __bonusProcessing(self, quest=None):
        if quest is None:
            quest = self.__eventsCache.getCachedQuestByID(self.__questID)
        if quest is None:
            return
        else:
            for bonus in quest.getBonuses():
                self.__bonuses.append(bonus)
                if bonus.getName() == 'tmanToken':
                    self.__tankmanToken = first(bonus.getValue().iterkeys())

            return
