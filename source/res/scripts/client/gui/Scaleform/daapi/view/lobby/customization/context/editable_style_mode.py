# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/context/editable_style_mode.py
import logging
import typing
from CurrentVehicle import g_currentVehicle
from gui.shared.gui_items.processors.common import OutfitApplier, CustomizationsSeller
from gui.Scaleform.daapi.view.lobby.customization.context.custom_mode import CustomMode
from gui.Scaleform.daapi.view.lobby.customization.context.styled_mode import StyledMode
from gui.Scaleform.daapi.view.lobby.customization import shared
from gui.Scaleform.daapi.view.lobby.customization.shared import CustomizationTabs, customizationSlotIdToUid, CustomizationSlotUpdateVO, getStylePurchaseItems, correctSlot, getCurrentVehicleAvailableRegionsMap, fitOutfit, removeItemFromEditableStyle, getEditableStyleOutfitDiff, getItemInventoryCount, getOutfitWithoutItems, ITEM_TYPE_TO_SLOT_TYPE, removeUnselectedItemsFromEditableStyle
from gui.customization.constants import CustomizationModes
from gui.customization.shared import PurchaseItem, getAvailableRegions, EDITABLE_STYLE_IRREMOVABLE_TYPES, EDITABLE_STYLE_APPLY_TO_ALL_AREAS_TYPES, C11nId
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils.decorators import process
from items.components.c11n_constants import SeasonType, MAX_USERS_PROJECTION_DECALS
from vehicle_outfit.containers import SlotData
from vehicle_outfit.outfit import Area, Outfit
from helpers import dependency
from account_helpers.settings_core.settings_constants import OnceOnlyHints
from skeletons.account_helpers.settings_core import ISettingsCore
from tutorial.hints_manager import HINT_SHOWN_STATUS
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
        return

    @property
    def style(self):
        return self.__style

    @property
    def baseOutfits(self):
        return self.__baseOutfits

    def getPurchaseItems(self):
        purchaseItems = getStylePurchaseItems(self.__style, self.getModifiedOutfits())
        return purchaseItems

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
        for season in SeasonType.COMMON_SEASONS:
            otherSlotData = self.getSlotDataFromSlot(slotId, season)
            df = slotData.weakDiff(otherSlotData)
            if not otherSlotData.intCD or df.intCD:
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
        diffs = {}
        for season in SeasonType.COMMON_SEASONS:
            outfit = self._modifiedOutfits[season]
            baseOutfit = self.__baseOutfits[season]
            diffs[season] = getEditableStyleOutfitDiff(outfit, baseOutfit)

        self._ctx.stylesDiffsCache.saveDiffs(self.__style, diffs)
        super(EditableStyleMode, self)._onStop()

    @process('customizationApply')
    def _applyItems(self, purchaseItems, isModeChanged):
        results = []
        vehicleCD = g_currentVehicle.item.descriptor.makeCompactDescr()
        modifiedOutfits = {season:outfit.copy() for season, outfit in self._modifiedOutfits.iteritems()}
        removeUnselectedItemsFromEditableStyle(modifiedOutfits, self.__baseOutfits, purchaseItems)
        outfit = self._modifiedOutfits[self.season]
        result = yield OutfitApplier(g_currentVehicle.item, outfit, SeasonType.ALL).request()
        results.append(result)
        for season in SeasonType.COMMON_SEASONS:
            outfit = modifiedOutfits[season]
            baseOutfit = self.__baseOutfits[season]
            if not outfit.isEqual(baseOutfit):
                diff = getEditableStyleOutfitDiff(outfit, baseOutfit)
                outfit = self.__style.getOutfit(season, vehicleCD=vehicleCD, diff=diff)
                result = yield OutfitApplier(g_currentVehicle.item, outfit, season).request()
                results.append(result)

        if self.isInited:
            self._events.onItemsBought(purchaseItems, results)

    def _fillOutfits(self):
        isInstalled = self._service.isStyleInstalled()
        vehicleCD = g_currentVehicle.item.descriptor.makeCompactDescr()
        for season in SeasonType.COMMON_SEASONS:
            diff = self._ctx.stylesDiffsCache.getDiff(self.__style, season)
            if not isInstalled and diff is not None:
                diffOutfit = Outfit(strCompactDescr=diff, vehicleCD=vehicleCD)
                self._removeHiddenFromOutfit(diffOutfit, g_currentVehicle.item.intCD)
                diff = diffOutfit.pack().makeCompDescr()
            outfit = self.__style.getOutfit(season, vehicleCD=vehicleCD, diff=diff)
            self._originalOutfits[season] = outfit.copy()
            self._modifiedOutfits[season] = outfit.copy()

        return

    def _installItem(self, intCD, slotId, season=None, component=None):
        if component is None:
            baseSlotData = self.getSlotDataFromBaseOutfit(slotId, season)
            if baseSlotData is not None and baseSlotData.intCD == intCD:
                component = baseSlotData.component.copy()
        return super(EditableStyleMode, self)._installItem(intCD, slotId, season, component)

    def _selectItem(self, intCD, progressionLevel=0):
        item = self._service.getItemByCD(intCD)
        if item.itemTypeID in EDITABLE_STYLE_APPLY_TO_ALL_AREAS_TYPES:
            slotId = EDITABLE_STYLE_APPLY_TO_ALL_AREAS_TYPES[item.itemTypeID]
            slotData = self.getSlotDataFromSlot(slotId)
            if slotData is None or slotData.intCD != intCD:
                self.__installItemToAllAreas(item)
            slotData = self.getSlotDataFromSlot(slotId)
            if slotData is not None and not slotData.isEmpty():
                self.selectSlot(slotId)
            return False
        else:
            result = super(EditableStyleMode, self)._selectItem(intCD, progressionLevel)
            return result

    @process('sellItem')
    def _sellItem(self, item, count):
        if item.fullInventoryCount(g_currentVehicle.item.intCD) < count:
            vehicleCD = g_currentVehicle.item.descriptor.makeCompactDescr()
            for season, outfit in getOutfitWithoutItems(self.getOutfitsInfo(), item.intCD, count):
                baseOutfit = self.__baseOutfits[season]
                diff = getEditableStyleOutfitDiff(outfit, baseOutfit)
                outfit = self.__style.getOutfit(season, vehicleCD=vehicleCD, diff=diff)
                yield OutfitApplier(g_currentVehicle.item, outfit, season).request()

        yield CustomizationsSeller(g_currentVehicle.item, item, count).request()

    def _selectSlot(self, slotId):
        slotId = correctSlot(slotId)
        result = super(EditableStyleMode, self)._selectSlot(slotId)
        return result

    def _removeItem(self, slotId, season=None):
        season = season or self.season
        outfit = self._modifiedOutfits[season]
        baseOutfit = self.__baseOutfits[season]
        removeItemFromEditableStyle(outfit, baseOutfit, slotId)

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
