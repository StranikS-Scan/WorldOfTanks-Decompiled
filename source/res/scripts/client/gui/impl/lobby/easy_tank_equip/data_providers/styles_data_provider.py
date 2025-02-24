# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/easy_tank_equip/data_providers/styles_data_provider.py
import random
from typing import TYPE_CHECKING
from gui.Scaleform.daapi.view.lobby.customization.shared import getStyledModeRequestData
from gui.customization.shared import C11N_ITEM_TYPE_MAP
from gui.impl.gen.view_models.views.lobby.easy_tank_equip.common.proposal_model import ProposalDisableReason
from gui.impl.lobby.easy_tank_equip.data_providers.base_data_provider import BaseDataProvider, PresetInfo
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.gui_item_economics import ITEM_PRICE_ZERO
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from items import vehicles
from items.components.c11n_constants import EMPTY_ITEM_ID
from items.components.c11n_constants import SeasonType
from shared_utils import first
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.server_events import IEventsCache
if TYPE_CHECKING:
    from gui.shared.gui_items.customization.c11n_items import Style
    from gui.shared.gui_items.Vehicle import Vehicle
    from typing import List, Optional, Dict
    from vehicle_outfit.outfit import Outfit

class StylesPresetInfo(PresetInfo):

    def __init__(self, installed, storedItemsCount, installedItemsCount, itemPrice, style):
        super(StylesPresetInfo, self).__init__(installed, storedItemsCount, installedItemsCount, itemPrice)
        self.style = style


