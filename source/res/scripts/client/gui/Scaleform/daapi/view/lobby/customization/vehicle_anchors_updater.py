# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/vehicle_anchors_updater.py
import GUI
import Math
from gui.customization.shared import C11nId
from gui.shared.gui_items.customization.outfit import Area
from gui.Scaleform.daapi.view.lobby.customization.shared import C11nTabs

class VehicleAnchorsUpdater(object):

    def __init__(self, service, ctx):
        self.__service = service
        self.__ctx = ctx
        self.__vehicleCustomizationAnchors = None
        self.__processedAnchors = {}
        return

    def startUpdater(self, interfaceScale):
        if self.__vehicleCustomizationAnchors is None:
            self.__vehicleCustomizationAnchors = GUI.WGVehicleCustomizationAnchors(interfaceScale)
        return

    def stopUpdater(self):
        if self.__vehicleCustomizationAnchors is not None:
            self._delAllAnchors()
            self.__vehicleCustomizationAnchors = None
        return

    def setAnchors(self, displayObjects):
        if self.__vehicleCustomizationAnchors is not None:
            processedObjectIds = {}
            self._delAllAnchors()
            for displayObject in displayObjects:
                if hasattr(displayObject, 'slotData'):
                    slotId = displayObject.slotData.slotId
                    customSlotId = C11nId(areaId=slotId.areaId, slotType=slotId.slotId, regionIdx=slotId.regionId)
                    anchorParams = self.__getAnchorParams(customSlotId)
                    if anchorParams is not None:
                        anchorWorldPos = Math.Vector3(anchorParams.pos)
                        normal = Math.Vector3(anchorParams.normal)
                        if self.__ctx.currentTab in C11nTabs.REGIONS:
                            if customSlotId.areaId != Area.GUN:
                                normal.normalise()
                                anchorWorldPos -= normal * 0.2
                        scaleformUid = self.__vehicleCustomizationAnchors.addAnchor(anchorWorldPos, normal, displayObject, True, True, True)
                        processedObjectIds[customSlotId] = scaleformUid

            self.__processedAnchors = processedObjectIds
        return

    def updateAnchorPositionAndNormal(self, slotId, position, normal):
        scaleformUid = self.__processedAnchors.get(slotId, -1)
        if scaleformUid == -1:
            return
        self.__vehicleCustomizationAnchors.updateAnchorPositionAndNormal(scaleformUid, position, normal)

    def changeAnchorParams(self, slotId, isDisplayed, isAutoScalable, isActive=True):
        scaleformUid = self.__processedAnchors.get(slotId, -1)
        if scaleformUid == -1:
            return
        self.__vehicleCustomizationAnchors.changeAnchorParams(scaleformUid, isDisplayed, isAutoScalable, isActive)

    def setInterfaceScale(self, scale):
        self.__vehicleCustomizationAnchors.setInterfaceScale(scale)

    def setMenuParams(self, menuDisplayObject, menuWidth, menuHeight, menuCenterX, menuCenterY):
        self.__vehicleCustomizationAnchors.setMenuParams(menuDisplayObject, menuWidth, menuHeight, menuCenterX, menuCenterY)

    def displayMenu(self, display):
        self.__vehicleCustomizationAnchors.displayMenu(display)

    def attachMenuToAnchor(self, slotId):
        scaleformUid = self.__processedAnchors.get(slotId, -1)
        if scaleformUid == -1:
            return
        self.__vehicleCustomizationAnchors.attachMenuToAnchor(scaleformUid)

    def setMainView(self, displayObject):
        return self.__vehicleCustomizationAnchors.setMainView(displayObject)

    def __getAnchorParams(self, slotId):
        anchorParams = self.__service.getAnchorParams(slotId.areaId, slotId.slotType, slotId.regionIdx)
        return anchorParams

    def _delAllAnchors(self):
        if self.__vehicleCustomizationAnchors is not None:
            for scaleformUid in self.__processedAnchors.itervalues():
                self.__vehicleCustomizationAnchors.delAnchor(scaleformUid)

            self.__processedAnchors.clear()
        return
