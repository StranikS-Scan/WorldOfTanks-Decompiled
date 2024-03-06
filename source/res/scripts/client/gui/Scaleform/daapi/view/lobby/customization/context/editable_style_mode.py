# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/context/editable_style_mode.py
import logging
import typing
from functools import partial
from CurrentVehicle import g_currentVehicle
from adisp import adisp_process, adisp_async
from gui.shared.gui_items.processors.common import OutfitApplier, CustomizationsSeller
from gui.Scaleform.daapi.view.lobby.customization.context.custom_mode import CustomMode
from gui.Scaleform.daapi.view.lobby.customization.context.styled_mode import StyledMode
from gui.Scaleform.daapi.view.lobby.customization import shared
from gui.Scaleform.daapi.view.lobby.customization.shared import CustomizationTabs, customizationSlotIdToUid, CustomizationSlotUpdateVO, getStylePurchaseItems, correctSlot, getCurrentVehicleAvailableRegionsMap, fitOutfit, removeItemFromEditableStyle, getEditableStyleOutfitDiff, getItemInventoryCount, getOutfitWithoutItemsNoDiff, getOutfitWithoutItems, ITEM_TYPE_TO_SLOT_TYPE, removeUnselectedItemsFromEditableStyle, getUnsuitableDependentData, changePartsOutfit
from gui.customization.constants import CustomizationModes
from gui.customization.shared import PurchaseItem, getAvailableRegions, EDITABLE_STYLE_IRREMOVABLE_TYPES, EDITABLE_STYLE_APPLY_TO_ALL_AREAS_TYPES, C11nId
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils.decorators import adisp_process as wrapperdProcess
from items import makeIntCompactDescrByID
from items.components.c11n_constants import SeasonType, MAX_USERS_PROJECTION_DECALS, CustomizationType
from vehicle_outfit.containers import SlotData
from vehicle_outfit.outfit import Area, Outfit
from helpers import dependency
from account_helpers.settings_core.settings_constants import OnceOnlyHints
from skeletons.account_helpers.settings_core import ISettingsCore
from tutorial.hints_manager import HINT_SHOWN_STATUS
from items.customizations import CustomizationOutfit
if typing.TYPE_CHECKING:
    from items.customizations import SerializableComponent
    from gui.hangar_vehicle_appearance import AnchorParams
    from gui.shared.gui_items.customization.c11n_items import Customization
    from gui.Scaleform.daapi.view.lobby.customization.context.context import CustomizationContext
_logger = logging.getLogger(__name__)

