# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/extension_stubs/gui_lootboxes_controller.py
from skeletons.gui.game_control import IGuiLootBoxesController
import Event

class GuiLootBoxesControllerStub(IGuiLootBoxesController):
    onStatusChange = Event.Event()
    onAvailabilityChange = Event.Event()
    onBoxesCountChange = Event.Event()
    onWelcomeScreenClosed = Event.Event()

    @property
    def boxCountToGuaranteedBonus(self):
        pass

    @property
    def isConsumesEntitlements(self):
        return False

    def getGuaranteedBonusLimit(self, boxType):
        pass

    def getSetting(self, setting):
        return None

    def setSetting(self, setting, value):
        pass

    def getBoxInfo(self, boxType):
        return {}

    def getVehicleLevels(self, boxType):
        return set()

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

    def openShop(self):
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

    def getBoxesInfo(self):
        return {}

    def getBonusesOrder(self, category=None):
        return tuple()

    def getHangarOptimizer(self):
        return None
