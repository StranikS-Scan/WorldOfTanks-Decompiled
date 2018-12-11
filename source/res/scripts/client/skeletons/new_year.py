# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/new_year.py
from adisp import async
from skeletons.gui.game_control import IFestivityController

class ICustomizableObjectsManager(object):

    def init(self):
        raise NotImplementedError

    def fini(self):
        raise NotImplementedError

    @property
    def pendingEntitiesToDestroy(self):
        raise NotImplementedError

    def addCustomizableEntity(self, entity):
        raise NotImplementedError

    def removeCustomizableEntity(self, entity):
        raise NotImplementedError

    def getCustomizableEntity(self, anchorName):
        raise NotImplementedError

    def addCameraAnchor(self, anchorName, anchor):
        raise NotImplementedError

    def removeCameraAnchor(self, anchorName):
        raise NotImplementedError

    def getCameraAnchor(self, anchorName):
        raise NotImplementedError

    def addCameraTarget(self, anchorName, cameraTarget):
        raise NotImplementedError

    def removeCameraTarget(self, anchorName):
        raise NotImplementedError

    def getCameraTarget(self, anchorName):
        raise NotImplementedError

    def updateSlot(self, slot, toy, withHangingEffect=True):
        raise NotImplementedError

    def switchCamera(self, anchorName):
        raise NotImplementedError

    def getEffect(self, effectName):
        raise NotImplementedError


class INewYearController(IFestivityController):
    onDataUpdated = None

    def isEnabled(self):
        raise NotImplementedError

    def getHangarQuestsFlagData(self):
        raise NotImplementedError

    def getHangarWidgetLinkage(self):
        raise NotImplementedError

    def getHangarEdgeColor(self):
        raise NotImplementedError

    def getSlotDescrs(self, objectName=None):
        raise NotImplementedError

    def getToyDescr(self, toyID):
        raise NotImplementedError

    def getToysByType(self, slotID):
        raise NotImplementedError

    @async
    def hangToy(self, toyID, slotID, callback):
        raise NotImplementedError

    def getLevel(self, level):
        raise NotImplementedError

    def checkForNewToys(self, slot=None, objectType=None):
        raise NotImplementedError

    def getToysInSlots(self, objectName=None):
        raise NotImplementedError

    def getBattleBonus(self, bonusType):
        raise NotImplementedError

    def isCollectionCompleted(self, collectionID=None):
        raise NotImplementedError

    def getFinishTime(self):
        raise NotImplementedError

    def sendSeenToys(self, toyIDs):
        raise NotImplementedError

    def sendSeenToysInCollection(self, toyIDs):
        raise NotImplementedError

    def sendViewAlbum(self, settingID, rank):
        raise NotImplementedError
