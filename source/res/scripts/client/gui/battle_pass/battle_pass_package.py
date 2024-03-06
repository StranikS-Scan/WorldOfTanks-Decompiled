# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_pass/battle_pass_package.py
from collections import OrderedDict
import typing
from battle_pass_common import BattlePassConsts
from gui.battle_pass.battle_pass_award import BattlePassAwardsManager
from gui.battle_pass.battle_pass_constants import MIN_LEVEL
from gui.battle_pass.battle_pass_helpers import getCompoundPriceDefaultID
from gui.shared.money import Money
from helpers import dependency
from helpers.dependency import replace_none_kwargs
from skeletons.gui.game_control import IBattlePassController
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import Dict
    from gui.battle_pass.battle_pass_constants import ChapterState
    from gui.server_events.bonuses import SimpleBonus

class BattlePassPackage(object):
    __slots__ = ('__seasonID', '__chapterID', '__buyWithRemainingLevels')
    __eventsCache = dependency.descriptor(IEventsCache)
    __itemsCache = dependency.descriptor(IItemsCache)
    __battlePass = dependency.descriptor(IBattlePassController)
    __TOP_PRIORITY_REWARDS_COUNT = 8

    def __init__(self, chapterID):
        self.__seasonID = self.__battlePass.getSeasonID()
        self.__chapterID = chapterID
        self.__buyWithRemainingLevels = False

    def getPrice(self):
        return self.__getPriceBP(self.getCompoundPrice())

    def getCompoundPrice(self):
        compoundPrice = self.__battlePass.getBattlePassCost(self.__chapterID)
        priceDefaultID = getCompoundPriceDefaultID(compoundPrice)
        compoundPrice = Money(**compoundPrice[priceDefaultID])
        if self.__buyWithRemainingLevels:
            compoundPrice += self.__getUnreachedLevelsPrice()
        return {priceDefaultID: compoundPrice.toDict()}

    def getLevelsCount(self):
        pass

    def getCurrentLevel(self):
        return self.__battlePass.getLevelInChapter(chapterID=self.__chapterID)

    def getLevelsRange(self):
        return (MIN_LEVEL, self.getCurrentLevel()) if not self.__buyWithRemainingLevels else (self.getCurrentLevel() + 1, self._getMaxLevel())

    def getRemainingLevelsCount(self):
        return self._getMaxLevel() - self.getCurrentLevel()

    def getTopPriorityAwards(self):
        maxLevel = self.__battlePass.getMaxLevelInChapter(chapterId=self.__chapterID)
        bonuses = self.__battlePass.getPackedAwardsInterval(self.__chapterID, MIN_LEVEL, maxLevel, awardType=BattlePassConsts.REWARD_PAID)
        if self.__buyWithRemainingLevels:
            bonuses.extend(self.__battlePass.getPackedAwardsInterval(self.__chapterID, self.getCurrentLevel() + 1, maxLevel, awardType=BattlePassConsts.REWARD_FREE))
        bonuses = BattlePassAwardsManager.uniteTokenBonuses(bonuses)
        return BattlePassAwardsManager.sortBonuses(bonuses)[:self.__TOP_PRIORITY_REWARDS_COUNT]

    def getNowAwards(self):
        curLevel = self.getCurrentLevel()
        bonuses = self.__battlePass.getPackedAwardsInterval(self.__chapterID, MIN_LEVEL, curLevel, awardType=BattlePassConsts.REWARD_PAID)
        if self.__buyWithRemainingLevels:
            bonuses.extend(self.__battlePass.getPackedAwardsInterval(self.__chapterID, curLevel + 1, self._getMaxLevel(), awardType=BattlePassConsts.REWARD_BOTH))
        bonuses = BattlePassAwardsManager.uniteTokenBonuses(bonuses)
        return BattlePassAwardsManager.sortBonuses(bonuses)

    def getFutureAwards(self):
        if self.__buyWithRemainingLevels:
            return []
        bonuses = self.__battlePass.getPackedAwardsInterval(self.__chapterID, self.getCurrentLevel() + 1, self._getMaxLevel(), awardType=BattlePassConsts.REWARD_PAID)
        bonuses = BattlePassAwardsManager.uniteTokenBonuses(bonuses)
        return BattlePassAwardsManager.sortBonuses(bonuses)

    def getSeasonID(self):
        return self.__seasonID

    def changeWithLevels(self):
        self.__buyWithRemainingLevels = not self.__buyWithRemainingLevels

    def resetWithLevels(self):
        self.__buyWithRemainingLevels = False

    def isVisible(self):
        return True

    def isLocked(self):
        return False

    def hasBattlePass(self):
        return True

    def isWithLevels(self):
        return self.__buyWithRemainingLevels

    def setLevels(self, value):
        pass

    def getChapterID(self):
        return self.__chapterID

    def getChapterState(self):
        return self.__battlePass.getChapterState(chapterID=self.__chapterID)

    def isBought(self):
        return self.__battlePass.isBought(chapterID=self.__chapterID)

    def isExtra(self):
        return self.__battlePass.isExtraChapter(chapterID=self.__chapterID)

    def isCustom(self):
        return self.__battlePass.isCustomChapter(chapterID=self.__chapterID)

    def isHoliday(self):
        return self.__battlePass.isHoliday()

    def getExpireTime(self):
        return self.__battlePass.getChapterExpiration(self.__chapterID)

    def _getMaxLevel(self):
        return self.__battlePass.getMaxLevelInChapter(self.__chapterID)

    def __getPriceBP(self, battlePassCost):
        return next(next(battlePassCost.itervalues()).itervalues()) if self.hasBattlePass() else 0

    def __getUnreachedLevelsPrice(self):
        levelsCount = self._getMaxLevel() - self.getCurrentLevel()
        price = self.__itemsCache.items.shop.getBattlePassLevelCost() * levelsCount
        return price


