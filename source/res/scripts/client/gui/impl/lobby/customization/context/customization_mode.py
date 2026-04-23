# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/customization/context/customization_mode.py
import logging
from copy import copy, deepcopy
from functools import partial
from typing import TYPE_CHECKING
from adisp import adisp_async, adisp_process
from constants import CLIENT_COMMAND_SOURCES
from gui import SystemMessages
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.customization.constants import CustomizationModeSource, CustomizationModes
from gui.customization.shared import C11nId, SeasonType
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.customization.shared import CustomizationTabs, ITEM_TYPE_TO_SLOT_TYPE, OutfitInfo, fitOutfit, getComponentFromSlot, getCurrentVehicleAvailableRegionsMap, getItemAppliedCount, getItemFromSlot, getItemInventoryCount, getPurchaseLimit, getSlotDataFromSlot, isItemLimitReached, removeItemsFromOutfit
from gui.shared.utils.decorators import adisp_process as wrappedProcess
from helpers import dependency
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.game_control import ISoundEventChecker
from skeletons.gui.shared import IItemsCache
if TYPE_CHECKING:
    from typing import Any, Callable, Dict, Generator, List, Optional, Set
    from gui.hangar_vehicle_appearance import AnchorParams
    from gui.customization.shared import PurchaseItem
    from gui.shared.gui_items.customization.c11n_items import Customization
    from gui.shared.gui_items.Vehicle import Vehicle
    from items.customizations import SerializableComponent
    from gui.impl.lobby.customization.context.context import CustomizationContext
    from vehicle_outfit.containers import SlotData
    from vehicle_outfit.outfit import Outfit
_logger = logging.getLogger(__name__)

