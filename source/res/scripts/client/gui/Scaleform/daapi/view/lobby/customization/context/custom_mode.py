# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/context/custom_mode.py
import logging
from copy import copy
import typing
import BigWorld
from CurrentVehicle import g_currentVehicle
from adisp import process, async
from gui.Scaleform.daapi.view.lobby.customization.context.customization_mode import CustomizationMode
from gui.Scaleform.daapi.view.lobby.customization.shared import CustomizationTabs, isNeedToMirrorProjectionDecal, isSlotFilled, isItemsQuantityLimitReached, fitPersonalNumber, formatPersonalNumber, EMPTY_PERSONAL_NUMBER, customizationSlotIdToUid, CustomizationSlotUpdateVO, getCustomPurchaseItems
from gui.Scaleform.daapi.view.lobby.customization.shared import getOutfitWithoutItems
from gui.customization.constants import CustomizationModes
from gui.customization.shared import C11nId, PurchaseItem, getAvailableRegions
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.processors.common import OutfitApplier, CustomizationsSeller
from gui.shared.utils.decorators import process as wrappedProcess
from items.components.c11n_components import isPersonalNumberAllowed
from items.components.c11n_constants import SeasonType, DEFAULT_PALETTE, Options, SLOT_DEFAULT_ALLOWED_MODEL
from items.customizations import CamouflageComponent, ProjectionDecalComponent, PersonalNumberComponent
from vehicle_outfit.containers import emptyComponent
from vehicle_outfit.outfit import Area
if typing.TYPE_CHECKING:
    from items.customizations import SerializableComponent
    from gui.shared.gui_items.customization.c11n_items import Customization
    from vehicle_outfit.outfit import Outfit
    from vehicle_outfit.containers import SlotData
    from gui.Scaleform.daapi.view.lobby.customization.context.context import CustomizationContext
_logger = logging.getLogger(__name__)