class StylesDataProvider(BaseDataProvider):
    PRESETS_COUNT = 3
    __eventsCache = dependency.descriptor(IEventsCache)
    __c11nService = dependency.descriptor(ICustomizationService)

    def __init__(self, vehicle, balance):
        super(StylesDataProvider, self).__init__(vehicle, balance)
        self.__currentStyle = self.__c11nService.getCurrentStyle()
        self.__season = None
        self.__vehicleCD = self.vehicle.descriptor.makeCompactDescr()
        self.__stylesPresets = []
        self.__customizationCache = vehicles.g_cache.customization20().itemTypes
        return

    def initialize(self):
        if self.vehicle.isOutfitLocked or self.vehicle.descriptor.type.hasCustomDefaultCamouflage:
            self.proposalDisableReason = ProposalDisableReason.BUILT_IN_STYLE
            return
        super(StylesDataProvider, self).initialize()
        self.isProposalSelected = len(self.presets) > 1 or not (self.isCurrentPresetDisabledForApplying() or self.__stylesPresets[0].isRentable)

    def finalize(self):
        self.__currentStyle = None
        self.__season = None
        self.__stylesPresets = []
        super(StylesDataProvider, self).finalize()
        return

    def setValuesFromCurrentPreset(self):
        style = self.__stylesPresets[self.currentPresetIndex]
        if not self.__season:
            self.__season = first(style.seasons)
        self.__applyCamouflageTTC(style)

    def revertChangesFromSelectedPreset(self):
        outfit = self.vehicle.getOutfit(self.__season)
        if outfit:
            outfit.hull.slotFor(GUI_ITEM_TYPE.CAMOUFLAGE).clear()
            self.vehicle.removeOutfitForSeason(self.__season)

    def getPresets(self):
        self.__setStylesPresets()
        return self.__getPresetsInfo()

    def updatePresets(self, fullUpdate=False):
        presets = self.getPresets() if fullUpdate else self.__getPresetsInfo()
        self.presets = presets
        presetIndex = min(self.currentPresetIndex, len(presets) - 1)
        self.currentPresetIndex = presetIndex

    def swapSlots(self, firstSlot, secondSlot):
        pass

    def getCurrentPresetItemsIds(self):
        return [] if self.isProposalDisabled() else [self.__stylesPresets[self.currentPresetIndex].intCD]

    def _getPresetDataForApplying(self):
        data = super(StylesDataProvider, self)._getPresetDataForApplying()
        style = self.__stylesPresets[self.currentPresetIndex]
        data.update({'styleData': self.__getStyleRequestData(self.vehicle, self.__vehicleCD, style, self.__season)})
        return data

    def __applyCamouflageTTC(self, style):
        itemTypeID = GUI_ITEM_TYPE.CAMOUFLAGE
        cType = C11N_ITEM_TYPE_MAP[itemTypeID]
        for itemID in self.__customizationCache[cType]:
            if itemID != EMPTY_ITEM_ID:
                camo = self.__c11nService.getItemByID(itemTypeID, itemID)
                outfit = style.getOutfit(self.__season, vehicleCD=self.__vehicleCD)
                outfit.hull.slotFor(GUI_ITEM_TYPE.CAMOUFLAGE).set(camo.intCD)
                self.vehicle.setCustomOutfit(self.__season, outfit)
                return

    def __getPresetsInfo(self):
        return [ self.__getStylesPresetInfo(style) for style in self.__stylesPresets ]

    def __setStylesPresets(self):
        self.__stylesPresets = []
        if self.__currentStyle:
            self.__season = first(self.__currentStyle.seasons)
            self.__stylesPresets.append(self.__currentStyle)
            return
        presetsLeftCount = self.PRESETS_COUNT
        availableStyles = self.__getAvailableStyles()
        styles3d = self.__getRandomStyles([ style for style in availableStyles if style.is3D and not style.isRentable ], presetsLeftCount)
        presetsLeftCount -= len(styles3d)
        styles2d = self.__getRandomStyles([ style for style in availableStyles if not style.is3D and not style.isRentable ], presetsLeftCount) if presetsLeftCount > 0 else []
        presetsLeftCount -= len(styles2d)
        rentStyle = self.__getRandomStyles([ style for style in availableStyles if not style.is3D and style.isRentable ], presetsLeftCount) if presetsLeftCount > 0 else []
        self.__stylesPresets = styles3d + styles2d + rentStyle

    def __getStylesPresetInfo(self, style):
        isInstalled = self.__isStyleInstalled(style)
        storedItemsCount = int(bool(style.boundInventoryCount(self.vehicle.intCD) if style.isRentable else style.inventoryCount))
        return StylesPresetInfo(installed=isInstalled, storedItemsCount=storedItemsCount, installedItemsCount=int(isInstalled), itemPrice=style.getBuyPrice() if style.isRentable and storedItemsCount == 0 else ITEM_PRICE_ZERO, style=style)

    def __isStyleInstalled(self, style):
        return bool(self.__currentStyle) and self.__currentStyle.id == style.id

    def __getAvailableStyles(self):
        itemTypeID = GUI_ITEM_TYPE.STYLE
        cType = C11N_ITEM_TYPE_MAP[itemTypeID]
        requirement = REQ_CRITERIA.CUSTOM(lambda item: item.itemTypeID == itemTypeID and item.season & SeasonType.ALL and (not item.requiredToken or self.__eventsCache.questsProgress.getTokenCount(item.requiredToken) > 0) and (item.buyCount > 0 and item.isRentable or item.fullInventoryCount(self.vehicle.intCD) > 0) and item.mayInstall(self.vehicle) and (not item.isProgressive or item.getLatestOpenedProgressionLevel(self.vehicle) > 0))
        styles = []
        for itemID in self.__customizationCache[cType]:
            if itemID != EMPTY_ITEM_ID:
                style = self.__c11nService.getItemByID(itemTypeID, itemID)
                if requirement(style):
                    styles.append(style)

        return styles

    def __getStyleRequestData(self, vehicle, vehicleCD, style, season):
        outfit = style.getOutfit(season, vehicleCD=vehicleCD)
        styleProgressionLevel = outfit.progressionLevel if style.isProgressive else 0
        outfit.removeStyle()
        if style.is3D:
            requestData = [(self.__c11nService.getEmptyOutfit(self.__vehicleCD), SeasonType.ALL)]
        else:
            requestData = [(self.__c11nService.getCommonOutfit(), SeasonType.ALL)]
        data = getStyledModeRequestData(requestData, style, vehicle, styleProgressionLevel=styleProgressionLevel)
        return {key:value for value, key in data}

    @staticmethod
    def __getRandomStyles(styles, count):
        return random.sample(styles, min(len(styles), count))
