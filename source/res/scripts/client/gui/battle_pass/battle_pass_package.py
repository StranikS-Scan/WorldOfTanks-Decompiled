# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_pass/battle_pass_package.py
from battle_pass_common import BattlePassConsts
from gui.battle_pass.battle_pass_award import BattlePassAwardsManager
from helpers import dependency
from helpers.dependency import replace_none_kwargs
from skeletons.gui.game_control import IBattlePassController
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache

class BattlePassPackage(object):
    __slots__ = ('__seasonID', '__chapter')
    _eventsCache = dependency.descriptor(IEventsCache)
    _itemsCache = dependency.descriptor(IItemsCache)
    _battlePassController = dependency.descriptor(IBattlePassController)

    def __init__(self, chapter=None):
        self.__seasonID = self._battlePassController.getSeasonID()
        self.__chapter = chapter

    def getPrice(self):
        bpCost = self._itemsCache.items.shop.getBattlePassCost()
        return self.__getPriceBP(bpCost)

    def getLevelsCount(self):
        pass

    def getNowAwards(self):
        fromLevel, maxLevelInChapter = self._battlePassController.getChapterLevelInterval(self.__chapter)
        curLevel = min(maxLevelInChapter, self._getBPCurrentLevel())
        bonuses = []
        if self.hasBattlePass():
            bonuses.extend(self._battlePassController.getPackedAwardsInterval(fromLevel, curLevel, awardType=BattlePassConsts.REWARD_PAID))
        bonuses = BattlePassAwardsManager.uniteTokenBonuses(bonuses)
        return BattlePassAwardsManager.sortBonuses(bonuses)

    def getFutureAwards(self):
        bonuses = []
        if self.hasBattlePass():
            fromLevel = self._getBPCurrentLevel() + self.getLevelsCount()
            bonuses.extend(self._battlePassController.getPackedAwardsInterval(fromLevel + 1, self._battlePassController.getChapterLevelInterval(self.__chapter)[1], awardType=BattlePassConsts.REWARD_PAID))
        bonuses = BattlePassAwardsManager.uniteTokenBonuses(bonuses)
        return BattlePassAwardsManager.sortBonuses(bonuses)

    def getSeasonID(self):
        return self.__seasonID

    def isDynamic(self):
        return False

    def isVisible(self):
        return True

    def isLocked(self):
        return self.getChapter() > self._battlePassController.getCurrentChapter()

    def hasBattlePass(self):
        return True

    def setLevels(self, value):
        pass

    def getChapter(self):
        return self.__chapter

    def isBought(self):
        return self._battlePassController.isBought(chapter=self.__chapter)

    def _getBPCurrentLevel(self):
        return self._battlePassController.getCurrentLevel()

    def __getPriceBP(self, battlePassCost):
        currency = battlePassCost.getCurrency()
        if self.hasBattlePass():
            value = battlePassCost.get(currency)
        else:
            value = 0
        return value


class PackageAnyLevels(BattlePassPackage):
    __slots__ = ('__dynamicLevelsCount',)

    def __init__(self):
        self.__dynamicLevelsCount = 1
        super(PackageAnyLevels, self).__init__()

    def setLevels(self, value):
        self.__dynamicLevelsCount = value

    def getLevelsCount(self):
        maxLevelCount = max(self._battlePassController.getMaxLevel() - self._battlePassController.getCurrentLevel(), 0)
        return min(maxLevelCount, self.__dynamicLevelsCount)

    def isLocked(self):
        return not self._battlePassController.isBought()

    def isDynamic(self):
        return True

    def isBought(self):
        return self._battlePassController.getMaxLevel() < self._battlePassController.getCurrentLevel()

    def isVisible(self):
        return True

    def hasBattlePass(self):
        return False

    def getPrice(self):
        levelCost = self._itemsCache.items.shop.getBattlePassLevelCost()
        return self.__getLevelsPrice(levelCost)

    def getNowAwards(self):
        curLevel = self._getBPCurrentLevel()
        toLevel = curLevel + self.getLevelsCount()
        bonuses = []
        if self.getLevelsCount():
            bonuses.extend(self._battlePassController.getPackedAwardsInterval(curLevel + 1, toLevel, awardType=BattlePassConsts.REWARD_BOTH))
        bonuses = BattlePassAwardsManager.uniteTokenBonuses(bonuses)
        return BattlePassAwardsManager.sortBonuses(bonuses)

    def __getLevelsPrice(self, levelCost):
        currency = levelCost.getCurrency()
        levelsCount = self.getLevelsCount()
        if levelsCount:
            value = levelCost.get(currency) * levelsCount
        else:
            value = 0
        return value


@replace_none_kwargs(battlePass=IBattlePassController)
def generatePackages(battlePass=None):
    packages = [ BattlePassPackage(chapter) for chapter, _ in enumerate(battlePass.getChapterConfig(), BattlePassConsts.MINIMAL_CHAPTER_NUMBER) ]
    return packages
