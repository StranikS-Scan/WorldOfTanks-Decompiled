# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/vehicle_anchors_updater.py
import logging
from copy import copy
from collections import defaultdict
import math
import GUI
import Math
from CurrentVehicle import g_currentVehicle
from Math import Vector3
from helpers import dependency
from gui.Scaleform.daapi.view.lobby.customization.shared import C11nTabs, getProjectionSlotFormfactor
from gui.Scaleform.daapi.view.lobby.customization.vehicle_anchor_states import Anchor
from gui.customization.shared import C11nId
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.customization.slots import SLOT_ASPECT_RATIO
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.shared.utils import IHangarSpace
_logger = logging.getLogger(__name__)
_LINES_SHIFT = 0.4
_MIN_PROJECTION_DECAL_ANCHORS_DIST = 0.15

class VehicleAnchorsUpdater(object):
    hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self, service, ctx):
        self.__service = service
        self.__ctx = ctx
        self.__vehicleCustomizationAnchors = None
        self.__processedAnchors = {}
        self.__menuAnchorId = None
        self.__changedStates = {}
        self.__closeGroups = DisjointSet()
        return

    def startUpdater(self, interfaceScale):
        if self.__vehicleCustomizationAnchors is None:
            self.__vehicleCustomizationAnchors = GUI.WGVehicleCustomizationAnchors(interfaceScale)
            self.__ctx.onPropertySheetHidden += self.__onPropertySheetHidden
            self.__ctx.onPropertySheetShown += self.__onPropertySheetShown
            self.__ctx.onCaruselItemSelected += self.__onCarouselItemSelected
            self.__ctx.onCaruselItemUnselected += self.__onCarouselItemUnselected
            self.__ctx.onCustomizationItemInstalled += self.__onItemInstalled
            self.__ctx.onCustomizationItemsRemoved += self.__onItemsRemoved
            self.__ctx.onChangesCanceled += self.__onChangesCanceled
            self.__ctx.onCustomizationSeasonChanged += self.__onSeasonChanged
            self.__ctx.onAnchorHovered += self.__onAnchorHovered
            self.__ctx.onAnchorUnhovered += self.__onAnchorUnhovered
            entity = self.hangarSpace.getVehicleEntity()
            if entity is not None and entity.appearance is not None:
                entity.appearance.loadState.subscribe(self.__onVehicleLoadFinished, self.__onVehicleLoadStarted)
        return

    def stopUpdater(self):
        if self.__vehicleCustomizationAnchors is not None:
            self.__ctx.onPropertySheetHidden -= self.__onPropertySheetHidden
            self.__ctx.onPropertySheetShown -= self.__onPropertySheetShown
            self.__ctx.onCaruselItemSelected -= self.__onCarouselItemSelected
            self.__ctx.onCaruselItemUnselected -= self.__onCarouselItemUnselected
            self.__ctx.onCustomizationItemInstalled -= self.__onItemInstalled
            self.__ctx.onCustomizationItemsRemoved -= self.__onItemsRemoved
            self.__ctx.onChangesCanceled -= self.__onChangesCanceled
            self.__ctx.onCustomizationSeasonChanged -= self.__onSeasonChanged
            self.__ctx.onAnchorHovered -= self.__onAnchorHovered
            self.__ctx.onAnchorUnhovered -= self.__onAnchorUnhovered
            entity = self.hangarSpace.getVehicleEntity()
            if entity is not None and entity.appearance is not None:
                entity.appearance.loadState.unsubscribe(self.__onVehicleLoadFinished, self.__onVehicleLoadStarted)
            self.__delAllAnchors()
            self.__vehicleCustomizationAnchors = None
        return

    def setAnchors(self, displayObjects):
        if self.__vehicleCustomizationAnchors is None:
            return
        else:
            self.__delAllAnchors()
            for displayObject in displayObjects:
                if not hasattr(displayObject, 'slotData'):
                    continue
                slotData = displayObject.slotData
                anchorId = C11nId(areaId=slotData.slotId.areaId, slotType=slotData.slotId.slotId, regionIdx=slotData.slotId.regionId)
                anchorParams = self.getAnchorParams(anchorId)
                if anchorParams is None:
                    continue
                location = anchorParams.location
                linesPosition = copy(location.position)
                slotWidth = 0.0
                if self.__ctx.currentTab in (C11nTabs.EMBLEM, C11nTabs.INSCRIPTION):
                    slotWidth = anchorParams.descriptor.size
                    slotHeight = slotWidth * SLOT_ASPECT_RATIO[anchorId.slotType]
                    linesShift = slotHeight * _LINES_SHIFT
                    linesPosition -= location.up * linesShift
                position = location.position
                direction = location.normal
                uid = self.__vehicleCustomizationAnchors.addAnchor(position, direction, linesPosition, slotWidth, displayObject, True, True, False, True)
                anchor = Anchor(anchorId, uid, position, direction)
                if anchorId.slotType == GUI_ITEM_TYPE.PROJECTION_DECAL:
                    self.__closeGroups.add(anchorId)
                    for aId, a in self.__processedAnchors.iteritems():
                        dist = (a.position - anchor.position).length
                        if dist < _MIN_PROJECTION_DECAL_ANCHORS_DIST:
                            self.__closeGroups.union(aId, anchorId)

                self.__processedAnchors[anchorId] = anchor
                anchor.setup()

            self.__changeAnchorsStates()
            self.__updateAnchorsVisability()
            return

    def setCollisions(self):
        entity = self.__ctx.hangarSpace.getVehicleEntity()
        if entity and entity.appearance and entity.appearance.isLoaded():
            collisions = entity.appearance.collisions
            if collisions is not None:
                self.__vehicleCustomizationAnchors.setCollisions(collisions)
            else:
                _logger.error('Collision component for current vehicle is missing.')
        else:
            _logger.error('Vehicle entity is not loaded/exist.')
        return

    def updateAnchorPositionAndNormal(self, anchorId, position, normal):
        if anchorId in self.__processedAnchors:
            anchor = self.__processedAnchors[anchorId]
            self.__vehicleCustomizationAnchors.updateAnchorPositionAndNormal(anchor.uid, position, normal)

    def setAnchorShift(self, anchorId, shift):
        if anchorId in self.__processedAnchors:
            anchor = self.__processedAnchors[anchorId]
            self.__vehicleCustomizationAnchors.setAnchorShift(anchor.uid, shift)

    def changeAnchorParams(self, anchorId, isDisplayed, isAutoScalable, isCollidable=False, isActive=True):
        if anchorId in self.__processedAnchors:
            anchor = self.__processedAnchors[anchorId]
            self.__vehicleCustomizationAnchors.changeAnchorParams(anchor.uid, isDisplayed, isAutoScalable, isCollidable, isActive)

    def setInterfaceScale(self, scale):
        self.__vehicleCustomizationAnchors.setInterfaceScale(scale)

    def setMenuParams(self, menuDisplayObject, menuWidth, menuHeight, menuCenterX, menuCenterY):
        self.__vehicleCustomizationAnchors.setMenuParams(menuDisplayObject, menuWidth, menuHeight, menuCenterX, menuCenterY)

    def displayMenu(self, display):
        self.__vehicleCustomizationAnchors.displayMenu(display)

    def displayLine(self, display):
        self.__vehicleCustomizationAnchors.displayLine(display)

    def attachMenuToAnchor(self, anchorId):
        if anchorId in self.__processedAnchors:
            anchor = self.__processedAnchors[anchorId]
            self.__vehicleCustomizationAnchors.attachMenuToAnchor(anchor.uid)

    def setMainView(self, displayObject):
        return self.__vehicleCustomizationAnchors.setMainView(displayObject)

    def hideAllAnchors(self):
        if self.__vehicleCustomizationAnchors is not None:
            for anchor in self.__processedAnchors.itervalues():
                self.__vehicleCustomizationAnchors.changeAnchorParams(anchor.uid, False, False)

        return

    def registerInscriptionController(self, inscriptionController, inputLines):
        self.__vehicleCustomizationAnchors.registerInscriptionController(inscriptionController, inputLines)

    def getAnchorParams(self, anchorId):
        anchorParams = self.__service.getAnchorParams(anchorId.areaId, anchorId.slotType, anchorId.regionIdx)
        return anchorParams

    def __delAllAnchors(self):
        if self.__vehicleCustomizationAnchors is not None:
            for anchor in self.__processedAnchors.itervalues():
                self.__vehicleCustomizationAnchors.delAnchor(anchor.uid)
                anchor.destroy()

            self.__processedAnchors.clear()
            self.__closeGroups.clear()
        return

    def __updateAnchorsVisability(self):
        if self.__ctx.currentTab in C11nTabs.REGIONS:
            self.__updateRegionsAnchorsVisability()
        elif self.__ctx.currentTab in (C11nTabs.EMBLEM, C11nTabs.INSCRIPTION):
            self.__updateDecalAnchorsVisability()
        elif self.__ctx.currentTab == C11nTabs.PROJECTION_DECAL:
            self.__updateProjectionDecalAnchorsVisability()

    def __updateRegionsAnchorsVisability(self):
        for anchorId in self.__processedAnchors:
            isDisplayed = self.__ctx.isSlotFilled(anchorId)
            isAutoScalable = self.__menuAnchorId != anchorId
            self.changeAnchorParams(anchorId, isDisplayed=isDisplayed, isAutoScalable=isAutoScalable)

    def __updateDecalAnchorsVisability(self):
        for anchorId in self.__processedAnchors:
            isDisplayed = anchorId != self.__menuAnchorId
            self.changeAnchorParams(anchorId, isDisplayed=isDisplayed, isAutoScalable=True)

    def __updateProjectionDecalAnchorsVisability(self):
        formfactor = None
        intCD = self.__ctx.selectedCarouselItem.intCD
        if intCD != -1:
            item = self.__service.getItemByCD(intCD)
            if item is not None:
                formfactor = item.formfactor
        visibleAnchors = defaultdict(set)
        for anchorId in self.__processedAnchors:
            if self.__ctx.isSlotFilled(anchorId):
                isDisplayed = self.__menuAnchorId != anchorId
                self.changeAnchorParams(anchorId, isDisplayed=isDisplayed, isAutoScalable=True)
                root = self.__closeGroups.find(anchorId)
                if root is not None:
                    visibleAnchors[root].add(anchorId)
                continue
            if formfactor is not None:
                anchor = g_currentVehicle.item.getAnchorBySlotId(anchorId.slotType, anchorId.areaId, anchorId.regionIdx)
                if anchor.isFitForFormfactor(formfactor):
                    self.changeAnchorParams(anchorId, isDisplayed=True, isAutoScalable=True, isCollidable=True)
                    root = self.__closeGroups.find(anchorId)
                    if root is not None:
                        visibleAnchors[root].add(anchorId)
                    continue
            self.changeAnchorParams(anchorId, isDisplayed=False, isAutoScalable=False)

        self.__spreadAnchorsApart(visibleAnchors)
        return

    def __spreadAnchorsApart(self, visibleAnchors):
        for anchorIds in visibleAnchors.itervalues():
            anchorsCount = len(anchorIds)
            if anchorsCount > 1:
                radius = _MIN_PROJECTION_DECAL_ANCHORS_DIST * 0.5 / math.sin(math.pi / anchorsCount)
                position = sum((self.__processedAnchors[anchorId].position for anchorId in anchorIds), Vector3()) / anchorsCount
                direction = sum((self.__processedAnchors[anchorId].direction for anchorId in anchorIds), Vector3()) / anchorsCount
                transformMatrix = Math.Matrix()
                transformMatrix.lookAt(position, direction, (0, 1, 0))
                transformMatrix.invert()
                shift = Vector3(0, radius, 0)
                angle = 2 * math.pi / anchorsCount
                rotor = Math.Matrix()
                rotor.setRotateZ(angle)
                for anchorId in sorted(anchorIds, key=getProjectionSlotFormfactor):
                    anchor = self.__processedAnchors[anchorId]
                    newPosition = transformMatrix.applyPoint(shift)
                    anchor.setShift(newPosition - anchor.position)
                    self.setAnchorShift(anchorId, anchor.shift)
                    shift = rotor.applyPoint(shift)

            anchorId = anchorIds.pop()
            self.setAnchorShift(anchorId, Vector3())

    def __onPropertySheetHidden(self):
        self.__menuAnchorId = None
        self.__updateAnchorsVisability()
        return

    def __onPropertySheetShown(self, anchorId):
        self.__menuAnchorId = anchorId
        self.__updateAnchorsVisability()

    def __onCarouselItemSelected(self, *_, **__):
        if self.__ctx.currentTab == C11nTabs.PROJECTION_DECAL:
            self.__updateAnchorsVisability()

    def __onCarouselItemUnselected(self, *_, **__):
        if self.__ctx.currentTab == C11nTabs.PROJECTION_DECAL:
            for anchor in self.__processedAnchors.itervalues():
                anchor.state.onItemUnselected()

            self.__changeAnchorsStates()
            self.__updateAnchorsVisability()

    def __onItemInstalled(self, item, component, slotId, limitReached):
        regionIdx = self.__ctx.getAnchorBySlotId(slotId).regionIdx
        anchorId = C11nId(slotId.areaId, slotId.slotType, regionIdx)
        anchor = self.__processedAnchors.get(anchorId)
        if anchor is not None:
            anchor.state.onItemInstalled()
        outfit = self.__ctx.getModifiedOutfit(self.__ctx.currentSeason)
        if self.__ctx.isC11nItemsQuantityLimitReached(outfit, slotId.slotType):
            for anchor in self.__processedAnchors.itervalues():
                anchor.state.onLocked()

        self.__changeAnchorsStates()
        self.__updateAnchorsVisability()
        return

    def __onItemsRemoved(self, *_, **__):
        self.__updateAnchorsState()
        self.__updateAnchorsVisability()

    def __onChangesCanceled(self, *_, **__):
        self.__updateAnchorsState()
        self.__updateAnchorsVisability()

    def __onSeasonChanged(self, *_, **__):
        self.__updateAnchorsState()
        self.__updateAnchorsVisability()

    def __onAnchorHovered(self, anchorId):
        if self.__ctx.currentTab != C11nTabs.PROJECTION_DECAL:
            return
        elif not self.__ctx.isCaruselItemSelected():
            return
        else:
            anchor = self.__processedAnchors.get(anchorId)
            if anchor is not None:
                slotId = self.__ctx.getSlotIdByAnchorId(anchorId)
                if slotId is not None:
                    item = self.__ctx.getItemFromRegion(slotId)
                    if item is not None and item.intCD == self.__ctx.selectedCarouselItem.intCD:
                        return
                anchor.state.onHovered()
            self.__changeAnchorsStates()
            return

    def __onAnchorUnhovered(self, anchorId):
        if self.__ctx.currentTab != C11nTabs.PROJECTION_DECAL:
            return
        elif not self.__ctx.isCaruselItemSelected():
            return
        else:
            anchor = self.__processedAnchors.get(anchorId)
            if anchor is not None:
                anchor.state.onUnhovered()
            self.__changeAnchorsStates()
            return

    def __updateAnchorsState(self):
        for anchor in self.__processedAnchors.itervalues():
            anchor.updateState()

        self.__changeAnchorsStates()

    def onAnchorStateChanged(self, uid, state):
        if state is not None:
            self.__changedStates[uid] = state
        return

    def onCameraLocated(self, locatedAnchorId=None):
        for anchorId, anchor in self.__processedAnchors.iteritems():
            if anchorId == locatedAnchorId:
                anchor.state.onSelected()
            anchor.state.onUnselected()

        self.__changeAnchorsStates()

    def getAnchorState(self, anchorId):
        if anchorId in self.__processedAnchors:
            anchor = self.__processedAnchors[anchorId]
            return anchor.stateID

    def __changeAnchorsStates(self):
        if self.__changedStates:
            self.__ctx.onAnchorsStateChanged(self.__changedStates)
            self.__changedStates.clear()

    def __onVehicleChanged(self):
        self.setCollisions()

    def __onVehicleLoadStarted(self):
        pass

    def __onVehicleLoadFinished(self):
        self.setCollisions()

    def getProcessedAnchor(self, anchorId):
        return self.__processedAnchors[anchorId] if anchorId in self.__processedAnchors else None


