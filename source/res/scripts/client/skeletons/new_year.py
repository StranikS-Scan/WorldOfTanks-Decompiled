# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/new_year.py
from skeletons.gui.game_control import IGameController

class ISwitchHandler(object):

    @property
    def nextHandler(self):
        return NotImplementedError

    def switchTo(self, state, callback=None):
        return NotImplementedError

    def getSwitchHandler(self, switchHandlerType):
        return NotImplementedError


class ICustomizableObjectsManager(ISwitchHandler):
    onNYSceneObjectsLoadedEvent = None

    def init(self):
        raise NotImplementedError

    def fini(self):
        raise NotImplementedError

    @property
    def state(self):
        raise NotImplementedError

    @property
    def effectsCache(self):
        raise NotImplementedError

    def addCustomizableEntity(self, entity):
        raise NotImplementedError

    def removeCustomizableEntity(self, entity):
        raise NotImplementedError

    def addSelectableEntity(self, entity):
        raise NotImplementedError

    def removeSelectableEntity(self, entity):
        raise NotImplementedError

    def enableAllSelectableEntities(self, isEnabled):
        raise NotImplementedError

    def getCustomizableEntity(self, anchorName):
        raise NotImplementedError

    def addCameraAnchor(self, anchorName, anchor):
        raise NotImplementedError

    def removeCameraAnchor(self, anchorName):
        raise NotImplementedError

    def getCameraAnchor(self, anchorName):
        raise NotImplementedError

    def updateSlot(self, slot, toy):
        raise NotImplementedError


class INewYearController(IGameController):
    onSlotUpdated = None
    onInventoryUpdated = None
    onProgressChanged = None
    onToyFragmentsChanged = None
    onToyCollectionChanged = None
    onStateChanged = None
    onCraftedToysChanged = None
    onToysBreak = None
    onToysBreakFailed = None
    onToysBreakStarted = None

    def init(self):
        raise NotImplementedError

    def fini(self):
        raise NotImplementedError

    def isEnabled(self):
        raise NotImplementedError

    def isAvailable(self):
        raise NotImplementedError

    @property
    def boxStorage(self):
        raise NotImplementedError

    @property
    def chestStorage(self):
        raise NotImplementedError

    @property
    def vehDiscountsStorage(self):
        raise NotImplementedError

    @property
    def tankmanDiscountsStorage(self):
        raise NotImplementedError

    @property
    def stateHandler(self):
        raise NotImplementedError

    @property
    def craftedToys(self):
        raise NotImplementedError

    def clearCraftedToys(self):
        raise NotImplementedError

    @property
    def toysDescrs(self):
        raise NotImplementedError

    @property
    def slotsDescrs(self):
        raise NotImplementedError

    @property
    def collectionRewardsBySettingID(self):
        raise NotImplementedError

    @property
    def receivedToysCollection(self):
        raise NotImplementedError

    @property
    def maxLevel(self):
        raise NotImplementedError

    @property
    def state(self):
        raise NotImplementedError

    @staticmethod
    def getSettingIndexInNationsOrder(setting):
        raise NotImplementedError

    def getToysForSlot(self, slotID):
        raise NotImplementedError

    def getPlacedToy(self, slotID):
        raise NotImplementedError

    def getPlacedToys(self, inSlots):
        raise NotImplementedError

    def getProgress(self):
        raise NotImplementedError

    def getToyFragments(self):
        raise NotImplementedError

    def getInventory(self):
        raise NotImplementedError

    def placeToy(self, slotID, toyID):
        raise NotImplementedError

    def markToysAsSeen(self, toys):
        raise NotImplementedError

    def getPriceForCraft(self, toyType, toyNation, toyLevel):
        raise NotImplementedError

    def getFragmentsForToy(self, toyID):
        raise NotImplementedError

    def craftToy(self, toyType, toyNation, toyLevel):
        raise NotImplementedError

    def breakToys(self, toys, toyIndexes=None, fromSlot=False):
        raise NotImplementedError

    def getBonusesForNation(self, nationID):
        raise NotImplementedError

    def getSettingForNation(self, nationID):
        raise NotImplementedError

    def getBonusesForSetting(self, settingID):
        raise NotImplementedError

    def getCollectionLevelForNation(self, nationID):
        raise NotImplementedError

    def getCollectionRatingForNation(self, nationID):
        raise NotImplementedError

    def calculateBonusesForCollectionLevel(self, collectionLevel):
        raise NotImplementedError


class INYSoundEvents(object):

    def init(self):
        raise NotImplementedError

    def fini(self):
        raise NotImplementedError

    def onCustomizationStateChanged(self, newState):
        raise NotImplementedError


class INewYearUIManager(object):
    onCraftPopoverFilterChanged = None
    onChestGiftsLoaded = None
    onChestGiftsDone = None
    onChestDone = None
    buttonClickOpenChest = None
    buttonClickOpenNextChest = None
    buttonClickCloseChest = None
    chestViewDone = None

    def fini(self):
        raise NotImplementedError

    def getCraftPopoverFilter(self):
        raise NotImplementedError

    def setCraftPopoverFilter(self, craftFilter):
        raise NotImplementedError

    def getSelectedCraftToy(self):
        raise NotImplementedError

    def setSelectedCraftToy(self, selectedToy):
        raise NotImplementedError

    def getSelectedCollectionLevels(self):
        raise NotImplementedError

    def setSelectedCollectionLevels(self, selectedCollectionLevels):
        raise NotImplementedError