class EditableStyleMode(CustomMode):
    modeId = CustomizationModes.EDITABLE_STYLE
    _tabs = CustomizationTabs.MODES[modeId]
    _settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, ctx):
        super(EditableStyleMode, self).__init__(ctx)
        self.__style = None
        self.__baseOutfits = {}
        self.__isCanceled = False
        return

    @property
    def style(self):
        return self.__style

    @property
    def baseOutfits(self):
        return self.__baseOutfits

    def getPurchaseItems(self):
        purchaseItems = getStylePurchaseItems(self.__style, self.getModifiedOutfits(), progressionLevel=self.getStyleProgressionLevel())
        return purchaseItems

    def getDependenciesData(self):
        return self.style.getDependenciesIntCDs()

    def changeCamouflageColor(self, slotId, paletteIdx):
        super(EditableStyleMode, self).changeCamouflageColor(slotId, paletteIdx)
        slotData = self.getSlotDataFromSlot(slotId)
        if slotData is not None:
            self.installItemToAllTankAreas(self.season, slotId.slotType, slotData)
        return

    def changeCamouflageScale(self, slotId, scale):
        super(EditableStyleMode, self).changeCamouflageScale(slotId, scale)
        slotData = self.getSlotDataFromSlot(slotId)
        if slotData is not None:
            self.installItemToAllTankAreas(self.season, slotId.slotType, slotData)
        return

    def getAnchorParams(self, slotId):
        if slotId.slotType in EDITABLE_STYLE_APPLY_TO_ALL_AREAS_TYPES:
            slotId = StyledMode.STYLE_SLOT
        return super(EditableStyleMode, self).getAnchorParams(slotId)

    def getSlotDataFromSlot(self, slotId, season=None):
        season = season or self.season
        slotId = correctSlot(slotId)
        outfit = self._modifiedOutfits[season]
        return shared.getSlotDataFromSlot(outfit, slotId)

    def getSlotDataFromBaseOutfit(self, slotId, season=None):
        season = season or self.season
        baseOutfit = self.__baseOutfits[season]
        baseSlotData = shared.getSlotDataFromSlot(baseOutfit, slotId)
        return baseSlotData

    def getItemFromSlot(self, slotId, season=None):
        season = season or self.season
        slotId = correctSlot(slotId)
        outfit = self._modifiedOutfits[season]
        return shared.getItemFromSlot(outfit, slotId)

    def getComponentFromSlot(self, slotId, season=None):
        season = season or self.season
        slotId = correctSlot(slotId)
        outfit = self._modifiedOutfits[season]
        return shared.getComponentFromSlot(outfit, slotId)

    def isBaseItem(self, slotId, season=None):
        season = season or self.season
        baseSlotData = self.getSlotDataFromBaseOutfit(slotId, season)
        outfit = self._modifiedOutfits[season]
        slotData = shared.getSlotDataFromSlot(outfit, slotId)
        return baseSlotData.intCD == slotData.intCD

    def isPossibleToInstallItemForAllSeasons(self, slotId, intCD):
        item = self._service.getItemByCD(intCD)
        if item.itemTypeID in EDITABLE_STYLE_IRREMOVABLE_TYPES:
            if self.isBaseItem(slotId):
                firstSeason, otherSeasons = SeasonType.COMMON_SEASONS[0], SeasonType.COMMON_SEASONS[1:]
                baseSlotData = self.getSlotDataFromBaseOutfit(slotId, firstSeason)
                for season in otherSeasons:
                    slotData = self.getSlotDataFromBaseOutfit(slotId, season)
                    if baseSlotData.intCD != slotData.intCD:
                        return False

                return True
        result = super(EditableStyleMode, self).isPossibleToInstallItemForAllSeasons(slotId, intCD)
        return result

    def installItemToAllSeasons(self, slotId, slotData):
        additionallyAppliedItems = 0
        installToAllAreas = slotId.slotType in EDITABLE_STYLE_APPLY_TO_ALL_AREAS_TYPES
        item = self._service.getItemByCD(slotData.intCD)
        itemTypeID = item.itemTypeID
        itemID = item.id
        for season in SeasonType.COMMON_SEASONS:
            otherSlotData = self.getSlotDataFromSlot(slotId, season)
            df = slotData.weakDiff(otherSlotData)
            if not otherSlotData.intCD or df.intCD:
                self.__processDependentTypes(itemTypeID, itemID, season)
                if installToAllAreas:
                    res = self.__installItemToAllAreas(item, season)
                else:
                    res = self.installItem(intCD=slotData.intCD, slotId=slotId, season=season, component=slotData.component)
                if res:
                    additionallyAppliedItems += 1

        return additionallyAppliedItems

    def getItemInventoryCount(self, item, excludeBase=False):
        baseCount = 0
        appliedCount = 0
        for season in SeasonType.COMMON_SEASONS:
            baseOutfit = self.__baseOutfits[season]
            modifiedOutfit = self._modifiedOutfits[season]
            bCount = baseOutfit.itemsCounter[item.intCD]
            aCount = modifiedOutfit.itemsCounter[item.intCD]
            if item.itemTypeID in EDITABLE_STYLE_APPLY_TO_ALL_AREAS_TYPES:
                bCount = min(1, bCount)
                aCount = min(1, aCount)
            baseCount += bCount
            appliedCount += aCount

        if baseCount:
            inventoryCount = getItemInventoryCount(item)
        else:
            inventoryCount = super(EditableStyleMode, self).getItemInventoryCount(item, excludeBase)
        if excludeBase:
            return inventoryCount
        if item.isStyleOnly:
            slotType = ITEM_TYPE_TO_SLOT_TYPE[item.itemTypeID]
            if slotType in EDITABLE_STYLE_APPLY_TO_ALL_AREAS_TYPES:
                availableCount = any((getAvailableRegions(areaId, slotType) for areaId in Area.ALL))
            else:
                availableCount = sum((len(getAvailableRegions(areaId, slotType)) for areaId in Area.ALL))
            if slotType == GUI_ITEM_TYPE.PROJECTION_DECAL:
                availableCount = min(availableCount, MAX_USERS_PROJECTION_DECALS)
            suitableSeasons = tuple((season for season in SeasonType.COMMON_SEASONS if item.season & season))
            availableCount *= len(suitableSeasons)
            actualInventoryCount = availableCount - appliedCount + inventoryCount
        else:
            actualInventoryCount = max(baseCount - appliedCount, 0) + inventoryCount
        return max(actualInventoryCount, 0)

    def clearStyle(self):
        diffs = {season:None for season in SeasonType.COMMON_SEASONS}
        self._ctx.stylesDiffsCache.saveDiffs(self.__style, diffs)
        vehicleCD = g_currentVehicle.item.descriptor.makeCompactDescr()
        for season in SeasonType.COMMON_SEASONS:
            outfit = self.__style.getOutfit(season, vehicleCD=vehicleCD)
            self._modifiedOutfits[season] = outfit.copy()

        self._fitOutfits(modifiedOnly=True)
        self._ctx.refreshOutfit()
        self._ctx.events.onItemsRemoved()

    def getStyleProgressionLevel(self):
        return self._modifiedOutfits[self.season].progressionLevel if self.__style and self.__style.isProgressive else -1

    def _onStart(self):
        if self._ctx.modeId != CustomizationModes.STYLED:
            _logger.error('Failed to start Style Edit Mode. Style Edit Mode could be started only from Styled mode.')
            self._ctx.changeMode(CustomizationModes.STYLED)
            return
        outfit = self._ctx.mode.currentOutfit
        if not outfit.id:
            _logger.error('Failed to start Style Edit Mode. No applied style.')
            self._ctx.changeMode(CustomizationModes.STYLED)
            return
        style = self._service.getItemByID(GUI_ITEM_TYPE.STYLE, outfit.id)
        if not style.isEditable:
            _logger.error('Failed to start Style Edit Mode. Applied style is not editable.')
            self._ctx.changeMode(CustomizationModes.STYLED)
            return
        self._isInited = False
        self.__style = style
        self.__isCanceled = False
        vehicleCD = g_currentVehicle.item.descriptor.makeCompactDescr()
        availableRegionsMap = getCurrentVehicleAvailableRegionsMap()
        for season in SeasonType.COMMON_SEASONS:
            baseOutfit = self.__style.getOutfit(season, vehicleCD)
            fitOutfit(baseOutfit, availableRegionsMap)
            self.__baseOutfits[season] = baseOutfit

        serverSettings = self._settingsCore.serverSettings
        if style.isProgressionRequired:
            hintShown = bool(serverSettings.getOnceOnlyHintsSetting(OnceOnlyHints.C11N_PROGRESSION_REQUIRED_STYLE_SLOT_BUTTON_HINT))
            if not hintShown:
                serverSettings.setOnceOnlyHintsSettings({OnceOnlyHints.C11N_PROGRESSION_REQUIRED_STYLE_SLOT_HINT: HINT_SHOWN_STATUS,
                 OnceOnlyHints.C11N_PROGRESSION_REQUIRED_STYLE_SLOT_BUTTON_HINT: HINT_SHOWN_STATUS,
                 OnceOnlyHints.C11N_EDITABLE_STYLE_SLOT_HINT: HINT_SHOWN_STATUS,
                 OnceOnlyHints.C11N_EDITABLE_STYLE_SLOT_BUTTON_HINT: HINT_SHOWN_STATUS})
        else:
            hintShown = bool(serverSettings.getOnceOnlyHintsSetting(OnceOnlyHints.C11N_EDITABLE_STYLE_SLOT_BUTTON_HINT))
            if not hintShown:
                serverSettings.setOnceOnlyHintsSettings({OnceOnlyHints.C11N_EDITABLE_STYLE_SLOT_HINT: HINT_SHOWN_STATUS,
                 OnceOnlyHints.C11N_EDITABLE_STYLE_SLOT_BUTTON_HINT: HINT_SHOWN_STATUS})
        super(EditableStyleMode, self)._onStart()

    def _onStop(self):
        if not self.__isCanceled:
            diffs = {}
            for season in SeasonType.COMMON_SEASONS:
                outfit = self._modifiedOutfits[season]
                baseOutfit = self.__baseOutfits[season]
                diffs[season] = getEditableStyleOutfitDiff(outfit, baseOutfit)

            self._ctx.stylesDiffsCache.saveDiffs(self.__style, diffs)
        super(EditableStyleMode, self)._onStop()

    def _cancelChanges(self):
        super(EditableStyleMode, self)._cancelChanges()
        self.__isCanceled = True

    @adisp_async
    @adisp_process
    def _applyItems(self, purchaseItems, isModeChanged, callback):
        results = []
        vehicleCD = g_currentVehicle.item.descriptor.makeCompactDescr()
        modifiedOutfits = {season:outfit.copy() for season, outfit in self._modifiedOutfits.iteritems()}
        originalOutfits = self._ctx.startMode.getOriginalOutfits()
        removeUnselectedItemsFromEditableStyle(modifiedOutfits, self.__baseOutfits, purchaseItems)
        requestData = []
        for season in SeasonType.COMMON_SEASONS:
            outfit = modifiedOutfits[season]
            baseOutfit = self.__baseOutfits[season]
            if outfit.vehicleCD != baseOutfit.vehicleCD or not outfit.isEqual(baseOutfit):
                diff = getEditableStyleOutfitDiff(outfit, baseOutfit)
                outfit = self.__style.getOutfit(season, vehicleCD=vehicleCD, diff=diff)
                requestData.append((outfit, season))

        if not requestData:
            emptyComponent = CustomizationOutfit()
            outfit = self._modifiedOutfits[self.season]
            emptyComponent.styleId = outfit.id
            if outfit.style is not None and outfit.style.isProgressionRewindEnabled:
                emptyComponent.styleProgressionLevel = outfit.progressionLevel
            if outfit.style is not None and outfit.style.isWithSerialNumber:
                emptyComponent.serial_number = outfit.serialNumber
            outfit = Outfit(component=emptyComponent)
            requestData.append((outfit, SeasonType.ALL))
        result = yield OutfitApplier(g_currentVehicle.item, requestData).request()
        results.append(result)
        if self.isInited:
            self._events.onItemsBought(originalOutfits, purchaseItems, results)
        callback(self)
        return

    def _fillOutfits(self):
        originalOutfits = self._ctx.mode.getOriginalOutfits()
        modifiedOutfits = self._ctx.mode.getModifiedOutfits()
        self._originalOutfits = originalOutfits
        self._modifiedOutfits = modifiedOutfits

    def _installItem(self, intCD, slotId, season=None, component=None):
        if component is None:
            baseSlotData = self.getSlotDataFromBaseOutfit(slotId, season)
            if baseSlotData is not None and baseSlotData.intCD == intCD:
                component = baseSlotData.component.copy()
        season = season or self.season
        slotData = self.getSlotDataFromSlot(slotId, season)
        self._modifiedOutfits[season] = changePartsOutfit(season, self._modifiedOutfits[season], intCD, slotData.intCD)
        return super(EditableStyleMode, self)._installItem(intCD, slotId, season, component)

    def _selectItem(self, intCD, progressionLevel=0):
        item = self._service.getItemByCD(intCD)
        selItemTypeID = item.itemTypeID
        self.__processDependentTypes(selItemTypeID, item.id, self.season)
        if selItemTypeID in EDITABLE_STYLE_APPLY_TO_ALL_AREAS_TYPES:
            slotId = EDITABLE_STYLE_APPLY_TO_ALL_AREAS_TYPES[selItemTypeID]
            slotData = self.getSlotDataFromSlot(slotId)
            if slotData is None or slotData.intCD != intCD:
                self.__installItemToAllAreas(item)
            slotData = self.getSlotDataFromSlot(slotId)
            if slotData is not None and not slotData.isEmpty():
                self.selectSlot(slotId)
            return False
        else:
            if selItemTypeID == GUI_ITEM_TYPE.PROJECTION_DECAL:
                ancors = self.getAnchorVOs()
                if len(ancors) == 1 and ancors[0] is not None:
                    slotId = C11nId(**ancors[0]['slotId'])
                    self.installItem(intCD, slotId)
                    self.selectSlot(slotId)
                    return False
            result = super(EditableStyleMode, self)._selectItem(intCD, progressionLevel)
            return result

    def _iterOutfitsWithoutItem(self, item, count):
        season = g_currentVehicle.item.getAnyOutfitSeason()
        isMountedStyleSelected = g_currentVehicle.item.getOutfit(season).id == self.__style.id
        if isMountedStyleSelected:
            iterOutfitsWithoutItem = partial(getOutfitWithoutItems, self.getOutfitsInfo(), item.intCD, count)
        else:
            outfits = {season:outfit for season, outfit in g_currentVehicle.item.outfits.iteritems()}
            iterOutfitsWithoutItem = partial(getOutfitWithoutItemsNoDiff, outfits, item.intCD, count)
        vehicleCD = g_currentVehicle.item.descriptor.makeCompactDescr()
        for season, outfit in iterOutfitsWithoutItem():
            if isMountedStyleSelected:
                baseOutfit = self.__baseOutfits[season]
                diff = getEditableStyleOutfitDiff(outfit, baseOutfit)
                outfit = self.__style.getOutfit(season, vehicleCD=vehicleCD, diff=diff)
            yield (season, outfit)

    @adisp_async
    @wrapperdProcess('sellItem')
    def _sellItem(self, item, count, callback):
        if item.fullInventoryCount(g_currentVehicle.item.intCD) < count:
            for season, outfit in self._iterOutfitsWithoutItem(item, count):
                yield OutfitApplier(g_currentVehicle.item, ((outfit, season),)).request()

        result = yield CustomizationsSeller(g_currentVehicle.item, item, count).request()
        callback(result)

    def _selectSlot(self, slotId):
        slotId = correctSlot(slotId)
        result = super(EditableStyleMode, self)._selectSlot(slotId)
        return result

    def _removeItem(self, slotId, season=None):
        season = season or self.season
        outfit = self._modifiedOutfits[season]
        baseOutfit = self.__baseOutfits[season]
        self._modifiedOutfits[season] = removeItemFromEditableStyle(outfit, baseOutfit, slotId, season)

    def _getAnchorVOs(self):
        if self.slotType in EDITABLE_STYLE_APPLY_TO_ALL_AREAS_TYPES:
            slotId = EDITABLE_STYLE_APPLY_TO_ALL_AREAS_TYPES[self.slotType]
            item = self.getItemFromSlot(slotId)
            intCD = item.intCD if item is not None else 0
            uid = customizationSlotIdToUid(slotId)
            anchorVO = CustomizationSlotUpdateVO(slotId=slotId._asdict(), itemIntCD=intCD, uid=uid)
            return [anchorVO._asdict()]
        else:
            return super(EditableStyleMode, self)._getAnchorVOs()

    def _validateItem(self, item, slotId, season):
        errors = []
        if item.isStyleOnly:
            return errors
        else:
            baseSlotData = self.getSlotDataFromBaseOutfit(slotId, season)
            if baseSlotData is not None and baseSlotData.intCD == item.intCD:
                return errors
            errors = super(EditableStyleMode, self)._validateItem(item, slotId, season)
            return errors

    def _onVehicleChangeStarted(self):
        self._ctx.changeMode(CustomizationModes.STYLED)

    def __installItemToAllAreas(self, item, season=None):
        season = season or self.season
        slotId = EDITABLE_STYLE_APPLY_TO_ALL_AREAS_TYPES[item.itemTypeID]
        component = self._getComponent(item, slotId)
        slotData = SlotData(item.intCD, component)
        baseSlotData = self.getSlotDataFromBaseOutfit(slotId, season)
        isBaseItem = baseSlotData is not None and baseSlotData.intCD == item.intCD
        if item.isStyleOnly or isBaseItem or self.isPossibleToInstallToAllTankAreas(item.intCD, item.itemTypeID):
            self.installItemToAllTankAreas(season, slotId.slotType, slotData)
            return True
        else:
            _logger.warning('Failed to apply item: %s to all tank areas', item)
            return False

    def __processDependentTypes(self, selItemTypeID, selItemID, season):
        if selItemTypeID == GUI_ITEM_TYPE.CAMOUFLAGE:
            styleDependencies = self.style.descriptor.dependencies
            camoDependencies = styleDependencies.get(selItemID)
            if camoDependencies:
                currentOutfit = self.getModifiedOutfit(season)
                if not currentOutfit:
                    _logger.error('Could not find outfit for required season "%d"', season)
                    return
                camoDependencies = styleDependencies.get(selItemID, {})
                for uItem, uSlotId in getUnsuitableDependentData(currentOutfit, selItemID, styleDependencies):
                    suitableItemIntCD = self.__getSuitableIntCD(uItem, camoDependencies.get(uItem.descriptor.itemType, tuple()))
                    if suitableItemIntCD is not None:
                        self.installItem(intCD=suitableItemIntCD, slotId=uSlotId, season=season, refresh=False)
                    self.removeItem(uSlotId, season, refresh=False)

        return

    def __getSuitableIntCD(self, unsuitableItem, dependentByType):
        suitableItemIntCD = None
        posUnsuitType = unsuitableItem.descriptor.itemType
        if posUnsuitType == CustomizationType.DECAL:
            originalDecalType = unsuitableItem.descriptor.type
            getItemByCD = self._service.getItemByCD
            for suitableID in dependentByType:
                posiblySuitableIntCD = makeIntCompactDescrByID('customizationItem', posUnsuitType, suitableID)
                suitableItem = getItemByCD(posiblySuitableIntCD)
                if suitableItem.descriptor.type == originalDecalType:
                    suitableItemIntCD = posiblySuitableIntCD
                    break

        else:
            suitableItemIntCD = makeIntCompactDescrByID('customizationItem', posUnsuitType, dependentByType[0])
        return suitableItemIntCD
