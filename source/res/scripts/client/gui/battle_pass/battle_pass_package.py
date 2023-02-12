# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_pass/battle_pass_package.py
from collections import OrderedDict
import typing
from battle_pass_common import BattlePassConsts
from gui.battle_pass.battle_pass_award import BattlePassAwardsManager
from gui.battle_pass.battle_pass_constants import MIN_LEVEL
from gui.battle_pass.battle_pass_helpers import chaptersIDsComparator
from helpers import dependency
from helpers.dependency import replace_none_kwargs
from skeletons.gui.game_control import IBattlePassController
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.battle_pass.battle_pass_constants import ChapterState
    from gui.server_events.bonuses import SimpleBonus

class BattlePassPackage(object):
    __slots__ = ('__seasonID', '__chapterID')
    _eventsCache = dependency.descriptor(IEventsCache)
    _itemsCache = dependency.descriptor(IItemsCache)
    _battlePassController = dependency.descriptor(IBattlePassController)
    __TOP_PRIORITY_REWARDS_COUNT = 7

    def __init__(self, chapterID):
        self.__seasonID = self._battlePassController.getSeasonID()
        self.__chapterID = chapterID

    def getPrice(self):
        bpCost = self._battlePassController.getBattlePassCost(self.__chapterID)
        return self.__getPriceBP(bpCost)

    def getLevelsCount(self):
        pass

    def getCurrentLevel(self):
        return self._battlePassController.getLevelInChapter(chapterID=self.__chapterID)

    def getTopPriorityAwards(self):
        maxLevel = self._battlePassController.getMaxLevelInChapter(chapterId=self.__chapterID)
        bonuses = []
        if self.hasBattlePass():
            bonuses.extend(self._battlePassController.getPackedAwardsInterval(self.__chapterID, MIN_LEVEL, maxLevel, awardType=BattlePassConsts.REWARD_PAID))
        bonuses = BattlePassAwardsManager.uniteTokenBonuses(bonuses)
        return BattlePassAwardsManager.sortBonuses(bonuses)[:self.__TOP_PRIORITY_REWARDS_COUNT]

    def getNowAwards(self):
        fromLevel = 1
        curLevel = self.getCurrentLevel()
        bonuses = []
        if self.hasBattlePass():
            bonuses.extend(self._battlePassController.getPackedAwardsInterval(self.__chapterID, fromLevel, curLevel, awardType=BattlePassConsts.REWARD_PAID))
        bonuses = BattlePassAwardsManager.uniteTokenBonuses(bonuses)
        return BattlePassAwardsManager.sortBonuses(bonuses)

    def getFutureAwards(self):
        bonuses = []
        if self.hasBattlePass():
            fromLevel = self.getCurrentLevel() + 1
            toLevel = self._getMaxLevel()
            bonuses.extend(self._battlePassController.getPackedAwardsInterval(self.__chapterID, fromLevel, toLevel, awardType=BattlePassConsts.REWARD_PAID))
        bonuses = BattlePassAwardsManager.uniteTokenBonuses(bonuses)
        return BattlePassAwardsManager.sortBonuses(bonuses)

    def getSeasonID(self):
        return self.__seasonID

    def isDynamic(self):
        return False

    def isVisible(self):
        return True

    def isLocked(self):
        return False

    def hasBattlePass(self):
        return True

    def setLevels(self, value):
        pass

    def getChapterID(self):
        return self.__chapterID

    def getChapterState(self):
        return self._battlePassController.getChapterState(chapterID=self.__chapterID)

    def isBought(self):
        return self._battlePassController.isBought(chapterID=self.__chapterID)

    def isExtra(self):
        return self._battlePassController.isExtraChapter(chapterID=self.__chapterID)

    def getExpireTime(self):
        return self._battlePassController.getChapterExpiration(self.__chapterID)

    def _getMaxLevel(self):
        return self._battlePassController.getMaxLevelInChapter(self.__chapterID)

    def __getPriceBP(self, battlePassCost):
        currency = battlePassCost.getCurrency()
        if self.hasBattlePass():
            value = battlePassCost.get(currency)
        else:
            value = 0
        return value


class PackageAnyLevels(BattlePassPackage):
    __slots__ = ('__dynamicLevelsCount',)

    def __init__(self, chapterID):
        self.__dynamicLevelsCount = 1
        super(PackageAnyLevels, self).__init__(chapterID)

    def setLevels(self, value):
        self.__dynamicLevelsCount = value

    def getLevelsCount(self):
        maxLevelCount = max(self._getMaxLevel() - self.getCurrentLevel(), 0)
        return min(maxLevelCount, self.__dynamicLevelsCount)

    def isLocked(self):
        chapterID = self.getChapterID()
        return not (self._battlePassController.isBought(chapterID=chapterID) and self._battlePassController.isChapterActive(chapterID))

    def isDynamic(self):
        return True

    def isBought(self):
        return self._getMaxLevel() <= self.getCurrentLevel()

    def isVisible(self):
        return True

    def hasBattlePass(self):
        return False

    def getPrice(self):
        levelCost = self._itemsCache.items.shop.getBattlePassLevelCost()
        return self.__getLevelsPrice(levelCost)

    def getNowAwards(self):
        curLevel = self.getCurrentLevel()
        toLevel = curLevel + self.getLevelsCount()
        bonuses = []
        if self.getLevelsCount():
            bonuses.extend(self._battlePassController.getPackedAwardsInterval(self.getChapterID(), curLevel + 1, toLevel, awardType=BattlePassConsts.REWARD_BOTH))
        bonuses = BattlePassAwardsManager.uniteTokenBonuses(bonuses)
        return BattlePassAwardsManager.sortBonuses(bonuses)

    def __getLevelsPrice(self, levelCost):
        currency = levelCost.getCurrency()
        levelsCount = self.getLevelsCount()
        return levelCost.get(currency, 0) * levelsCount


@replace_none_kwargs(battlePass=IBattlePassController)
def generatePackages(battlePass=None):
    return OrderedDict(sorted(((chapterID, BattlePassPackage(chapterID)) for chapterID in battlePass.getChapterIDs()), cmp=lambda first, second: chaptersIDsComparator(first[0], second[0])))
