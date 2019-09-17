# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/festival.py
from skeletons.gui.game_control import IFestivityController

class IFestivalController(IFestivityController):
    onDataUpdated = None
    onMiniGamesUpdated = None

    def setCurrentCardTabState(self, tabState):
        raise NotImplementedError

    def getCurrentCardTabState(self):
        raise NotImplementedError

    def getReceivedItemsCount(self):
        raise NotImplementedError

    def getTotalItemsCount(self):
        raise NotImplementedError

    def getTickets(self):
        raise NotImplementedError

    def getPlayerCard(self):
        raise NotImplementedError

    def getFestivalItems(self, criteria):
        raise NotImplementedError

    def getUnseenItems(self, typeName=None):
        raise NotImplementedError

    def markItemsAsSeen(self, itemsIDs):
        raise NotImplementedError

    def getGlobalPlayerCard(self):
        raise NotImplementedError

    def setGlobalPlayerCard(self, playerCard):
        raise NotImplementedError

    def getPackages(self):
        raise NotImplementedError

    def getPackageByID(self, pkgID):
        raise NotImplementedError

    def isCommonItemCollected(self):
        raise NotImplementedError

    def getTotalCommonItem(self):
        raise NotImplementedError

    def getRandomCost(self, randomName):
        raise NotImplementedError

    def canBuyAnyRandomPack(self):
        raise NotImplementedError

    def needToShowWhereEarnTickets(self):
        raise NotImplementedError

    def getCommonItems(self, randomName):
        raise NotImplementedError

    def getMagicBasis(self):
        raise NotImplementedError

    def canShowRandomBtnHint(self):
        raise NotImplementedError

    def getMiniGamesCooldown(self):
        raise NotImplementedError

    def getMiniGamesCooldownDuration(self):
        raise NotImplementedError

    def getMiniGamesAttemptsMax(self):
        raise NotImplementedError

    def getMiniGamesAttemptsLeft(self):
        raise NotImplementedError

    def forceUpdateMiniGames(self):
        raise NotImplementedError

    def isMiniGamesEnabled(self):
        raise NotImplementedError
