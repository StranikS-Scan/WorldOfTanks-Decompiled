# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/vehicle_anchors_updater.py
from copy import copy
import GUI
from gui.customization.shared import C11nId
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.customization.outfit import Area
from gui.shared.gui_items.customization.slots import SLOT_ASPECT_RATIO
from gui.Scaleform.daapi.view.lobby.customization.shared import C11nTabs
_ANCHOR_SHIFT = {GUI_ITEM_TYPE.EMBLEM: 0.5,
 GUI_ITEM_TYPE.INSCRIPTION: 0.3}
_LINES_SHIFT = 0.4
_REGION_ANCHOR_SHIFT = 0.2

class VehicleAnchorsUpdater(object):

    def __init__(self, service, ctx):
        self.__service = service
        self.__ctx = ctx
        self.__vehicleCustomizationAnchors = None
        self.__processedAnchors = {}
        from gui.ClientHangarSpace import hangarCFG
        cfg = hangarCFG()
        self.__vScale = cfg['v_scale'] if 'v_scale' in cfg else 1.0
        return

    def startUpdater(self, interfaceScale):
        if self.__vehicleCustomizationAnchors is None:
            self.__vehicleCustomizationAnchors = GUI.WGVehicleCustomizationAnchors(interfaceScale)
        return

    def stopUpdater(self):
        if self.__vehicleCustomizationAnchors is not None:
            self.__delAllAnchors()
            self.__vehicleCustomizationAnchors = None
        return

    def setAnchors(self, displayObjects, propSheetSlotId):
        if self.__vehicleCustomizationAnchors is not None:
            processedObjectIds = {}
            self.__delAllAnchors()
            for displayObject in displayObjects:
                if not hasattr(displayObject, 'slotData'):
                    continue
                slotData = displayObject.slotData
                slotId = C11nId(areaId=slotData.slotId.areaId, slotType=slotData.slotId.slotId, regionIdx=slotData.slotId.regionId)
                anchorParams = self.__getAnchorParams(slotId)
                if anchorParams is None:
                    continue
                location = anchorParams.location
                position = copy(location.position)
                linesPosition = copy(location.position)
                slotWidth = 0.0
                if self.__ctx.currentTab in C11nTabs.REGIONS and slotId.areaId != Area.GUN:
                    position -= location.normal * _REGION_ANCHOR_SHIFT * self.__vScale
                elif self.__ctx.currentTab in (C11nTabs.EMBLEM, C11nTabs.INSCRIPTION):
                    slotWidth = anchorParams.descriptor.size
                    slotHeight = slotWidth * SLOT_ASPECT_RATIO[slotId.slotType]
                    linesShift = slotHeight * _LINES_SHIFT * self.__vScale
                    linesPosition -= location.up * linesShift
                    if slotId != propSheetSlotId:
                        item = self.__ctx.getItemFromRegion(slotId)
                        if item is not None or slotId.slotType == GUI_ITEM_TYPE.EMBLEM:
                            anchorShift = slotHeight * _ANCHOR_SHIFT[slotId.slotType] * self.__vScale
                            position += location.up * anchorShift
                scaleformUid = self.__vehicleCustomizationAnchors.addAnchor(position, location.normal, linesPosition, slotWidth, displayObject, True, True, True)
                processedObjectIds[slotId] = scaleformUid

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

    def displayLine(self, display):
        self.__vehicleCustomizationAnchors.displayLine(display)

    def attachMenuToAnchor(self, slotId):
        scaleformUid = self.__processedAnchors.get(slotId, -1)
        if scaleformUid == -1:
            return
        self.__vehicleCustomizationAnchors.attachMenuToAnchor(scaleformUid)

    def setMainView(self, displayObject):
        return self.__vehicleCustomizationAnchors.setMainView(displayObject)

    def hideAllAnchors(self):
        if self.__vehicleCustomizationAnchors is not None:
            for scaleformUid in self.__processedAnchors.itervalues():
                self.__vehicleCustomizationAnchors.changeAnchorParams(scaleformUid, False, False)

        return

    def registerInscriptionController(self, inscriptionController, inputLines):
        self.__vehicleCustomizationAnchors.registerInscriptionController(inscriptionController, inputLines)

    def __getAnchorParams(self, slotId):
        anchorParams = self.__service.getAnchorParams(slotId.areaId, slotId.slotType, slotId.regionIdx)
        return anchorParams

    def __delAllAnchors(self):
        if self.__vehicleCustomizationAnchors is not None:
            for scaleformUid in self.__processedAnchors.itervalues():
                self.__vehicleCustomizationAnchors.delAnchor(scaleformUid)

            self.__processedAnchors.clear()
        return
