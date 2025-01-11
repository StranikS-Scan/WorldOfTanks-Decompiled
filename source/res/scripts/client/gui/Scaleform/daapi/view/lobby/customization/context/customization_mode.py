# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/context/customization_mode.py
import logging
from copy import copy
from functools import partial
import typing
import math_utils
import Math
import AnimationSequence
from CurrentVehicle import g_currentVehicle
from adisp import adisp_process, adisp_async
from gui import SystemMessages
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.daapi.view.lobby.customization.shared import OutfitInfo, getItemAppliedCount, isItemLimitReached, getComponentFromSlot, getItemInventoryCount, getPurchaseLimit, CustomizationTabs, getItemFromSlot, getSlotDataFromSlot, getCurrentVehicleAvailableRegionsMap, fitOutfit, ITEM_TYPE_TO_SLOT_TYPE, removeItemsFromOutfit, isItemsQuantityLimitReached, isSlotFilled, customizationSlotIdToUid, CustomizationSlotUpdateVO
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.customization.constants import CustomizationModeSource
from gui.customization.shared import SeasonType, C11nId, C11N_ITEM_TYPE_MAP
from gui.shared.utils.decorators import adisp_process as wrappedProcess
from helpers import dependency
from shared_utils import first
from items.components.c11n_constants import CustomizationType, SLOT_DEFAULT_ALLOWED_MODEL
from items.readers.shared_readers import getAttachmentHangingEffect
from vehicle_outfit.outfit import Area
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.game_control import ISoundEventChecker
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
from gui.shared.gui_items import GUI_ITEM_TYPE
from vehicle_outfit.containers import emptyComponent
if typing.TYPE_CHECKING:
    from gui.hangar_vehicle_appearance import AnchorParams
    from gui.customization.shared import PurchaseItem
    from gui.shared.gui_items.customization.c11n_items import Customization
    from gui.shared.gui_items.Vehicle import Vehicle
    from items.customizations import SerializableComponent, AttachmentComponent
    from gui.Scaleform.daapi.view.lobby.customization.context.context import CustomizationContext
    from vehicle_outfit.containers import SlotData
    from vehicle_outfit.outfit import Outfit
    from gui.shared.gui_items.customization.c11n_items import Attachment, Customization
_logger = logging.getLogger(__name__)

