# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/extension_stubs/gui_lootboxes_controller.py
from skeletons.gui.game_control import IGuiLootBoxesController
import Event

class GuiLootBoxesControllerStub(IGuiLootBoxesController):
    onStatusChange = Event.Event()
    onAvailabilityChange = Event.Event()
    onBoxesCountChange = Event.Event()
    onKeysUpdate = Event.Event()
    onWelcomeScreenClosed = Event.Event()

    @property
    def isConsumesEntitlements(self):
        return False

    def getSetting(self, setting):
        return None

    def setSetting(self, setting, value):
        pass

    def isEnabled(self):
        return False

    def isLootBoxesAvailable(self):
        return False

    def isBuyAvailable(self):
        return False

    def isFirstStorageEnter(self):
        return True

    def setStorageVisited(self):
        pass

    def getDayLimit(self):
        pass

    def openShop(self, lootboxID=None):
        pass

    def getDayInfoStatistics(self):
        return {}

    def getExpiresAtLootBoxBuyCounter(self):
        pass

    def getTimeLeftToResetPurchase(self):
        pass

    def getStoreInfo(self):
        return {}

    def getBoxesIDs(self):
        pass

    def getBoxesCount(self):
        pass

    def getBoxKeysCount(self):
        pass

    def getKeyByID(self, keyID):
        return None

    def getKeyByTokenID(self, keyID):
        return None

    def getBonusesOrder(self, category=None):
        return tuple()

    def getHangarOptimizer(self):
        return None

    def addShopWindowHandler(self, keyHandler, handler):
        pass

    def hasLootboxKey(self):
        return False

    def hasInfiniteLootboxes(self):
        return False

    def getGuiLootBoxes(self):
        return []

    def getGuiLootBoxByTokenID(self, tokenID):
        return None