class CustomizationMode(object):
    modeId = CustomizationModes.NONE
    _tabs = ()
    _itemsCache = dependency.descriptor(IItemsCache)
    _service = dependency.descriptor(ICustomizationService)
    _soundEventChecker = dependency.descriptor(ISoundEventChecker)

    def __init__(self, ctx):
        self._ctx = ctx
        self._isInited = False
        self._tabId = None
        self._source = None
        self._originalOutfits = {}
        self._modifiedOutfits = {}
        self._state = {}
        self._selectedSlot = None
        self._selectedItem = None
        return

    @property
    def isInited(self):
        return self._isInited

    @property
    def tabs(self):
        return self._tabs

    @property
    def tabId(self):
        return self._ctx.tabId

    @property
    def source(self):
        return self._source

    @property
    def season(self):
        return self._ctx.season

    @property
    def currentOutfit(self):
        return self._modifiedOutfits[self.season]

    @property
    def selectedSlot(self):
        return self._selectedSlot

    @property
    def selectedItem(self):
        return self._selectedItem

    @property
    def isRegion(self):
        return self.tabId in CustomizationTabs.REGIONS

    @property
    def slotType(self):
        return CustomizationTabs.SLOT_TYPES[self.tabId]

    @property
    def _events(self):
        return self._ctx.events

    def start(self, source=None):
        self._source = source or CustomizationModeSource.UNDEFINED
        self._onStart()

    def stop(self):
        self._onStop()

    def fini(self):
        self._originalOutfits.clear()
        self._modifiedOutfits.clear()
        self._state.clear()
        self._isInited = False
        self._ctx = None
        return

    def isPossibleToInstallItemForAllSeasons(self, slotId, intCD):
        return False

    def isAutoRentEnabled(self, intCD=None):
        return False

    def changeAutoRent(self, source=CLIENT_COMMAND_SOURCES.UNDEFINED):
        pass

    def selectSlot(self, slotId):
        if self._selectSlot(slotId):
            self._events.onSlotSelected(self.selectedSlot)

    def unselectSlot(self):
        if self._unselectSlot():
            self._events.onSlotUnselected()

    def selectItem(self, intCD, progressionLevel=0):
        if self._selectItem(intCD, progressionLevel):
            self._events.onItemSelected(self.selectedItem.intCD)

    def unselectItem(self):
        if self._unselectItem():
            self._events.onItemUnselected()

    def installItem(self, intCD, slotId, season=None, component=None, refresh=True):
        item = self._service.getItemByCD(intCD)
        errors = self._validateItem(item, slotId, season)
        if errors:
            for error in errors:
                error()

            return False
        elif not self._installItem(intCD, slotId, season, component):
            return False
        else:
            component = self.getComponentFromSlot(slotId, season)
            if refresh:
                self._ctx.refreshOutfit(season)
                self._events.onItemInstalled(item, slotId, season, component)
            if isItemLimitReached(item, self._modifiedOutfits, self):
                if component is None or component.isFilled():
                    self._events.onItemLimitReached(item)
            return True

    def removeItem(self, slotId, season=None, refresh=True):
        item = self.getItemFromSlot(slotId, season)
        if item is None:
            return
        else:
            self._removeItem(slotId, season)
            if refresh:
                self._ctx.refreshOutfit(season)
                self._events.onItemsRemoved(slotId)
            return

    def removeFromSlots(self, slotIds, season=None):
        season = season or self.season
        for slotId in slotIds:
            self.removeItem(slotId, season, refresh=False)

        self._ctx.refreshOutfit(season)
        self._events.onItemsRemoved()

    def removeItemsFromSeason(self, season=None, filterMethod=None, refresh=True, revertToPrevious=False):
        season = season or self.season
        outfit = self._modifiedOutfits[season]
        originalOutfit = self._originalOutfits[season]
        for intCD, _, regionIdx, container, _ in outfit.itemsFull():
            item = self._service.getItemByCD(intCD)
            if item.isHiddenInUI():
                continue
            if filterMethod is None or filterMethod(item):
                areaId = container.getAreaID()
                slotType = ITEM_TYPE_TO_SLOT_TYPE[item.itemTypeID]
                slotId = C11nId(areaId, slotType, regionIdx)
                if revertToPrevious:
                    container = originalOutfit.getContainer(areaId)
                    slotData = container.slotFor(item.itemTypeID).getSlotData(regionIdx)
                    if slotData.intCD:
                        self.installItem(slotData.intCD, slotId, season, refresh=False)
                    else:
                        self.removeItem(slotId, season, refresh=False)
                else:
                    self.removeItem(slotId, season, refresh=False)

        if refresh:
            self._ctx.refreshOutfit(season)
            self._events.onItemsRemoved()
        return

    @adisp_async
    @adisp_process
    def applyItems(self, purchaseItems, isModeChanged, callback):
        purchaseItems = copy(purchaseItems)
        yield self._applyItems(purchaseItems, isModeChanged)
        callback(None)
        return

    @adisp_process
    def sellItem(self, intCD, count, _):
        if not count:
            return
        item = self._service.getItemByCD(intCD)
        self._soundEventChecker.lockPlayingSounds()
        result = yield self._sellItem(item, count)
        self._soundEventChecker.unlockPlayingSounds(restore=False)
        if self.isInited and result.success:
            self._events.onItemSold(item=item, count=count)

    def cancelChanges(self):
        self._cancelChanges()
        self._events.onChangesCanceled()

    def updateOutfits(self, preserve=False):
        if preserve:
            self._preserveState()
            self._fillOutfits()
            self._restoreState()
        else:
            self._fillOutfits()
        self._fitOutfits()

    def onVehicleChangeStarted(self):
        self._onVehicleChangeStarted()

    def getModifiedOutfit(self, season=None):
        season = season or self.season
        if season not in self._modifiedOutfits:
            _logger.warning('Wrong season %s', self.season)
            return None
        else:
            return self._modifiedOutfits[season]

    def getOriginalOutfit(self, season=None):
        season = season or self.season
        if season not in self._originalOutfits:
            _logger.warning('Wrong season %s', self.season)
            return None
        else:
            return self._originalOutfits[season]

    def getModifiedOutfits(self):
        return copy(self._modifiedOutfits)

    def getOriginalOutfits(self):
        return copy(self._originalOutfits)

    def getOutfitsInfo(self):
        outfitsInfo = {}
        for season in SeasonType.COMMON_SEASONS:
            outfitsInfo[season] = OutfitInfo(self._originalOutfits[season], self._modifiedOutfits[season])

        return outfitsInfo

    def getItemInventoryCount(self, item, excludeBase=False):
        return getItemInventoryCount(item, self._modifiedOutfits)

    def getItemAppliedCount(self, item):
        return getItemAppliedCount(item, self._modifiedOutfits)

    def getPurchaseLimit(self, item):
        return getPurchaseLimit(item, self._modifiedOutfits)

    def getAppliedItems(self, isOriginal=True):
        return self._getAppliedItems(isOriginal)

    def getDependenciesData(self):
        return {}

    def isOutfitsEmpty(self):
        return self._isOutfitsEmpty()

    def isOutfitsModified(self):
        return self._isOutfitsModified()

    def isOutfitsHasLockedItems(self):
        for season in SeasonType.COMMON_SEASONS:
            outfit = self._modifiedOutfits[season]
            for itemCD in outfit.items():
                item = self._service.getItemByCD(itemCD)
                if not item.isUnlockedByToken():
                    return True

        return False

    def getOutfitsLockedItemsCount(self):
        count = 0
        for season in SeasonType.COMMON_SEASONS:
            outfit = self._modifiedOutfits[season]
            for itemCD in outfit.items():
                item = self._service.getItemByCD(itemCD)
                if not item.isUnlockedByToken():
                    count += 1

        return count

    def getAnchorsData(self):
        return self._getAnchorsData()

    def getSlotDataFromSlot(self, slotId, season=None):
        season = season or self.season
        outfit = self._modifiedOutfits[season]
        return getSlotDataFromSlot(outfit, slotId)

    def getItemFromSlot(self, slotId, season=None):
        season = season or self.season
        outfit = self._modifiedOutfits[season]
        return getItemFromSlot(outfit, slotId)

    def getComponentFromSlot(self, slotId, season=None):
        season = season or self.season
        outfit = self._modifiedOutfits[season]
        return getComponentFromSlot(outfit, slotId)

    def getAnchorParams(self, slotId):
        anchorParams = self._service.getAnchorParams(slotId.areaId, slotId.slotType, slotId.regionIdx)
        return anchorParams

    @adisp_async
    @adisp_process
    def _applyItems(self, modifiedOutfits, isModeChanged, callback):
        raise NotImplementedError

    @adisp_async
    @wrappedProcess('sellItem')
    def _sellItem(self, item, count, callback):
        raise NotImplementedError

    def _preserveState(self):
        self._state = deepcopy(self._modifiedOutfits)

    def _fillOutfits(self):
        raise NotImplementedError

    def _restoreState(self):
        self._modifiedOutfits = self._state
        self._state = {}

    def _selectSlot(self, slotId):
        raise NotImplementedError

    def _unselectSlot(self):
        raise NotImplementedError

    def _selectItem(self, intCD, progressionLevel):
        raise NotImplementedError

    def _unselectItem(self):
        raise NotImplementedError

    def _installItem(self, intCD, slotId, season=None, component=None):
        raise NotImplementedError

    def _removeItem(self, slotId, season=None):
        raise NotImplementedError

    def _onStart(self):
        if not self.isInited:
            self.updateOutfits()
            self._isInited = True

    def _onStop(self):
        pass

    def _cancelChanges(self):
        for season in SeasonType.COMMON_SEASONS:
            self._modifiedOutfits[season] = self._originalOutfits[season].copy()
            self._ctx.refreshOutfit(season)

    def _getAppliedItems(self, isOriginal=True):
        if isOriginal:
            outfits = self._originalOutfits
            seasons = SeasonType.COMMON_SEASONS
        else:
            outfits = self._modifiedOutfits
            seasons = (self._ctx.season,)
        appliedItems = set()
        for seasonType in seasons:
            outfit = outfits[seasonType]
            appliedItems.update((intCD for intCD in outfit.items()))

        return appliedItems

    def _validateItem(self, item, slotId, season):
        errors = []
        if isItemLimitReached(item, self._modifiedOutfits, self):
            error = partial(SystemMessages.pushI18nMessage, key=SYSTEM_MESSAGES.CUSTOMIZATION_PROHIBITED, type=SystemMessages.SM_TYPE.Warning, itemName=item.userName)
            errors.append(error)
        if not item.mayInstall(self._ctx.vehicle):
            error = partial(SystemMessages.pushMessage, text=backport.text(R.strings.system_messages.customization.invalidVehicle()), type=SystemMessages.SM_TYPE.Warning)
            errors.append(error)
        return errors

    def _removeHiddenFromOutfit(self, outfit, vehicleIntCD):
        toRemove = []
        for itemCD, count in outfit.itemsCounter.iteritems():
            item = self._service.getItemByCD(itemCD)
            if not item.isHidden or item.isStyleOnly or item.isHiddenInUI():
                continue
            if item.fullInventoryCount(vehicleIntCD) < count:
                toRemove.append(itemCD)

        if toRemove:
            removeItemsFromOutfit(outfit, filterMethod=lambda i: i.intCD in toRemove)

    def _isOutfitsEmpty(self):
        raise NotImplementedError

    def _isOutfitsModified(self):
        raise NotImplementedError

    def _getAnchorsData(self):
        raise NotImplementedError

    def _onVehicleChangeStarted(self):
        pass

    def _fitOutfits(self, modifiedOnly=False):
        availableRegionsMap = getCurrentVehicleAvailableRegionsMap()
        for season in SeasonType.COMMON_SEASONS:
            fitOutfit(self._modifiedOutfits[season], availableRegionsMap)
            if not modifiedOnly:
                fitOutfit(self._originalOutfits[season], availableRegionsMap)
