# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/vehicle_anchors_updater.py
import logging
import math
from collections import defaultdict
from copy import copy
import typing
import GUI
import Math
from CurrentVehicle import g_currentVehicle
from Math import Vector3
from gui.Scaleform.daapi.view.lobby.customization.shared import isSlotFilled, isItemsQuantityLimitReached, CustomizationTabs, getProjectionSlotFormfactor
from gui.Scaleform.daapi.view.lobby.customization.vehicle_anchor_states import Anchor
from gui.customization.constants import CustomizationModes
from gui.customization.shared import C11nId, EDITABLE_STYLE_APPLY_TO_ALL_AREAS_TYPES
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.customization.slots import SLOT_ASPECT_RATIO
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.shared.utils import IHangarSpace
from vehicle_outfit.outfit import Area
if typing.TYPE_CHECKING:
    from gui.Scaleform.daapi.view.lobby.customization.context.context import CustomizationContext
_logger = logging.getLogger(__name__)
_LINES_SHIFT = 0.4
_MIN_PROJECTION_DECAL_ANCHORS_DIST = 0.15

class VehicleAnchorsUpdater(object):
    __hangarSpace = dependency.descriptor(IHangarSpace)
    __service = dependency.descriptor(ICustomizationService)
    __settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, ctx):
        self.__ctx = ctx
        self.__vehicleCustomizationAnchors = None
        self.__processedAnchors = {}
        self.__menuSlotId = None
        self.__changedStates = {}
        self.__closeGroups = DisjointSet()
        return

    def startUpdater(self):
        if self.__vehicleCustomizationAnchors is None:
            interfaceScale = self.__settingsCore.interfaceScale.get()
            self.__vehicleCustomizationAnchors = GUI.WGVehicleCustomizationAnchors(interfaceScale)
            self.__ctx.events.onPropertySheetHidden += self.__onPropertySheetHidden
            self.__ctx.events.onPropertySheetShown += self.__onPropertySheetShown
            self.__ctx.events.onItemSelected += self.__onCarouselItemSelected
            self.__ctx.events.onItemUnselected += self.__onCarouselItemUnselected
            self.__ctx.events.onItemInstalled += self.__onItemInstalled
            self.__ctx.events.onItemsRemoved += self.__onItemsRemoved
            self.__ctx.events.onChangesCanceled += self.__onChangesCanceled
            self.__ctx.events.onSeasonChanged += self.__onSeasonChanged
            self.__ctx.events.onAnchorHovered += self.__onAnchorHovered
            self.__ctx.events.onAnchorUnhovered += self.__onAnchorUnhovered
            g_currentVehicle.onChangeStarted += self.__onVehicleChangeStarted
            g_currentVehicle.onChanged += self.__onVehicleChanged
            self.__settingsCore.interfaceScale.onScaleExactlyChanged += self.__onInterfaceScaleChanged
            self.__subscribeToAppearanceChange()
            self.__setCollisions()
        return

    def stopUpdater(self):
        if self.__vehicleCustomizationAnchors is not None:
            self.__resetCollisions()
            self.__unsubscribeFromAppearanceChange()
            self.__ctx.events.onPropertySheetHidden -= self.__onPropertySheetHidden
            self.__ctx.events.onPropertySheetShown -= self.__onPropertySheetShown
            self.__ctx.events.onItemSelected -= self.__onCarouselItemSelected
            self.__ctx.events.onItemUnselected -= self.__onCarouselItemUnselected
            self.__ctx.events.onItemInstalled -= self.__onItemInstalled
            self.__ctx.events.onItemsRemoved -= self.__onItemsRemoved
            self.__ctx.events.onChangesCanceled -= self.__onChangesCanceled
            self.__ctx.events.onSeasonChanged -= self.__onSeasonChanged
            self.__ctx.events.onAnchorHovered -= self.__onAnchorHovered
            self.__ctx.events.onAnchorUnhovered -= self.__onAnchorUnhovered
            g_currentVehicle.onChangeStarted -= self.__onVehicleChangeStarted
            g_currentVehicle.onChanged -= self.__onVehicleChanged
            self.__settingsCore.interfaceScale.onScaleExactlyChanged -= self.__onInterfaceScaleChanged
            self.__delAllAnchors()
            self.__vehicleCustomizationAnchors = None
        return

    def setAnchors(self, displayObjects):
        if self.__vehicleCustomizationAnchors is None:
            _logger.error('Missing WGVehicleCustomizationAnchors.')
            return
        else:
            self.__delAllAnchors()
            modeId = self.__ctx.modeId
            tabId = self.__ctx.mode.tabId
            styleSlot = C11nId(areaId=Area.MISC, slotType=GUI_ITEM_TYPE.STYLE, regionIdx=0)
            styleAnchorParams = self.__ctx.mode.getAnchorParams(styleSlot)
            for displayObject in displayObjects:
                if not hasattr(displayObject, 'slotData'):
                    _logger.error('Incorrect anchor displayObject. Missing slotData section. %s', displayObject)
                    continue
                slotData = displayObject.slotData
                slotId = C11nId(areaId=slotData.slotId.areaId, slotType=slotData.slotId.slotType, regionIdx=slotData.slotId.regionIdx)
                anchorParams = self.__ctx.mode.getAnchorParams(slotId)
                if anchorParams is None:
                    _logger.error('Failed to get anchor params for slotId: %s', slotId)
                    continue
                if modeId == CustomizationModes.EDITABLE_STYLE and slotId.slotType in EDITABLE_STYLE_APPLY_TO_ALL_AREAS_TYPES:
                    location = styleAnchorParams.location
                else:
                    location = anchorParams.location
                linesPosition = copy(location.position)
                slotWidth = 0.0
                if tabId in (CustomizationTabs.EMBLEMS, CustomizationTabs.INSCRIPTIONS):
                    slotWidth = anchorParams.descriptor.size
                    slotHeight = slotWidth * SLOT_ASPECT_RATIO[slotId.slotType]
                    linesShift = slotHeight * _LINES_SHIFT
                    linesPosition -= location.up * linesShift
                position = location.position
                direction = location.normal
                uid = self.__vehicleCustomizationAnchors.addAnchor(position, direction, linesPosition, slotWidth, displayObject, True, True, False, True)
                anchor = Anchor(slotId, uid, position, direction)
                if slotId.slotType == GUI_ITEM_TYPE.PROJECTION_DECAL:
                    self.__closeGroups.add(slotId)
                    for aId, a in self.__processedAnchors.iteritems():
                        dist = (a.position - anchor.position).length
                        if dist < _MIN_PROJECTION_DECAL_ANCHORS_DIST:
                            self.__closeGroups.union(aId, slotId)

                self.__processedAnchors[slotId] = anchor
                anchor.setup()

            self.__changeAnchorsStates()
            self.__updateAnchorsVisability()
            return

    def updateAnchorPositionAndNormal(self, slotId, position, normal):
        if slotId in self.__processedAnchors:
            anchor = self.__processedAnchors[slotId]
            self.__vehicleCustomizationAnchors.updateAnchorPositionAndNormal(anchor.uid, position, normal)

    def setAnchorShift(self, slotId, shift):
        if slotId in self.__processedAnchors:
            anchor = self.__processedAnchors[slotId]
            self.__vehicleCustomizationAnchors.setAnchorShift(anchor.uid, shift)

    def changeAnchorParams(self, slotId, isDisplayed, isAutoScalable, isCollidable=False, isActive=True):
        if slotId in self.__processedAnchors:
            anchor = self.__processedAnchors[slotId]
            self.__vehicleCustomizationAnchors.changeAnchorParams(anchor.uid, isDisplayed, isAutoScalable, isCollidable, isActive)

    def setMenuParams(self, menuDisplayObject, menuWidth, menuHeight, menuCenterX, menuCenterY):
        self.__vehicleCustomizationAnchors.setMenuParams(menuDisplayObject, menuWidth, menuHeight, menuCenterX, menuCenterY)

    def displayMenu(self, display):
        self.__vehicleCustomizationAnchors.displayMenu(display)

    def displayLine(self, display):
        self.__vehicleCustomizationAnchors.displayLine(display)

    def attachMenuToAnchor(self, slotId):
        if slotId in self.__processedAnchors:
            anchor = self.__processedAnchors[slotId]
            self.__vehicleCustomizationAnchors.attachMenuToAnchor(anchor.uid)

    def setMainView(self, displayObject):
        return self.__vehicleCustomizationAnchors.setMainView(displayObject)

    def hideAllAnchors(self):
        if self.__vehicleCustomizationAnchors is not None:
            for slotId in self.__processedAnchors:
                self.changeAnchorParams(slotId, isDisplayed=False, isAutoScalable=False)

        return

    def registerInscriptionController(self, inscriptionController, inputLines):
        self.__vehicleCustomizationAnchors.registerInscriptionController(inscriptionController, inputLines)

    def __delAllAnchors(self):
        if self.__vehicleCustomizationAnchors is not None:
            for anchor in self.__processedAnchors.itervalues():
                self.__vehicleCustomizationAnchors.delAnchor(anchor.uid)
                anchor.destroy()

            self.__processedAnchors.clear()
            self.__closeGroups.clear()
        return

    def __updateAnchorsVisability(self):
        if self.__ctx.mode.isRegion:
            self.__updateRegionsAnchorsVisability()
        elif self.__ctx.mode.tabId in (CustomizationTabs.EMBLEMS, CustomizationTabs.INSCRIPTIONS):
            self.__updateDecalAnchorsVisability()
        elif self.__ctx.mode.tabId == CustomizationTabs.PROJECTION_DECALS:
            self.__updateProjectionDecalAnchorsVisability()

    def __updateRegionsAnchorsVisability(self):
        outfit = self.__ctx.mode.currentOutfit
        for slotId in self.__processedAnchors:
            isDisplayed = isSlotFilled(outfit, slotId)
            isAutoScalable = self.__menuSlotId != slotId
            self.changeAnchorParams(slotId, isDisplayed=isDisplayed, isAutoScalable=isAutoScalable)

    def __updateDecalAnchorsVisability(self):
        for slotId in self.__processedAnchors:
            isDisplayed = slotId != self.__menuSlotId
            self.changeAnchorParams(slotId, isDisplayed=isDisplayed, isAutoScalable=True)

    def __updateProjectionDecalAnchorsVisability(self):
        formfactor = None
        item = self.__ctx.mode.selectedItem
        if item is not None:
            formfactor = item.formfactor
        visibleAnchors = defaultdict(set)
        outfit = self.__ctx.mode.currentOutfit
        for slotId in self.__processedAnchors:
            if isSlotFilled(outfit, slotId):
                isDisplayed = self.__menuSlotId != slotId
                self.changeAnchorParams(slotId, isDisplayed=isDisplayed, isAutoScalable=True)
                root = self.__closeGroups.find(slotId)
                if root is not None:
                    visibleAnchors[root].add(slotId)
                continue
            if formfactor is not None:
                anchor = g_currentVehicle.item.getAnchorBySlotId(slotId.slotType, slotId.areaId, slotId.regionIdx)
                if anchor.isFitForFormfactor(formfactor):
                    self.changeAnchorParams(slotId, isDisplayed=True, isAutoScalable=True, isCollidable=True)
                    root = self.__closeGroups.find(slotId)
                    if root is not None:
                        visibleAnchors[root].add(slotId)
                    continue
            self.changeAnchorParams(slotId, isDisplayed=False, isAutoScalable=False)

        self.__spreadAnchorsApart(visibleAnchors)
        return

    def __spreadAnchorsApart(self, visibleAnchors):
        for slotIds in visibleAnchors.itervalues():
            anchorsCount = len(slotIds)
            if anchorsCount > 1:
                radius = _MIN_PROJECTION_DECAL_ANCHORS_DIST * 0.5 / math.sin(math.pi / anchorsCount)
                position = sum((self.__processedAnchors[slotId].position for slotId in slotIds), Vector3()) / anchorsCount
                direction = sum((self.__processedAnchors[slotId].direction for slotId in slotIds), Vector3()) / anchorsCount
                transformMatrix = Math.Matrix()
                transformMatrix.lookAt(position, direction, (0, 1, 0))
                transformMatrix.invert()
                shift = Vector3(0, radius, 0)
                angle = 2 * math.pi / anchorsCount
                rotor = Math.Matrix()
                rotor.setRotateZ(angle)
                for slotId in sorted(slotIds, key=getProjectionSlotFormfactor):
                    anchor = self.__processedAnchors[slotId]
                    newPosition = transformMatrix.applyPoint(shift)
                    anchor.setShift(newPosition - anchor.position)
                    self.setAnchorShift(slotId, anchor.shift)
                    shift = rotor.applyPoint(shift)

            slotId = slotIds.pop()
            self.setAnchorShift(slotId, Vector3())

    def __onPropertySheetHidden(self):
        self.__menuSlotId = None
        self.__updateAnchorsVisability()
        return

    def __onPropertySheetShown(self, slotId):
        self.__menuSlotId = slotId
        self.__updateAnchorsVisability()

    def __onCarouselItemSelected(self, *_, **__):
        if self.__ctx.mode.tabId == CustomizationTabs.PROJECTION_DECALS:
            self.__updateAnchorsVisability()

    def __onCarouselItemUnselected(self, *_, **__):
        if self.__ctx.mode.tabId == CustomizationTabs.PROJECTION_DECALS:
            for anchor in self.__processedAnchors.itervalues():
                anchor.state.onItemUnselected()

            self.__changeAnchorsStates()
            self.__updateAnchorsVisability()

    def __onItemInstalled(self, item, slotId, season, component):
        anchor = self.__processedAnchors.get(slotId)
        if anchor is not None:
            anchor.state.onItemInstalled()
        outfit = self.__ctx.mode.currentOutfit
        if isItemsQuantityLimitReached(outfit, slotId.slotType):
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

    def __onAnchorHovered(self, slotId):
        if self.__ctx.mode.tabId != CustomizationTabs.PROJECTION_DECALS:
            return
        elif self.__ctx.mode.selectedItem is None:
            return
        else:
            anchor = self.__processedAnchors.get(slotId)
            if anchor is not None:
                item = self.__ctx.mode.getItemFromSlot(slotId)
                if item is not None and item.intCD == self.__ctx.mode.selectedItem.intCD:
                    return
                anchor.state.onHovered()
            self.__changeAnchorsStates()
            return

    def __onAnchorUnhovered(self, slotId):
        if self.__ctx.mode.tabId != CustomizationTabs.PROJECTION_DECALS:
            return
        elif self.__ctx.mode.selectedItem is None:
            return
        else:
            anchor = self.__processedAnchors.get(slotId)
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

    def onCameraLocated(self, locatedSlotId=None):
        for slotId, anchor in self.__processedAnchors.iteritems():
            if slotId == locatedSlotId:
                anchor.state.onSelected()
            anchor.state.onUnselected()

        self.__changeAnchorsStates()

    def getAnchorState(self, slotId):
        if slotId in self.__processedAnchors:
            anchor = self.__processedAnchors[slotId]
            return anchor.stateID

    def __changeAnchorsStates(self):
        if self.__changedStates:
            self.__ctx.events.onAnchorsStateChanged(self.__changedStates)
            self.__changedStates.clear()

    def __onInterfaceScaleChanged(self, scale):
        self.__vehicleCustomizationAnchors.setInterfaceScale(scale)

    def getProcessedAnchor(self, slotId):
        return self.__processedAnchors[slotId] if slotId in self.__processedAnchors else None

    def __subscribeToAppearanceChange(self):
        appearance = self.__hangarSpace.getVehicleEntityAppearance()
        if appearance is not None:
            appearance.loadState.subscribe(self.__onVehicleLoadFinished, self.__onVehicleLoadStarted)
        else:
            _logger.error('Missing vehicle appearance.')
        return

    def __unsubscribeFromAppearanceChange(self):
        appearance = self.__hangarSpace.getVehicleEntityAppearance()
        if appearance is not None:
            appearance.loadState.unsubscribe(self.__onVehicleLoadFinished, self.__onVehicleLoadStarted)
        else:
            _logger.info('Missing vehicle appearance.')
        return

    def __onVehicleChangeStarted(self):
        self.__resetCollisions()
        self.__unsubscribeFromAppearanceChange()

    def __onVehicleChanged(self):
        self.__subscribeToAppearanceChange()
        self.__setCollisions()

    def __onVehicleLoadStarted(self):
        self.__resetCollisions()

    def __onVehicleLoadFinished(self):
        self.__setCollisions()

    def __setCollisions(self):
        if self.__vehicleCustomizationAnchors is None:
            _logger.error('Missing WGVehicleCustomizationAnchors.')
            return
        else:
            appearance = self.__hangarSpace.getVehicleEntityAppearance()
            if appearance is None:
                _logger.error('Missing vehicle appearance.')
                return
            if appearance.isLoaded():
                collisions = appearance.collisions
                if collisions is not None:
                    self.__vehicleCustomizationAnchors.setCollisions(collisions)
                else:
                    _logger.error('Missing vehicle collisions.')
            return

    def __resetCollisions(self):
        if self.__vehicleCustomizationAnchors is not None:
            self.__vehicleCustomizationAnchors.resetCollisions()
        else:
            _logger.error('Missing WGVehicleCustomizationAnchors.')
        return


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