class PackageAnyLevels(BattlePassPackage):
    __slots__ = ('__dynamicLevelsCount',)
    __itemsCache = dependency.descriptor(IItemsCache)
    __battlePass = dependency.descriptor(IBattlePassController)

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
        return not (self.__battlePass.isBought(chapterID=chapterID) and self.__battlePass.isChapterActive(chapterID))

    def isBought(self):
        return self._getMaxLevel() <= self.getCurrentLevel()

    def isVisible(self):
        return True

    def hasBattlePass(self):
        return False

    def isWithLevels(self):
        return False

    def getPrice(self):
        levelCost = self.__itemsCache.items.shop.getBattlePassLevelCost()
        return self.__getLevelsPrice(levelCost)

    def getCompoundPrice(self):
        return {}

    def getNowAwards(self):
        curLevel = self.getCurrentLevel()
        toLevel = curLevel + self.getLevelsCount()
        bonuses = []
        if self.getLevelsCount():
            bonuses.extend(self.__battlePass.getPackedAwardsInterval(self.getChapterID(), curLevel + 1, toLevel, awardType=BattlePassConsts.REWARD_BOTH))
        bonuses = BattlePassAwardsManager.uniteTokenBonuses(bonuses)
        return BattlePassAwardsManager.sortBonuses(bonuses)

    def getFutureAwards(self):
        return []

    def getLevelsRange(self):
        curLevel = self.getCurrentLevel()
        return (curLevel + 1, curLevel + self.getLevelsCount())

    def changeWithLevels(self):
        pass

    def resetWithLevels(self):
        pass

    def __getLevelsPrice(self, levelCost):
        currency = levelCost.getCurrency()
        levelsCount = self.getLevelsCount()
        return levelCost.get(currency, 0) * levelsCount


@replace_none_kwargs(battlePass=IBattlePassController)
def generatePackages(battlePass=None):
    return OrderedDict(sorted(((chapterID, BattlePassPackage(chapterID)) for chapterID in battlePass.getChapterIDs())))
