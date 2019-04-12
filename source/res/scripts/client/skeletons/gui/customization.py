# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/gui/customization.py
from Event import Event

class ICustomizationService(object):
    onRegionHighlighted = None
    onOutfitChanged = None

    def init(self):
        raise NotImplementedError

    def fini(self):
        raise NotImplementedError

    def showCustomization(self, vehInvId=None, callback=None):
        raise NotImplementedError

    def getCtx(self):
        raise NotImplementedError

    def destroyCtx(self):
        raise NotImplementedError

    def startHighlighter(self, mode):
        raise NotImplementedError

    def stopHighlighter(self):
        raise NotImplementedError

    def suspendHighlighter(self):
        raise NotImplementedError

    def resumeHighlighter(self):
        raise NotImplementedError

    def getSelectionMode(self):
        raise NotImplementedError

    def getPointForRegionLeaderLine(self, areaId):
        raise NotImplementedError

    def getAnchorParams(self, areaId, slotId, regionId):
        raise NotImplementedError

    def getHightlighter(self):
        raise NotImplementedError

    def getItems(self, itemTypeID, vehicle=None, criteria=None):
        raise NotImplementedError

    def getPaints(self, vehicle=None, criteria=None):
        raise NotImplementedError

    def getCamouflages(self, vehicle=None, criteria=None):
        raise NotImplementedError

    def getStyles(self, vehicle=None, criteria=None):
        raise NotImplementedError

    def getItemByID(self, itemTypeID, itemID):
        raise NotImplementedError

    def getItemByCD(self, itemCD):
        raise NotImplementedError

    def getEmptyOutfit(self):
        raise NotImplementedError

    def tryOnOutfit(self, outfit):
        raise NotImplementedError

    def getOutfit(self, season):
        raise NotImplementedError

    def getCustomOutfit(self, season):
        raise NotImplementedError

    def getCurrentStyle(self):
        raise NotImplementedError

    def isCurrentStyleInstalled(self):
        raise NotImplementedError

    def isRegionSelected(self):
        raise NotImplementedError

    def buyItems(self, item, count, vehicle=None):
        raise NotImplementedError

    def sellItem(self, item, count, vehicle=None):
        raise NotImplementedError

    def buyAndEquipOutfit(self, outfit, season, vehicle=None):
        raise NotImplementedError

    def buyAndEquipStyle(self, style, vehicle=None):
        raise NotImplementedError

    def setSelectHighlighting(self, value):
        raise NotImplementedError

    def resetHighlighting(self):
        raise NotImplementedError

    def highlightRegions(self, regionsMask):
        raise NotImplementedError

    def selectRegions(self, regionsMask):
        raise NotImplementedError

    def moveHangarVehicleToCustomizationRoom(self):
        raise NotImplementedError

    def setSelectingRegionEnabled(self, enable):
        raise NotImplementedError

    def setDOFenabled(self, enable):
        raise NotImplementedError

    def setDOFparams(self, params):
        raise NotImplementedError