class CustomMode(CustomizationMode):
    __SELFINSTALL_ITEM_TYPES = {GUI_ITEM_TYPE.MODIFICATION: C11nId(areaId=Area.MISC, slotType=GUI_ITEM_TYPE.MODIFICATION, regionIdx=0),
     GUI_ITEM_TYPE.STYLE: C11nId(areaId=Area.MISC, slotType=GUI_ITEM_TYPE.STYLE, regionIdx=0)}
    modeId = CustomizationModes.CUSTOM
    _tabs = CustomizationTabs.MODES[modeId]

    def __init__(self, ctx):
        super(CustomMode, self).__init__(ctx)
        self.__editModeEnabled = False
        self.__storedComponent = None
        self.__storedProgressionLevel = 0
        return

    @property
    def storedProgressionLevel(self):
        return self.__storedProgressionLevel

    def removeItemFromAllTankAreas(self, season, slotType):
        for areaId in Area.TANK_PARTS:
            regionsIndexes = getAvailableRegions(areaId, slotType)
            for regionIdx in regionsIndexes:
                slotId = C11nId(areaId=areaId, slotType=slotType, regionIdx=regionIdx)
                self.removeItem(slotId, season, refresh=False)

        self._ctx.refreshOutfit(season)
        self._events.onItemsRemoved()

    def removeItemFromAllSeasons(self, slotId):
        for season in SeasonType.COMMON_SEASONS:
            self.removeItem(slotId, season, refresh=False)
            self._ctx.refreshOutfit(season)

        self._events.onItemsRemoved()

    def removeItems(self, onlyCurrent, *intCDs):

        def intCdFilter(item):
            return item.intCD in intCDs

        if onlyCurrent:
            self.removeItemsFromSeason(filterMethod=intCdFilter, refresh=False)
            self._ctx.refreshOutfit()
        else:
            for season in SeasonType.COMMON_SEASONS:
                self.removeItemsFromSeason(season, filterMethod=intCdFilter, refresh=False)
                self._ctx.refreshOutfit(season)

        self._events.onItemsRemoved()

    def installItemToAllTankAreas(self, season, slotType, slotData):
        additionallyAppliedItems = 0
        for areaId in Area.TANK_PARTS:
            regionsIndexes = getAvailableRegions(areaId, slotType)
            multiSlot = self._modifiedOutfits[season].getContainer(areaId).slotFor(slotType)
            for regionIdx in regionsIndexes:
                otherSlotData = multiSlot.getSlotData(regionIdx)
                df = slotData.weakDiff(otherSlotData)
                if not otherSlotData.intCD or df.intCD:
                    slotId = C11nId(areaId=areaId, slotType=slotType, regionIdx=regionIdx)
                    res = self.installItem(intCD=slotData.intCD, slotId=slotId, season=season, component=slotData.component)
                    if res:
                        additionallyAppliedItems += 1

        return additionallyAppliedItems

    def installItemToAllSeasons(self, slotId, slotData):
        additionallyAppliedItems = 0
        for season in SeasonType.COMMON_SEASONS:
            otherSlotData = self.getSlotDataFromSlot(slotId, season)
            df = slotData.weakDiff(otherSlotData)
            if not otherSlotData.intCD or df.intCD:
                self.installItem(intCD=slotData.intCD, slotId=slotId, season=season, component=slotData.component)
                additionallyAppliedItems += 1

        return additionallyAppliedItems

    def isPossibleToInstallToAllTankAreas(self, intCD, slotType):
        item = self._service.getItemByCD(intCD)
        if not item.isLimited and not item.isHidden or item.isStyleOnly:
            return True
        needed = 0
        for areaId in Area.TANK_PARTS:
            regionsIndexes = getAvailableRegions(areaId, slotType)
            multiSlot = self.currentOutfit.getContainer(areaId).slotFor(slotType)
            for regionIdx in regionsIndexes:
                otehrIntCD = multiSlot.getItemCD(regionIdx)
                if intCD != otehrIntCD:
                    needed += 1

        inventoryCount = self.getItemInventoryCount(item)
        toBye = needed - inventoryCount
        return toBye <= item.buyCount

    def isPossibleToInstallItemForAllSeasons(self, slotId, intCD):
        item = self._service.getItemByCD(intCD)
        if item.season != SeasonType.ALL:
            return False
        if not item.isLimited and not item.isHidden or item.isStyleOnly:
            return True
        needed = 0
        for season in SeasonType.COMMON_SEASONS:
            outfit = self.getModifiedOutfit(season)
            otherIntCD = outfit.getContainer(slotId.areaId).slotFor(slotId.slotType).getItemCD(slotId.regionIdx)
            if intCD != otherIntCD:
                needed += 1

        inventoryCount = self.getItemInventoryCount(item)
        toBye = needed - inventoryCount
        return toBye <= item.buyCount

    def previewItem(self, intCD, slotId):
        if slotId.slotType != GUI_ITEM_TYPE.PROJECTION_DECAL:
            _logger.warning('Preview is not available for itemType: %s', slotId.slotType)
            return
        item = self._service.getItemByCD(intCD)
        component = self._getComponent(item=item, slotId=slotId)
        component.preview = True
        multiSlot = self.currentOutfit.getContainer(slotId.areaId).slotFor(slotId.slotType)
        multiSlot.set(item.intCD, idx=slotId.regionIdx, component=component)
        self._ctx.refreshOutfit()

    def removeItemPreview(self, slotId):
        if slotId.slotType != GUI_ITEM_TYPE.PROJECTION_DECAL:
            _logger.warning('Preview is not available for itemType: %s', slotId.slotType)
            return
        else:
            multiSlot = self.currentOutfit.getContainer(slotId.areaId).slotFor(slotId.slotType)
            component = multiSlot.getComponent(slotId.regionIdx)
            if component is None:
                _logger.warning('Item is not previewed in slotId: %s', slotId)
                return
            if not component.preview:
                return
            multiSlot.remove(idx=slotId.regionIdx)
            self._ctx.refreshOutfit()
            return

    def mirrorDecal(self, slotId, option=Options.NONE):
        if slotId.slotType != GUI_ITEM_TYPE.PROJECTION_DECAL:
            _logger.warning('Mirroring is not available for itemType: %s', slotId.slotType)
            return
        else:
            component = self.getComponentFromSlot(slotId)
            if component is not None:
                component.options ^= option
                self._ctx.refreshOutfit()
                self._events.onComponentChanged(slotId, False)
            return

    def changeCamouflageColor(self, slotId, paletteIdx):
        if slotId.slotType != GUI_ITEM_TYPE.CAMOUFLAGE:
            _logger.warning('Color change is not available for itemType: %s', slotId.slotType)
            return
        else:
            component = self.getComponentFromSlot(slotId)
            if component is not None and component.palette != paletteIdx:
                component.palette = paletteIdx
                self._ctx.refreshOutfit()
                self._events.onComponentChanged(slotId, False)
            return

    def changeCamouflageScale(self, slotId, scale):
        if slotId.slotType != GUI_ITEM_TYPE.CAMOUFLAGE:
            _logger.warning('Scale change is not available for itemType: %s', slotId.slotType)
            return
        else:
            component = self.getComponentFromSlot(slotId)
            if component is not None and component.patternSize != scale:
                component.patternSize = scale
                self._ctx.refreshOutfit()
                self._events.onComponentChanged(slotId, False)
            return

    def changeProjectionDecalScale(self, slotId, scale):
        if slotId.slotType != GUI_ITEM_TYPE.PROJECTION_DECAL:
            _logger.warning('Scale change is not available for itemType: %s', slotId.slotType)
            return
        else:
            component = self.getComponentFromSlot(slotId)
            if component is not None and component.scaleFactorId != scale:
                component.scaleFactorId = scale
                self._ctx.refreshOutfit()
                self._events.onComponentChanged(slotId, False)
            return

    def changeItemProgression(self, slotId, progression):
        component = self.getComponentFromSlot(slotId)
        if hasattr(component, 'progressionLevel'):
            if component.progressionLevel != progression:
                component.progressionLevel = progression
                self._ctx.refreshOutfit()
                self._events.onComponentChanged(slotId, False)
        else:
            _logger.warning('Progression change is not available for itemType: %s', slotId.slotType)
            return

    def getPurchaseItems(self):
        return getCustomPurchaseItems(self._ctx.season, self.getModifiedOutfits())

    def getNotModifiedItems(self, season=None):
        season = season if season is not None else self._ctx.season
        df = self._modifiedOutfits[season].diff(self._originalOutfits[season])
        notModifiedItems = df.diff(self._originalOutfits[self._ctx.season])
        return notModifiedItems

    def enableEditMode(self, enabled):
        if self.__editModeEnabled == enabled:
            return
        self.__editModeEnabled = enabled
        self._events.onEditModeEnabled(self.__editModeEnabled)

    def _fillOutfits(self):
        isInstalled = not self._service.isStyleInstalled()
        for season in SeasonType.COMMON_SEASONS:
            outfit = self._service.getCustomOutfit(season)
            if not isInstalled:
                self._removeHiddenFromOutfit(outfit, g_currentVehicle.item.intCD)
            if outfit is not None:
                self._originalOutfits[season] = outfit.copy()
                self._modifiedOutfits[season] = outfit.copy()
            self._originalOutfits[season] = self._service.getEmptyOutfit()
            self._modifiedOutfits[season] = self._service.getEmptyOutfit()

        return

    def _restoreState(self):
        self._modifiedOutfits = copy(self._state)
        self._state.clear()

    def _selectItem(self, intCD, progressionLevel=0):
        item = self._service.getItemByCD(intCD)
        if item.itemTypeID in self.__SELFINSTALL_ITEM_TYPES:
            slotId = self.__SELFINSTALL_ITEM_TYPES[item.itemTypeID]
            self.selectSlot(slotId)
        if self.selectedSlot is None:
            self._selectedItem = item
            self.__storedProgressionLevel = progressionLevel
            return True
        else:
            self.installItem(intCD, self.selectedSlot)
            return False

    def _unselectItem(self):
        if self._selectedItem is not None:
            self._selectedItem = None
            self.__storedProgressionLevel = 0
            return True
        else:
            return False

    def _selectSlot(self, slotId):
        if self.selectedItem is None:
            self._selectedSlot = slotId
            return True
        else:
            self.installItem(self.selectedItem.intCD, slotId)
            return False

    def _unselectSlot(self):
        if self.selectedSlot is not None:
            self._selectedSlot = None
            return True
        else:
            return False

    def _installItem(self, intCD, slotId, season=None, component=None):
        outfit = self.currentOutfit if season is None else self._modifiedOutfits[season]
        if isItemsQuantityLimitReached(outfit, slotId.slotType) and not isSlotFilled(outfit, slotId):
            return False
        else:
            item = self._service.getItemByCD(intCD)
            component = component or self._getComponent(item, slotId)
            multiSlot = outfit.getContainer(slotId.areaId).slotFor(slotId.slotType)
            multiSlot.set(item.intCD, idx=slotId.regionIdx, component=component)
            return True

    def _removeItem(self, slotId, season=None):
        outfit = self.currentOutfit if season is None else self._modifiedOutfits[season]
        multiSlot = outfit.getContainer(slotId.areaId).slotFor(slotId.slotType)
        multiSlot.remove(slotId.regionIdx)
        return

    @async
    @process
    def _applyItems(self, purchaseItems, isModeChanged, callback):
        modifiedOutfits = {season:outfit.copy() for season, outfit in self._modifiedOutfits.iteritems()}
        for pItem in purchaseItems:
            if not pItem.selected:
                if pItem.slotType:
                    season = pItem.group
                    slot = modifiedOutfits[season].getContainer(pItem.areaID).slotFor(pItem.slotType)
                    slot.remove(pItem.regionIdx)

        if isModeChanged:
            modifiedSeasons = SeasonType.COMMON_SEASONS
        else:
            modifiedSeasons = tuple((season for season in SeasonType.COMMON_SEASONS if not modifiedOutfits[season].isEqual(self._originalOutfits[season])))
        for season in modifiedSeasons:
            emptyOutfit = self._service.getEmptyOutfit()
            yield OutfitApplier(g_currentVehicle.item, emptyOutfit, season).request()

        results = []
        for season in modifiedSeasons:
            outfit = modifiedOutfits[season]
            if outfit.isEmpty():
                continue
            result = yield OutfitApplier(g_currentVehicle.item, outfit, season).request()
            results.append(result)

        if self.isInited:
            self._events.onItemsBought(purchaseItems, results)
        callback(self)

    @wrappedProcess('sellItem')
    def _sellItem(self, item, count):
        if item.fullInventoryCount(g_currentVehicle.item.intCD) < count:
            for season, outfit in getOutfitWithoutItems(self.getOutfitsInfo(), item.intCD, count):
                yield OutfitApplier(g_currentVehicle.item, outfit, season).request()

        yield CustomizationsSeller(g_currentVehicle.item, item, count).request()

    def _isOutfitsEmpty(self):
        for season in SeasonType.COMMON_SEASONS:
            outfit = self._modifiedOutfits[season]
            if not outfit.isEmpty():
                return False

        return True

    def _isOutfitsModified(self):
        for season in SeasonType.COMMON_SEASONS:
            modifiedOutfit = self._modifiedOutfits[season]
            originalOutfit = self._originalOutfits[season]
            for _, component, _, _, _ in originalOutfit.diff(modifiedOutfit).itemsFull():
                if component.isFilled():
                    return True

            for _, component, _, _, _ in modifiedOutfit.diff(originalOutfit).itemsFull():
                if component.isFilled():
                    return True

        return False

    def _getAnchorVOs(self):
        anchorVOs = []
        for areaId in Area.ALL:
            slot = self.currentOutfit.getContainer(areaId).slotFor(self.slotType)
            for regionIdx, anchor in g_currentVehicle.item.getAnchors(self.slotType, areaId):
                if anchor.hiddenForUser:
                    continue
                model = self.currentOutfit.modelsSet or SLOT_DEFAULT_ALLOWED_MODEL
                if model not in anchor.compatibleModels:
                    continue
                slotId = C11nId(areaId, self.slotType, regionIdx)
                intCD = slot.getItemCD(regionIdx)
                uid = customizationSlotIdToUid(slotId)
                anchorVO = CustomizationSlotUpdateVO(slotId=slotId._asdict(), itemIntCD=intCD, uid=uid)
                anchorVOs.append(anchorVO._asdict())

        return anchorVOs

    def _getComponent(self, item, slotId):
        component = self.__getBaseComponent(item, slotId)
        if component.customType == CamouflageComponent.customType:
            self.__configureCamouflageComponent(component)
        elif component.customType == ProjectionDecalComponent.customType:
            self.__configureProjectionDecalComponent(component, item, slotId)
        elif component.customType == PersonalNumberComponent.customType:
            self.__configurePersonalNumberComponent(component, item)
        return component

    def __getBaseComponent(self, item, slotId):
        newComponent = emptyComponent(item.itemTypeID)
        prevItem = self.getItemFromSlot(slotId)
        prevComponent = self.getComponentFromSlot(slotId)
        if prevItem is None:
            return newComponent
        elif prevItem.itemTypeID == item.itemTypeID:
            self.__storedComponent = None
            return prevComponent
        else:
            if self.__storedComponent is not None:
                if self.__storedComponent.customType == newComponent.customType:
                    newComponent = self.__storedComponent
                self.__storedComponent = None
            elif item.itemTypeID == GUI_ITEM_TYPE.INSCRIPTION:
                items = self._ctx.carouselItems
                accidentalSwitch = abs(items.index(prevItem.intCD) - items.index(item.intCD)) == 1
                self.__storedComponent = prevComponent if accidentalSwitch else None
            return newComponent

    def __configureCamouflageComponent(self, component):
        component.palette = DEFAULT_PALETTE

    def __configureProjectionDecalComponent(self, component, item, slotId):
        prevItem = self.getItemFromSlot(slotId)
        self.__configureProjectionDecalComponentMirror(component, item, prevItem, slotId)
        self.__configureProjectionDecalComponentProgression(component, item, prevItem)
        self.__storedProgressionLevel = component.progressionLevel
        component.preview = False

    def __configureProjectionDecalComponentMirror(self, component, item, prevItem, slotId):
        slot = g_currentVehicle.item.getAnchorBySlotId(slotId.slotType, slotId.areaId, slotId.regionIdx)
        canBeMirroredHorizontally = item.canBeMirroredHorizontally
        canBeMirroredVertically = item.canBeMirroredVertically and slot.canBeMirroredVertically
        if not canBeMirroredVertically:
            component.options &= ~Options.MIRRORED_VERTICALLY
        if not canBeMirroredHorizontally:
            component.options &= ~Options.MIRRORED_HORIZONTALLY
            return
        elif prevItem is not None and prevItem.canBeMirroredHorizontally:
            if not item.canBeMirroredHorizontally:
                component.options &= ~Options.MIRRORED_HORIZONTALLY
            elif item.direction != prevItem.direction:
                component.options ^= Options.MIRRORED_HORIZONTALLY
            return
        else:
            if isNeedToMirrorProjectionDecal(item, slot):
                component.options |= Options.MIRRORED_HORIZONTALLY
            return

    def __configureProjectionDecalComponentProgression(self, component, item, prevItem):
        if not item.isProgressive:
            component.progressionLevel = 0
            return
        else:
            achievedLevel = item.getLatestOpenedProgressionLevel(g_currentVehicle.item)
            if achievedLevel == -1:
                _logger.warning('Progressive item: %s for vehicle: %s is locked', item, g_currentVehicle.item)
                component.progressionLevel = 0
                return
            if prevItem is not None and prevItem != item:
                if not prevItem.isProgressive:
                    progressionLevel = 0
                else:
                    prevLevel = component.progressionLevel
                    prevLevel = prevLevel or prevItem.getLatestOpenedProgressionLevel(g_currentVehicle.item)
                    progressionLevel = min(prevLevel, achievedLevel)
            else:
                progressionLevel = min(self.__storedProgressionLevel, achievedLevel)
            if progressionLevel == achievedLevel:
                progressionLevel = 0
            component.progressionLevel = progressionLevel
            return

    def __configurePersonalNumberComponent(self, component, item):
        if not component.number:
            return
        if not self.__editModeEnabled and item.digitsCount != len(component.number):
            number = fitPersonalNumber(component.number, item.digitsCount)
            number = formatPersonalNumber(number, item.digitsCount)
            if isPersonalNumberAllowed(number):
                component.number = number
            else:
                component.number = EMPTY_PERSONAL_NUMBER
                BigWorld.callback(0.0, lambda : self._events.onPersonalNumberCleared(number))
