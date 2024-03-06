# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/context/styled_mode.py
import logging
import typing
from CurrentVehicle import g_currentVehicle
from adisp import adisp_async, adisp_process
from constants import CLIENT_COMMAND_SOURCES
from gui.Scaleform.daapi.view.lobby.customization.context.customization_mode import CustomizationMode
from gui.Scaleform.daapi.view.lobby.customization.shared import OutfitInfo, CustomizationTabs, customizationSlotIdToUid, CustomizationSlotUpdateVO, getStylePurchaseItems, removeItemFromEditableStyle, fitOutfit, getCurrentVehicleAvailableRegionsMap, getEditableStyleOutfitDiff, removeUnselectedItemsFromEditableStyle
from gui.customization.constants import CustomizationModes
from gui.customization.shared import C11nId, PurchaseItem
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.processors.common import CustomizationsSeller, OutfitApplier
from gui.shared.gui_items.processors.vehicle import VehicleAutoStyleEquipProcessor
from gui.shared.utils.decorators import adisp_process as wrappedProcess
from items.components.c11n_constants import SeasonType
from items.customizations import CustomizationOutfit
from vehicle_outfit.outfit import Area, Outfit
from helpers import dependency
from account_helpers.settings_core.settings_constants import OnceOnlyHints
from skeletons.account_helpers.settings_core import ISettingsCore
from tutorial.hints_manager import HINT_SHOWN_STATUS
from vehicle_systems.camouflages import getStyleProgressionOutfit
from items.customizations import parseCompDescr
if typing.TYPE_CHECKING:
    from items.customizations import SerializableComponent
    from gui.shared.gui_items.customization.c11n_items import Style, Customization
    from gui.Scaleform.daapi.view.lobby.customization.context.context import CustomizationContext
_logger = logging.getLogger(__name__)