class CustomizationMode(object):
    _itemsCache = dependency.descriptor(IItemsCache)
    _service = dependency.descriptor(ICustomizationService)
    _soundEventChecker = dependency.descriptor(ISoundEventChecker)
    _hangarSpace = dependency.descriptor(IHangarSpace)

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
        self._hangingEffect = None
        self._hangarSpace.onSpaceDestroy += self._onSpaceDestroy
        return

    @property
    def isInited(self):
        return self._isInited

    @property
    def tabId(self):
        return self._tabId

    @property
    def tabs(self):
        return CustomizationTabs.MODES[self._ctx.modeId]

    @property
    def source(self):
        return self._source

    @property
    def season(self):
        return self._ctx.season

    @property
    def currentOutfit(self):
        return self._modifiedOutfits[self.season].adjust(self._ctx.commonOutfit)

    @property
    def outfits(self):
        outfits = {SeasonType.ALL: self._ctx.commonOutfit}
        outfits.update(self._modifiedOutfits)
        return outfits

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

    def start(self, tabId=None, source=None):
        if tabId is not None and tabId not in self.tabs:
            _logger.warning('Wrong tabId: %s for current customization mode: %s', tabId, self._ctx.modeId)
            tabId = None
        self._tabId = tabId or first(self.tabs)
        self._source = source or CustomizationModeSource.UNDEFINED
        self._onStart()
        return

    def stop(self):
        self._onStop()

    def fini(self):
        self._hangarSpace.onSpaceDestroy -= self._onSpaceDestroy
        self._originalOutfits.clear()
        self._modifiedOutfits.clear()
        self._state.clear()
        self._isInited = False
        self._ctx = None
        self._hangingEffect = None
        return

    def changeTab(self, tabId, itemCD=None):
        if tabId not in self.tabs:
            _logger.warning('Wrong tabId: %s for current customization mode: %s', tabId, self._ctx.modeId)
            return
        if self._tabId == tabId:
            return
        self.unselectItem()
        self.unselectSlot(False)
        self._tabId = tabId
        if not self._ctx.isModeChangeInProgress:
            self._events.onTabChanged(tabId, itemCD)

    def selectSlot(self, slotId):
        if self._selectSlot(slotId):
            self._events.onSlotSelected(self.selectedSlot)

    def unselectSlot(self, isResetCamera=True):
        if self._unselectSlot():
            self._events.onSlotUnselected(isResetCamera)

    def selectItem(self, intCD, progressionLevel=-1):
        if self._selectItem(intCD, progressionLevel) and self.selectedItem:
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
            if not self._removeCommonItem(slotId, season):
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
        if season == SeasonType.ALL:
            outfit = self._ctx.getCommonModifiedOutfit()
            originalOutfit = self._ctx.getCommonOutfit()
        else:
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
    def applyItems(self, purchaseItems, callback):
        purchaseItems = copy(purchaseItems)
        yield self._applyItems(purchaseItems)
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

    def updateOutfits(self):
        self._fillOutfits()
        self._fitOutfits()

    def onVehicleChangeStarted(self):
        self._onVehicleChangeStarted()

    def getModifiedOutfit(self, season=None):
        season = season or self.season
        if season not in self._modifiedOutfits:
            _logger.warning('Wrong season %s', season)
            return None
        else:
            return self._modifiedOutfits[season]

    def getOriginalOutfit(self, season=None):
        season = season or self.season
        if season not in self._originalOutfits:
            _logger.warning('Wrong season %s', season)
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
        return getItemInventoryCount(item, self.outfits)

    def getItemAppliedCount(self, item):
        return getItemAppliedCount(item, self.outfits)

    def getPurchaseLimit(self, item):
        return getPurchaseLimit(item, self.outfits)

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

    def getAnchorVOs(self):
        return self._getAnchorVOs()

    def getSlotDataFromSlot(self, slotId, season=None):
        return getSlotDataFromSlot(self._getOutfitForSlot(slotId, season), slotId)

    def getItemFromSlot(self, slotId, season=None):
        return getItemFromSlot(self._getOutfitForSlot(slotId, season), slotId)

    def getComponentFromSlot(self, slotId, season=None):
        return getComponentFromSlot(self._getOutfitForSlot(slotId, season), slotId)

    def getAnchorParams(self, slotId):
        anchorParams = self._service.getAnchorParams(slotId.areaId, slotId.slotType, slotId.regionIdx)
        return anchorParams

    def rotateAttachment(self, slotId):
        component = getComponentFromSlot(self._ctx.commonOutfit, slotId)
        if component is not None:
            component.rotated = 0 if component.isRotated else 1
            self._ctx.refreshOutfit()
            self._events.onComponentChanged(slotId, False)
        return

    def changeAttachmentScale(self, slotId, scaleFactorId):
        component = getComponentFromSlot(self._ctx.commonOutfit, slotId)
        if component is not None:
            if component.scaleFactorId != scaleFactorId:
                component.scaleFactorId = scaleFactorId
                self._ctx.refreshOutfit()
                self._events.onComponentChanged(slotId, False)
        return

    def _onSpaceDestroy(self, *_):
        self._hangingEffect = None
        return

    def _getOutfitForSlot(self, slotId, season=None):
        if slotId.slotType in C11N_ITEM_TYPE_MAP and C11N_ITEM_TYPE_MAP[slotId.slotType] in CustomizationType.COMMON_TYPES:
            season = SeasonType.ALL
        else:
            season = season or self.season
        return self.outfits[season]

    def _getRequestData(self, purchaseItems):
        requestData = []
        outfit = self._ctx.commonOutfit.copy()
        for pItem in purchaseItems:
            if not pItem.selected:
                if pItem.slotType:
                    slot = outfit.getContainer(pItem.areaID).slotFor(pItem.slotType)
                    slot.remove(pItem.regionIdx)

        outfit.removeStyle()
        requestData.append((outfit, SeasonType.ALL))
        return requestData

    @adisp_async
    @adisp_process
    def _applyItems(self, modifiedOutfits, callback):
        raise NotImplementedError

    @adisp_async
    @wrappedProcess('sellItem')
    def _sellItem(self, item, count, callback):
        raise NotImplementedError

    def _fillOutfits(self):
        raise NotImplementedError

    def _selectSlot(self, slotId):
        if self.selectedItem is None:
            self._selectedSlot = slotId
            return True
        else:
            self.installItem(self.selectedItem.intCD, slotId)
            return False

    def _unselectSlot(self):
        if self._selectedSlot is not None:
            self._selectedSlot = None
            return True
        else:
            return False

    def _selectItem(self, intCD, progressionLevel):
        item = self._service.getItemByCD(intCD)
        if C11N_ITEM_TYPE_MAP[item.itemTypeID] in CustomizationType.COMMON_TYPES:
            if self.selectedSlot is None:
                self._selectedItem = item
                return True
            self.installItem(intCD, self.selectedSlot)
            return True
        else:
            return False

    def _unselectItem(self):
        if self._selectedItem is not None:
            self._selectedItem = None
            return True
        else:
            return False

    def _installItem(self, intCD, slotId, season=None, component=None):
        if C11N_ITEM_TYPE_MAP[slotId.slotType] in CustomizationType.COMMON_TYPES:
            outfit = self._ctx.commonOutfit
            if isItemsQuantityLimitReached(outfit, slotId.slotType) and not isSlotFilled(outfit, slotId):
                return False
            item = self._service.getItemByCD(intCD)
            multiSlot = outfit.getContainer(slotId.areaId).slotFor(slotId.slotType)
            multiSlot.set(item.intCD, idx=slotId.regionIdx, component=component or self._getCommonComponent(item, slotId))
            outfit.invalidate()
            self._playInstallEffect(item, slotId)
            return True
        return False

    def _removeItem(self, slotId, season=None):
        raise NotImplementedError

    def _removeCommonItem(self, slotId, season=None):
        if C11N_ITEM_TYPE_MAP[slotId.slotType] in CustomizationType.COMMON_TYPES:
            multiSlot = self._ctx.commonOutfit.getContainer(slotId.areaId).slotFor(slotId.slotType)
            multiSlot.remove(slotId.regionIdx)
            self._ctx.commonOutfit.invalidate()
            return True
        return False

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
            outfits = self.outfits
            seasons = (self._ctx.season, SeasonType.ALL)
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

    def _getAnchorVOs(self):
        anchorVOs = []
        if g_currentVehicle.isPresent():
            for areaId in Area.ALL:
                outfit = self.currentOutfit
                slot = outfit.getContainer(areaId).slotFor(self.slotType)
                for regionIdx, anchor in g_currentVehicle.item.getAnchors(self.slotType, areaId):
                    if anchor.hiddenForUser:
                        continue
                    model = outfit.modelsSet or SLOT_DEFAULT_ALLOWED_MODEL
                    if model not in anchor.compatibleModels:
                        continue
                    slotId = C11nId(areaId, self.slotType, regionIdx)
                    intCD = slot.getItemCD(regionIdx)
                    uid = customizationSlotIdToUid(slotId)
                    anchorVO = CustomizationSlotUpdateVO(slotId=slotId._asdict(), itemIntCD=intCD, uid=uid)
                    anchorVOs.append(anchorVO._asdict())

        return anchorVOs

    def _onVehicleChangeStarted(self):
        pass

    def _fitOutfits(self, modifiedOnly=False):
        availableRegionsMap = getCurrentVehicleAvailableRegionsMap()
        for season in SeasonType.COMMON_SEASONS:
            fitOutfit(self._modifiedOutfits[season], availableRegionsMap)
            if not modifiedOnly:
                fitOutfit(self._originalOutfits[season], availableRegionsMap)

    def _getCommonComponent(self, item, slotId):
        component = emptyComponent(item.itemTypeID)
        if slotId.slotType == GUI_ITEM_TYPE.ATTACHMENT:
            self._configureAttachmentComponent(component, item, slotId)
        return component

    def _configureAttachmentComponent(self, component, item, slotId):
        slot = g_currentVehicle.item.getAnchorBySlotId(slotId.slotType, slotId.areaId, slotId.regionIdx)
        component.setScaleFactorId(item.scaleFactorId, slot.scaleFactorId)

    def _playInstallEffect(self, item, slotId):
        sequenceID = getAttachmentHangingEffect(item.applyType, item.rarity)
        if sequenceID:
            loader = AnimationSequence.Loader(sequenceID, self._hangarSpace.spaceID)
            self._hangingEffect = loader.loadSync()
            anchorParams = self.getAnchorParams(slotId)
            rotationYPR = Math.Vector3(anchorParams.descriptor.rotation.y, anchorParams.descriptor.rotation.x, anchorParams.descriptor.rotation.z)
            matrix = math_utils.createSRTMatrix(anchorParams.descriptor.scale, rotationYPR, anchorParams.location.position)
            self._hangingEffect.bindToWorld(matrix)
            self._hangingEffect.loopCount = 1
            self._hangingEffect.start()
