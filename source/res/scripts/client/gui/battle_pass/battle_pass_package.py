# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_pass/battle_pass_package.py
from helpers import dependency
from battle_pass_common import BattlePassConsts
from gui.battle_pass.battle_pass_award import BattlePassAwardsManager
from gui.battle_pass.battle_pass_helpers import isCurrentBattlePassStateBase
from skeletons.gui.game_control import IBattlePassController
from skeletons.gui.shared import IItemsCache

class BattlePassPackage(object):
    __slots__ = ('__seasonID',)
    _itemsCache = dependency.descriptor(IItemsCache)
    _battlePassController = dependency.descriptor(IBattlePassController)

    def __init__(self):
        self.__seasonID = self._battlePassController.getSeasonID()

    def getPrice(self):
        bpCost = self._itemsCache.items.shop.getBattlePassCost()
        currency = bpCost.getCurrency()
        if self.hasBattlePass():
            value = bpCost.get(currency)
        else:
            value = 0
        return value

    def getLevelsCount(self):
        pass

    def getNowAwards(self):
        curLevel = self._getBPCurrentLevel()
        bonuses = []
        if self.hasBattlePass():
            bonuses.extend(self._battlePassController.getPackedAwardsInterval(1, curLevel, awardType=BattlePassConsts.REWARD_PAID))
            if not isCurrentBattlePassStateBase():
                _, paidBonuses = self._battlePassController.getSplitFinalAwards()
                bonuses.extend(paidBonuses)
        return BattlePassAwardsManager.sortBonuses(bonuses)

    def getFutureAwards(self):
        bonuses = []
        if self.hasBattlePass():
            fromLevel = self._getBPCurrentLevel() + self.getLevelsCount()
            bonuses.extend(self._battlePassController.getPackedAwardsInterval(fromLevel + 1, self._battlePassController.getMaxLevel(), awardType=BattlePassConsts.REWARD_PAID))
            if isCurrentBattlePassStateBase():
                _, paidBonuses = self._battlePassController.getSplitFinalAwards()
                bonuses.extend(paidBonuses)
        return BattlePassAwardsManager.sortBonuses(bonuses)

    def getSeasonID(self):
        return self.__seasonID

    def getTimeToUnlock(self):
        pass

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

    def isBought(self):
        return self._battlePassController.isBought()

    def _getBPCurrentLevel(self):
        return self._battlePassController.getMaxLevel() if not isCurrentBattlePassStateBase() else self._battlePassController.getCurrentLevel()


class PackageLevels(BattlePassPackage):

    def hasBattlePass(self):
        return False

    def setLevels(self, value):
        pass

    def getLevelsCount(self):
        levelsCount = self._battlePassController.getMaxLevel() - self._getBPCurrentLevel()
        if levelsCount > self._battlePassController.getMaxSoldLevelsBeforeUnlock():
            levelsCount = self._battlePassController.getMaxSoldLevelsBeforeUnlock()
        return levelsCount

    def getPrice(self):
        levelCost = self._itemsCache.items.shop.getBattlePassLevelCost()
        currency = levelCost.getCurrency()
        levelsCount = self.getLevelsCount()
        if levelsCount:
            value = levelCost.get(currency) * levelsCount
        else:
            value = 0
        return value

    def getNowAwards(self):
        curLevel = self._getBPCurrentLevel()
        toLevel = curLevel + self.getLevelsCount()
        bonuses = []
        if self.getLevelsCount():
            bonuses.extend(self._battlePassController.getPackedAwardsInterval(curLevel + 1, toLevel, awardType=BattlePassConsts.REWARD_BOTH))
            if toLevel == self._battlePassController.getMaxLevel():
                bonuses.extend(self._battlePassController.getFinalAwardsForPurchaseLevels())
        return BattlePassAwardsManager.sortBonuses(bonuses)

    def isLocked(self):
        return not self._battlePassController.isBought()

    def isDynamic(self):
        return False

    def isBought(self):
        return self._battlePassController.getBoughtLevels() > 0

    def isVisible(self):
        isAvaibleToBuy = not self._battlePassController.isSellAnyLevelsUnlocked()
        return (isAvaibleToBuy or self.isBought()) and isCurrentBattlePassStateBase()


class PackageAnyLevels(PackageLevels):
    __slots__ = ('__dynamicLevelsCount',)

    def __init__(self):
        self.__dynamicLevelsCount = 1
        super(PackageAnyLevels, self).__init__()

    def setLevels(self, value):
        self.__dynamicLevelsCount = value

    def getLevelsCount(self):
        maxLevelsCount = self._battlePassController.getMaxLevel() - self._battlePassController.getCurrentLevel()
        return maxLevelsCount if self.__dynamicLevelsCount > maxLevelsCount else self.__dynamicLevelsCount

    def getTimeToUnlock(self):
        return self._battlePassController.getSellAnyLevelsUnlockTimeLeft() if not self._battlePassController.isSellAnyLevelsUnlocked() else 0

    def isLocked(self):
        return not (self._battlePassController.isBought() and self._battlePassController.isSellAnyLevelsUnlocked())

    def isDynamic(self):
        return True

    def isBought(self):
        return False

    def isVisible(self):
        return isCurrentBattlePassStateBase()


def generatePackages():
    packages = list([BattlePassPackage(), PackageLevels(), PackageAnyLevels()])
    return packages