def getAnchorShiftParams(positionA, positionB, normal):
    if positionA != positionB:
        direction = positionA - positionB
        distance = direction.length
    else:
        if normal != Vector3(0, 1, 0):
            direction = normal * Vector3(0, 1, 0)
        else:
            direction = normal * Vector3(1, 0, 0)
        distance = 0
    direction.normalise()
    return (direction, distance)


class DisjointSet(object):

    def __init__(self):
        super(DisjointSet, self).__init__()
        self._root = {}
        self._set = {}

    @property
    def subsets(self):
        return self._set.itervalues()

    def add(self, element):
        self._root[element] = element
        self._set[element] = {element}

    def find(self, element):
        return self._root[element] if element in self._root else None

    def get(self, element):
        root = self.find(element)
        return self._set[root] if root is not None and root in self._set else None

    def union(self, elementA, elementB):
        rootA = self.find(elementA)
        rootB = self.find(elementB)
        if rootA is not None and rootB is not None and rootA != rootB:
            if len(self._set[rootA]) < len(self._set[rootB]):
                rootA, rootB = rootB, rootA
            setB = self._set.pop(rootB)
            for element in setB:
                self._root[element] = rootA

            self._set[rootA].update(setB)
        return

    def clear(self):
        self._root.clear()
        self._set.clear()