class StyledMode(CustomizationMode):
    modeId = CustomizationModes.STYLED
    _tabs = CustomizationTabs.MODES[modeId]
    STYLE_SLOT = C11nId(areaId=Area.MISC, slotType=GUI_ITEM_TYPE.STYLE, regionIdx=0)
    _settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, ctx):
        super(StyledMode, self).__init__(ctx)
        self.__originalStyle = None
        self.__modifiedStyle = None
        self.__prolongRent = False
        self.__autoRentEnabled = False
        self.__autoRentChangeSource = CLIENT_COMMAND_SOURCES.UNDEFINED
        return

    @property
    def originalStyle(self):
        return self.__originalStyle

    @property
    def modifiedStyle(self):
        return self.__modifiedStyle

    def changeTab(self, tabId, itemCD=None):
        if tabId != CustomizationTabs.STYLES:
            _logger.warning('There is no tabs in styled customization mode')
        elif itemCD is not None:
            self._events.onTabChanged(tabId, itemCD)
        return

    def isAutoRentEnabled(self):
        return self.__autoRentEnabled

    def changeAutoRent(self, source=CLIENT_COMMAND_SOURCES.UNDEFINED):
        self.__autoRentEnabled = not self.__autoRentEnabled
        if source != CLIENT_COMMAND_SOURCES.UNDEFINED:
            self.__autoRentChangeSource = source
        self._events.onComponentChanged(self.STYLE_SLOT, True)

    def getStyleInfo(self):
        return OutfitInfo(self.__originalStyle, self.__modifiedStyle)

    def getPurchaseItems(self):
        return getStylePurchaseItems(self.__modifiedStyle, self.getModifiedOutfits(), prolongRent=self.__prolongRent, progressionLevel=self.getStyleProgressionLevel()) if self.__modifiedStyle is not None else []

    def getDependenciesData(self):
        return self.__modifiedStyle.getDependenciesIntCDs() if self.__modifiedStyle else {}

    def removeStyle(self, intCD):
        if self.__modifiedStyle is not None and self.__modifiedStyle.intCD == intCD:
            self.removeItem(self.STYLE_SLOT)
        return

    def prolongRent(self, style):
        if style is None:
            return
        else:
            self.__prolongRent = True
            self.installItem(style.intCD, self.STYLE_SLOT)
            self._events.onProlongStyleRent()
            return

    def changeStyleProgressionLevel(self, toLevel):
        vehicleCD = g_currentVehicle.item.descriptor.makeCompactDescr()
        baseOutfit = self.__modifiedStyle.getOutfit(self.season, vehicleCD=vehicleCD)
        for seasonID in SeasonType.COMMON_SEASONS:
            self._modifiedOutfits[seasonID] = getStyleProgressionOutfit(self._modifiedOutfits[seasonID], toLevel, seasonID)
            addOutfit = self.__modifiedStyle.getAdditionalOutfit(toLevel, seasonID, vehicleCD)
            if addOutfit is not None:
                baseOutfit = baseOutfit.patch(addOutfit)
            diff = getEditableStyleOutfitDiff(self._modifiedOutfits[seasonID], baseOutfit)
            self._ctx.stylesDiffsCache.saveDiff(self.__modifiedStyle, seasonID, diff)

        self._fitOutfits(modifiedOnly=True)
        self._ctx.refreshOutfit()
        self._events.onComponentChanged(self.STYLE_SLOT, True)
        return

    def getStyleProgressionLevel(self):
        return self._modifiedOutfits[self.season].progressionLevel if self.__modifiedStyle and self.__modifiedStyle.isProgressive else -1

    def clearStyle(self):
        style = self.__modifiedStyle
        if style is None:
            _logger.error('Failed to install EditableStyle base outfit. Style is not applied')
            return
        else:
            diffs = {season:None for season in SeasonType.COMMON_SEASONS}
            self._ctx.stylesDiffsCache.saveDiffs(style, diffs)
            vehicleCD = g_currentVehicle.item.descriptor.makeCompactDescr()
            for season in SeasonType.COMMON_SEASONS:
                outfit = style.getOutfit(season, vehicleCD=vehicleCD)
                self._modifiedOutfits[season] = outfit.copy()

            self._fitOutfits(modifiedOnly=True)
            self._ctx.refreshOutfit()
            self._ctx.events.onItemsRemoved()
            return

    def _onStart(self):
        super(StyledMode, self)._onStart()
        if self.__modifiedStyle is not None:
            self._installItem(self.__modifiedStyle.intCD, self.STYLE_SLOT)
        self.__prolongRent = False
        self.__autoRentEnabled = g_currentVehicle.item.isAutoRentStyle
        return

    def _fillOutfits(self):
        styleId = self._service.getStyledOutfit(self.season).id
        style = self._service.getItemByID(GUI_ITEM_TYPE.STYLE, styleId) if styleId else None
        isInstalled = self._service.isStyleInstalled()
        if not isInstalled:
            if style is not None and style.isHidden and style.fullInventoryCount(g_currentVehicle.item.intCD) == 0:
                style = None
        self.__originalStyle = style
        self.__modifiedStyle = style
        vehicleCD = g_currentVehicle.item.descriptor.makeCompactDescr()
        diffs = self._ctx.stylesDiffsCache.getDiffs(style) if style is not None else {}
        styleProgressionLevel = 0
        styleOutfitData = self._itemsCache.items.inventory.getOutfitData(g_currentVehicle.item.descriptor.type.compactDescr, SeasonType.ALL)
        if styleOutfitData:
            styledOutfitComponent = parseCompDescr(styleOutfitData)
            styleProgressionLevel = styledOutfitComponent.styleProgressionLevel
        for season in SeasonType.COMMON_SEASONS:
            if style is None:
                outfit = self._service.getEmptyOutfit()
            else:
                diff = diffs.get(season)
                if not isInstalled and diff is not None:
                    diffOutfit = Outfit(strCompactDescr=diff, vehicleCD=vehicleCD)
                    self._removeHiddenFromOutfit(diffOutfit, g_currentVehicle.item.intCD)
                    diff = diffOutfit.pack().makeCompDescr()
                outfit = style.getOutfit(season, vehicleCD=vehicleCD, diff=diff)
                if self.__modifiedStyle and self.__modifiedStyle.isProgressionRewindEnabled:
                    outfit = getStyleProgressionOutfit(outfit, styleProgressionLevel, season)
            self._originalOutfits[season] = outfit.copy()
            self._modifiedOutfits[season] = outfit.copy()

        return

    def _restoreState(self):
        super(StyledMode, self)._restoreState()
        styleId = self._modifiedOutfits[SeasonType.SUMMER].id
        self.__modifiedStyle = self._service.getItemByID(GUI_ITEM_TYPE.STYLE, styleId) if styleId else None
        return

    def _selectItem(self, intCD, *_):
        self.selectSlot(self.STYLE_SLOT)
        currentItem = self.getItemFromSlot(self._selectedSlot)
        if currentItem is not None and currentItem.intCD == intCD:
            return False
        else:
            self.installItem(intCD, self._selectedSlot)
            item = self._service.getItemByCD(intCD)
            serverSettings = self._settingsCore.serverSettings
            if item.isProgressionRequiredCanBeEdited(g_currentVehicle.item.intCD):
                wasVisited = bool(serverSettings.getOnceOnlyHintsSetting(OnceOnlyHints.C11N_PROGRESSION_REQUIRED_STYLE_SLOT_HINT))
                if not wasVisited:
                    serverSettings.setOnceOnlyHintsSettings({OnceOnlyHints.C11N_EDITABLE_STYLE_SLOT_HINT: HINT_SHOWN_STATUS,
                     OnceOnlyHints.C11N_PROGRESSION_REQUIRED_STYLE_SLOT_HINT: HINT_SHOWN_STATUS})
            elif item.isEditable:
                wasVisited = bool(serverSettings.getOnceOnlyHintsSetting(OnceOnlyHints.C11N_EDITABLE_STYLE_SLOT_HINT))
                if not wasVisited and item.canBeEditedForVehicle(g_currentVehicle.item.intCD):
                    serverSettings.setOnceOnlyHintsSettings({OnceOnlyHints.C11N_EDITABLE_STYLE_SLOT_HINT: HINT_SHOWN_STATUS})
            return False

    def _unselectItem(self):
        return False

    def _selectSlot(self, slotId):
        if slotId != self.STYLE_SLOT:
            _logger.warning('Wrong slot selected for customization styled mode: %s', slotId)
            return False
        self._selectedSlot = slotId
        return True

    def _unselectSlot(self):
        if self._selectedSlot is not None:
            self._selectedSlot = None
            return True
        else:
            return False

    def _installItem(self, intCD, slotId, season=None, component=None):
        item = self._service.getItemByCD(intCD)
        if item.itemTypeID != GUI_ITEM_TYPE.STYLE:
            _logger.warning('Wrong itemType: %s. Only styles could be installed in styled customization mode.', item.itemTypeID)
            return False
        self.__modifiedStyle = item
        vehicleCD = g_currentVehicle.item.descriptor.makeCompactDescr()
        for s in SeasonType.COMMON_SEASONS:
            diff = self._ctx.stylesDiffsCache.getDiff(item, s)
            outfit = item.getOutfit(s, vehicleCD=vehicleCD, diff=diff)
            self._modifiedOutfits[s] = outfit.copy()

        self._fitOutfits(modifiedOnly=True)
        return True

    def _removeItem(self, slotId, season=None):
        if self.__modifiedStyle is None:
            return
        elif slotId == self.STYLE_SLOT:
            self.__modifiedStyle = None
            self._modifiedOutfits = {s:self._service.getEmptyOutfit() for s in SeasonType.COMMON_SEASONS}
            return
        elif not self.__modifiedStyle.isEditable:
            return _logger.error('Failed to remove item from slotId: %s for style: %s. Style is not Editable', slotId, self.__modifiedStyle)
        else:
            season = season or self.season
            outfit = self._modifiedOutfits[season]
            vehicleCD = g_currentVehicle.item.descriptor.makeCompactDescr()
            baseOutfit = self.__modifiedStyle.getOutfit(season, vehicleCD=vehicleCD)
            fitOutfit(baseOutfit, getCurrentVehicleAvailableRegionsMap())
            self._modifiedOutfits[season] = removeItemFromEditableStyle(outfit, baseOutfit, slotId, season)
            diff = getEditableStyleOutfitDiff(outfit, baseOutfit)
            self._ctx.stylesDiffsCache.saveDiff(self.__modifiedStyle, season, diff)
            return

    def _cancelChanges(self):
        super(StyledMode, self)._cancelChanges()
        self.__modifiedStyle = self.__originalStyle

    @adisp_async
    @adisp_process
    def _applyItems(self, purchaseItems, isModeChanged, callback):
        results = []
        style = self.__modifiedStyle
        vehicleCD = g_currentVehicle.item.descriptor.makeCompactDescr()
        originalOutfits = self._ctx.startMode.getOriginalOutfits()
        if style is not None:
            baseStyleOutfits = {}
            modifiedStyleOutfits = {}
            for season in SeasonType.COMMON_SEASONS:
                diff = self._ctx.stylesDiffsCache.getDiffs(style).get(season)
                baseStyleOutfits[season] = style.getOutfit(season, vehicleCD=vehicleCD)
                modifiedStyleOutfits[season] = style.getOutfit(season, vehicleCD=vehicleCD, diff=diff)

            removeUnselectedItemsFromEditableStyle(modifiedStyleOutfits, baseStyleOutfits, purchaseItems)
            result = yield OutfitApplier(g_currentVehicle.item, [ (outfit, season) for season, outfit in modifiedStyleOutfits.iteritems() ]).request()
            results.append(result)
        else:
            outfit = self._modifiedOutfits[self.season]
            result = yield OutfitApplier(g_currentVehicle.item, ((outfit, SeasonType.ALL),)).request()
            results.append(result)
        if style is not None and style.isRentable and self.__prolongRent:
            self._service.buyItems(style, count=1, vehicle=g_currentVehicle.item)
            self.__prolongRent = False
        isAutoRentChanged = self.__autoRentEnabled != g_currentVehicle.item.isAutoRentStyle
        if isAutoRentChanged:
            yield VehicleAutoStyleEquipProcessor(g_currentVehicle.item, self.__autoRentEnabled, self.__autoRentChangeSource).request()
            self.__autoRentChangeSource = CLIENT_COMMAND_SOURCES.UNDEFINED
        if self.isInited:
            self._events.onItemsBought(originalOutfits, purchaseItems, results, isAutoRentChanged)
        callback(self)
        return

    @adisp_async
    @wrappedProcess('sellItem')
    def _sellItem(self, item, count, callback):
        if item.fullInventoryCount(g_currentVehicle.item.intCD) < count:
            emptyComponent = CustomizationOutfit()
            vehicleCD = g_currentVehicle.item.descriptor.makeCompactDescr()
            outfit = Outfit(component=emptyComponent, vehicleCD=vehicleCD)
            yield OutfitApplier(g_currentVehicle.item, ((outfit, SeasonType.ALL),)).request()
        result = yield CustomizationsSeller(g_currentVehicle.item, item, count).request()
        callback(result)

    def _getAppliedItems(self, isOriginal=True):
        appliedItems = set()
        style = self.__originalStyle if isOriginal else self.__modifiedStyle
        if style is not None:
            appliedItems.add(style.intCD)
        return appliedItems

    def _isOutfitsEmpty(self):
        return self.__modifiedStyle is None

    def _isOutfitsModified(self):
        isStyleChanged = any((not self._originalOutfits[season].isEqual(self._modifiedOutfits[season]) for season in SeasonType.COMMON_SEASONS))
        isAutoRentChanged = self.__autoRentEnabled != g_currentVehicle.item.isAutoRentStyle
        if self.__modifiedStyle and self.__modifiedStyle.isProgressive:
            modifiedOutfit = self._modifiedOutfits[self.season]
            originalOutfit = self._originalOutfits[self.season]
            isInstalled = originalOutfit.id == modifiedOutfit.id and self._service.isStyleInstalled()
            modifiedProgression = modifiedOutfit.progressionLevel
            if g_currentVehicle and g_currentVehicle.item:
                originalProgression = self.__modifiedStyle.getLatestOpenedProgressionLevel(g_currentVehicle.item)
            else:
                originalProgression = originalOutfit.progressionLevel
            isProgressionReachable = self.__modifiedStyle.isProgressionPurchasable(modifiedProgression)
            isProgressionReachable = isProgressionReachable or modifiedProgression == originalProgression or self.__modifiedStyle.isProgressionRewindEnabled
            if (not isInstalled or modifiedProgression != originalProgression) and not isProgressionReachable:
                return False
            if not isInstalled:
                return True
        return isStyleChanged or isAutoRentChanged

    def _getAnchorVOs(self):
        slotId = C11nId(self.STYLE_SLOT.areaId, self.STYLE_SLOT.slotType, self.STYLE_SLOT.regionIdx)
        uid = customizationSlotIdToUid(slotId)
        intCD = self.modifiedStyle.intCD if self.modifiedStyle is not None else 0
        anchorVO = CustomizationSlotUpdateVO(slotId=slotId._asdict(), itemIntCD=intCD, uid=uid)
        return [anchorVO._asdict()]

    def _onVehicleChangeStarted(self):
        self.__prolongRent = False
        self._autoRentEnabled = g_currentVehicle.item.isAutoRentStyle
