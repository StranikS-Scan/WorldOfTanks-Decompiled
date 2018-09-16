# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/main_view.py
from collections import namedtuple
import struct
import BigWorld
import GUI
import Math
from adisp import async, process as adisp_process
from AvatarInputHandler import cameras
from CurrentVehicle import g_currentVehicle
from account_helpers.settings_core.settings_constants import GRAPHICS, GAME
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from gui import DialogsInterface, g_tankActiveCamouflage, SystemMessages
from gui.app_loader import g_appLoader
from gui.app_loader.settings import GUI_GLOBAL_SPACE_ID as _SPACE_ID
from gui.customization.shared import chooseMode
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.dialogs import I18nConfirmDialogMeta
from gui.Scaleform.daapi.view.lobby.customization import CustomizationItemCMHandler
from gui.Scaleform.daapi.view.lobby.customization.customization_carousel import CustomizationCarouselDataProvider, comparisonKey
from gui.Scaleform.daapi.view.lobby.customization.customization_cm_handlers import CustomizationOptions
from gui.Scaleform.daapi.view.lobby.customization.customization_item_vo import buildCustomizationItemDataVO
from gui.Scaleform.daapi.view.lobby.customization.shared import C11nMode, CUSTOMIZATION_POPOVER_ALIASES, TABS_ITEM_MAPPING, C11nTabs, SEASON_IDX_TO_TYPE, SEASON_TYPE_TO_NAME, SEASONS_ORDER, OutfitInfo, getCustomPurchaseItems, getStylePurchaseItems, getTotalPurchaseInfo, getOutfitWithoutItems, getItemInventoryCount, getStyleInventoryCount, AdditionalPurchaseGroups
from gui.Scaleform.daapi.view.lobby.customization.sound_constants import SOUNDS, C11N_SOUND_SPACE
from gui.Scaleform.framework.entities.View import ViewKey, ViewKeyDynamic
from gui.Scaleform.framework.managers.view_lifecycle_watcher import IViewLifecycleHandler, ViewLifecycleWatcher
from gui.Scaleform.genConsts.CUSTOMIZATION_ALIASES import CUSTOMIZATION_ALIASES
from gui.Scaleform.daapi.view.meta.CustomizationMainViewMeta import CustomizationMainViewMeta
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.Scaleform.locale.MESSENGER import MESSENGER
from gui.Scaleform.locale.VEHICLE_CUSTOMIZATION import VEHICLE_CUSTOMIZATION
from gui.Scaleform.locale.ITEM_TYPES import ITEM_TYPES
from gui.Scaleform.Waiting import Waiting
from gui.SystemMessages import SM_TYPE, CURRENCY_TO_SM_TYPE
from gui.shared import events, g_eventBus
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.formatters import text_styles, icons, getItemPricesVO, formatPrice
from gui.shared.gui_items import GUI_ITEM_TYPE, GUI_ITEM_TYPE_NAMES
from gui.shared.gui_items.customization.outfit import Area
from gui.shared.gui_items.gui_item_economics import ITEM_PRICE_EMPTY, ItemPrice
from gui.shared.gui_items.processors.common import OutfitApplier, StyleApplier, CustomizationsSeller
from gui.shared.utils.HangarSpace import g_hangarSpace
from gui.shared.utils.decorators import process
from gui.shared.utils.functions import makeTooltip
from helpers import dependency, int2roman
from helpers.i18n import makeString as _ms
from items.components.c11n_constants import SeasonType
from shared_utils import first, nextTick
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from gui.Scaleform.daapi.view.dialogs.confirm_customization_item_dialog_meta import ConfirmC11nBuyMeta, ConfirmC11nSellMeta
from gui.shared.utils import toUpper

class _C11nWindowsLifecycleHandler(IViewLifecycleHandler):
    service = dependency.descriptor(ICustomizationService)
    __SUB_VIEWS = (VIEW_ALIAS.SETTINGS_WINDOW, VIEW_ALIAS.CUSTOMIZATION_PURCHASE_WINDOW, VIEW_ALIAS.LOBBY_MENU)
    __DIALOGS = (VIEW_ALIAS.SIMPLE_DIALOG, CUSTOMIZATION_ALIASES.CONFIRM_CUSTOMIZATION_ITEM_DIALOG)

    def __init__(self):
        super(_C11nWindowsLifecycleHandler, self).__init__([ ViewKey(alias) for alias in self.__SUB_VIEWS ] + [ ViewKeyDynamic(alias) for alias in self.__DIALOGS ])
        self.__viewStack = []

    def onViewCreated(self, view):
        self.__viewStack.append(view.key)
        self.service.suspendHighlighter()

    def onViewDestroyed(self, _):
        self.__viewStack.pop()
        if not self.__viewStack:
            self.service.resumeHighlighter()


CustomizationCarouselDataVO = namedtuple('CustomizationCarouselDataVO', ('displayString', 'isZeroCount', 'shouldShow', 'itemLayoutSize', 'bookmarks'))
CustomizationAnchorInitVO = namedtuple('CustomizationAnchorInitVO', ('anchorUpdateVOs', 'doRegions'))
CustomizationSlotUpdateVO = namedtuple('CustomizationSlotUpdateVO', ('slotId', 'propertySheetAlias', 'itemIntCD', 'uid'))
CustomizationSlotIdVO = namedtuple('CustomizationSlotIdVO', ('areaId', 'slotId', 'regionId'))
CustomizationAnchorsSetVO = namedtuple('CustomizationAnchorsSetVO', ('rendererList',))
CustomizationAnchorPositionVO = namedtuple('CustomizationAnchorPositionVO', ('zIndex', 'slotId'))
AnchorPositionData = namedtuple('AnchorPositionData', ('angleToCamera', 'clipSpacePos', 'slotId'))

class _VehicleCustomizationAnchorsUpdater(object):

    def __init__(self, service):
        self.__service = service
        self.__vehicleCustomizationAnchors = None
        self.__processedAnchors = set()
        return

    def startUpdater(self, interfaceScale):
        if self.__vehicleCustomizationAnchors is None:
            self.__vehicleCustomizationAnchors = GUI.WGVehicleCustomizationAnchors(interfaceScale)
        return

    def stopUpdater(self):
        if self.__vehicleCustomizationAnchors is not None:
            self._delAllAnchors()
            self.__vehicleCustomizationAnchors = None
        return

    def setAnchors(self, displayObjects, isRegionObjects):

        def getRegionBySlotId(customSlotId):
            outfit = self.__service.getEmptyOutfit()
            for container in (cnt for cnt in outfit.containers() if cnt.getAreaID() == customSlotId.areaId):
                for slot in (x for x in container.slots() if x.getType() == customSlotId.slotId):
                    if len(slot.getRegions()) > customSlotId.regionId:
                        return slot.getRegions()[customSlotId.regionId]
                    return None

            return None

        if self.__vehicleCustomizationAnchors is not None:
            processedObjectIds = set()
            for displayObject in displayObjects:
                if hasattr(displayObject, 'slotData'):
                    customSlotId = CustomizationSlotIdVO(displayObject.slotData.slotId.areaId, displayObject.slotData.slotId.slotId, displayObject.slotData.slotId.regionId)
                    normal = Math.Vector3(0, 0, 0)
                    if isRegionObjects:
                        region = getRegionBySlotId(customSlotId)
                        anchorWorldPos = self.__service.getPointForRegionLeaderLine(region)
                    else:
                        anchorWorldPos = self.__service.getPointForAnchorLeaderLine(customSlotId.areaId, customSlotId.slotId, customSlotId.regionId)
                        normal = self.__service.getNormalForAnchorLeaderLine(customSlotId.areaId, customSlotId.slotId, customSlotId.regionId)
                    if anchorWorldPos is not None:
                        uid = self.__vehicleCustomizationAnchors.addAnchor(anchorWorldPos, normal, displayObject, not isRegionObjects)
                        processedObjectIds.add(uid)

            delAnchors = self.__processedAnchors - processedObjectIds
            for anchorId in delAnchors:
                self.__vehicleCustomizationAnchors.delAnchor(anchorId)

            self.__processedAnchors = processedObjectIds
        return

    def setInterfaceScale(self, scale):
        self.__vehicleCustomizationAnchors.setInterfaceScale(scale)

    def _delAllAnchors(self):
        if self.__vehicleCustomizationAnchors is not None:
            for anchorId in self.__processedAnchors:
                self.__vehicleCustomizationAnchors.delAnchor(anchorId)

            self.__processedAnchors.clear()
        return


class MainView(CustomizationMainViewMeta):
    _COMMON_SOUND_SPACE = C11N_SOUND_SPACE
    lobbyContext = dependency.descriptor(ILobbyContext)
    itemsCache = dependency.descriptor(IItemsCache)
    service = dependency.descriptor(ICustomizationService)
    settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, _=None):
        super(MainView, self).__init__()
        self.__viewLifecycleWatcher = ViewLifecycleWatcher()
        self.fadeAnchorsOut = False
        self._currentSeason = SeasonType.SUMMER
        self._tabIndex = C11nTabs.PAINT
        self._lastTab = C11nTabs.PAINT
        self._originalStyle = None
        self._modifiedStyle = None
        self._isCurrentStyleInstalled = False
        self._originalOutfits = {}
        self._modifiedOutfits = {}
        self._currentOutfit = None
        self._mode = C11nMode.CUSTOM
        self._isDeferredRenderer = True
        self.__anchorPositionCallbackID = None
        self._state = {}
        self._needFullRebuild = False
        self.__locatedOnEmbelem = False
        self.itemIsPicked = False
        self._vehicleCustomizationAnchorsUpdater = None
        return

    def showBuyWindow(self):
        self.__releaseItemSound()
        self.soundManager.playInstantSound(SOUNDS.SELECT)
        purchaseItems = self.getPurchaseItems()
        cart = getTotalPurchaseInfo(purchaseItems)
        if cart.totalPrice == ITEM_PRICE_EMPTY:
            self.buyAndExit(purchaseItems)
        else:
            self.as_hideAnchorPropertySheetS()
            self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.CUSTOMIZATION_PURCHASE_WINDOW), EVENT_BUS_SCOPE.LOBBY)

    def onSelectItem(self, index):
        self._carouselDP.selectItemIdx(index)
        self.soundManager.playInstantSound(SOUNDS.SELECT)

    def onPickItem(self):
        if not self.itemIsPicked:
            self.soundManager.playInstantSound(SOUNDS.PICK)
            self.itemIsPicked = True

    def onReleaseItem(self):
        self.__releaseItemSound()

    def changeSeason(self, seasonIdx):
        self._currentSeason = SEASON_IDX_TO_TYPE[seasonIdx]
        seasonName = SEASON_TYPE_TO_NAME.get(self._currentSeason)
        self.soundManager.playInstantSound(SOUNDS.SEASON_SELECT.format(seasonName))
        self.refreshOutfit()
        self.refreshCarousel(rebuild=True)
        self.as_refreshAnchorPropertySheetS()
        doRegions = self._tabIndex in C11nTabs.REGIONS
        self.__setAnchorsInitData(self._tabIndex, doRegions, True)

    def refreshCarousel(self, rebuild=False):
        if rebuild:
            self._carouselDP.buildList(self._tabIndex, self._currentSeason, refresh=False)
            self.as_setCarouselDataS(self._buildCustomizationCarouselDataVO())
        self._carouselDP.refresh()

    def refreshHotFilters(self):
        self.as_setCarouselFiltersDataS({'hotFilters': [self._carouselDP.getOwnedFilter(), self._carouselDP.getAppliedFilter()]})

    def refreshOutfit(self):
        if self._mode == C11nMode.STYLE:
            if self._modifiedStyle:
                self._currentOutfit = self._modifiedStyle.getOutfit(self._currentSeason)
            else:
                self._currentOutfit = self.service.getEmptyOutfit()
        else:
            self._currentOutfit = self._modifiedOutfits[self._currentSeason]
        self.service.tryOnOutfit(self._currentOutfit)
        g_tankActiveCamouflage[g_currentVehicle.item.intCD] = self._currentSeason

    def showGroupFromTab(self, tabIndex):
        self.soundManager.playInstantSound(SOUNDS.TAB_SWITCH)
        self._tabIndex = tabIndex
        doRegions = self._tabIndex in C11nTabs.REGIONS
        self.service.stopHighlighter()
        if doRegions:
            itemTypeID = TABS_ITEM_MAPPING[self._tabIndex]
            self.service.startHighlighter(chooseMode(itemTypeID, g_currentVehicle.item))
        self.__setAnchorsInitData(self._tabIndex, doRegions)
        if self.__locatedOnEmbelem and g_hangarSpace.spaceInited:
            space = g_hangarSpace.space
            space.clearSelectedEmblemInfo()
            space.locateCameraToPreview()
        self.__updateAnchorPositions()
        if self._tabIndex == C11nTabs.STYLE:
            slotIdVO = CustomizationSlotIdVO(0, GUI_ITEM_TYPE.STYLE, 0)._asdict()
        elif self._tabIndex == C11nTabs.EFFECT:
            slotIdVO = CustomizationSlotIdVO(Area.MISC, GUI_ITEM_TYPE.MODIFICATION, 0)._asdict()
        else:
            slotIdVO = None
        self.as_updateSelectedRegionsS(slotIdVO)
        self.refreshCarousel(rebuild=True)
        return

    def installCustomizationElement(self, intCD, areaId, slotId, regionId, seasonIdx):
        if self.itemIsPicked:
            self.soundManager.playInstantSound(SOUNDS.APPLY)
        item = self.itemsCache.items.getItemByCD(intCD)
        if item.isHidden and not self.getItemInventoryCount(item):
            SystemMessages.pushI18nMessage(SYSTEM_MESSAGES.CUSTOMIZATION_PROHIBITED, type=SystemMessages.SM_TYPE.Warning, itemName=item.userName)
            return
        if self._mode == C11nMode.STYLE:
            self._modifiedStyle = item
        else:
            season = SEASON_IDX_TO_TYPE.get(seasonIdx, self._currentSeason)
            outfit = self._modifiedOutfits[season]
            outfit.getContainer(areaId).slotFor(slotId).set(item, idx=regionId)
            outfit.invalidate()
        self.refreshOutfit()
        self.__setBuyingPanelData()
        self.__setHeaderInitData()
        self.refreshCarousel(rebuild=self._carouselDP.getAppliedFilter() or self._carouselDP.getOwnedFilter())

    def clearCustomizationItem(self, areaId, slotId, regionId, seasonIdx):
        self.soundManager.playInstantSound(SOUNDS.REMOVE)
        season = SEASON_IDX_TO_TYPE.get(seasonIdx, self._currentSeason)
        outfit = self._modifiedOutfits[season]
        outfit.getContainer(areaId).slotFor(slotId).remove(idx=regionId)
        self.refreshOutfit()
        doRegions = self._tabIndex in C11nTabs.REGIONS
        self.__setAnchorsInitData(self._tabIndex, doRegions, True)
        self.__setBuyingPanelData()
        self.__setHeaderInitData()
        self.refreshCarousel(rebuild=self._carouselDP.getAppliedFilter() or self._carouselDP.getOwnedFilter())

    def switchToCustom(self, updateUI=True):
        self.soundManager.playInstantSound(SOUNDS.TAB_SWITCH)
        self._mode = C11nMode.CUSTOM
        self._tabIndex = self._lastTab
        self.refreshOutfit()
        self.as_setBottomPanelTabsDataS({'tabData': self.__getItemTabsData(),
         'selectedTab': self._tabIndex})
        self._carouselDP.selectItem()
        self.__setBuyingPanelData()
        self.__setHeaderInitData()

    def switchToStyle(self):
        self.soundManager.playInstantSound(SOUNDS.TAB_SWITCH)
        self._mode = C11nMode.STYLE
        self._lastTab = self._tabIndex
        self._tabIndex = C11nTabs.STYLE
        self.refreshOutfit()
        self.as_setBottomPanelTabsDataS({'tabData': self.__getItemTabsData(),
         'selectedTab': self._tabIndex})
        self._carouselDP.selectItem()
        self.__setBuyingPanelData()
        self.__setHeaderInitData()

    def fadeOutAnchors(self, isFadeOut):
        self.fadeAnchorsOut = isFadeOut

    def closeWindow(self):
        purchaseItems = self.getPurchaseItems()
        cart = getTotalPurchaseInfo(purchaseItems)
        if cart.numTotal:
            DialogsInterface.showDialog(I18nConfirmDialogMeta('customization/close'), self.__onConfirmCloseWindow)
        else:
            self.__onConfirmCloseWindow(proceed=True)

    def itemContextMenuDisplayed(self):
        cmHandler = self.app.contextMenuManager.getCurrentHandler()
        if isinstance(cmHandler, CustomizationItemCMHandler):
            cmHandler.onSelected += self._itemCtxMenuSelected

    def resetFilter(self):
        self.clearFilter()
        self.refreshFilterData()
        self.refreshHotFilters()
        self.refreshCarousel(rebuild=True)

    def clearFilter(self):
        self._carouselDP.clearFilter()

    def refreshFilterData(self):
        self.as_setFilterDataS(self._carouselDP.getFilterData())

    def getHistoricalPopoverData(self):
        self.soundManager.playInstantSound(SOUNDS.SELECT)
        if self._mode == C11nMode.STYLE and self._modifiedStyle:
            if not self._modifiedStyle.isHistorical():
                return {'items': [self._modifiedStyle.intCD]}
            return {'items': []}
        items = []
        for outfit in self._modifiedOutfits.itervalues():
            items.extend((item for item in outfit.items() if not item.isHistorical()))

        return {'items': [ item.intCD for item in sorted(items, key=comparisonKey) ]}

    def removeItems(self, *intCDs):
        self.soundManager.playInstantSound(SOUNDS.REMOVE)
        if self._modifiedStyle and self._modifiedStyle.intCD in intCDs:
            self._modifiedStyle = None
        for outfit in self._modifiedOutfits.itervalues():
            for slot in outfit.slots():
                for idx in range(slot.capacity()):
                    item = slot.getItem(idx)
                    if item and item.intCD in intCDs:
                        slot.remove(idx)

        self.refreshOutfit()
        self.__setHeaderInitData()
        self.__setBuyingPanelData()
        self.as_refreshAnchorPropertySheetS()
        doRegions = self._tabIndex in C11nTabs.REGIONS
        self.__setAnchorsInitData(self._tabIndex, doRegions, True)
        self.refreshCarousel(rebuild=self._carouselDP.getAppliedFilter() or self._carouselDP.getOwnedFilter())
        return

    def updatePropertySheetButtons(self, areaId, slotId, regionId):
        self.service.onPropertySheetShow(areaId, slotId, regionId)

    def onLobbyClick(self):
        if self._tabIndex in (C11nTabs.EMBLEM, C11nTabs.INSCRIPTION):
            self.as_hideAnchorPropertySheetS()
            if self.__locatedOnEmbelem and g_hangarSpace.spaceInited:
                space = g_hangarSpace.space
                space.clearSelectedEmblemInfo()
                space.locateCameraToPreview()
                self.__updateAnchorPositions()
                self.__locatedOnEmbelem = False

    def setEnableMultiselectRegions(self, isEnabled):
        self.service.setSelectHighlighting(isEnabled)

    def onChangeSize(self):
        self.__updateAnchorPositions()

    def onSelectAnchor(self, areaID, regionID):
        if g_hangarSpace.spaceInited:
            self.soundManager.playInstantSound(SOUNDS.CHOOSE)
            if self._tabIndex == C11nTabs.EMBLEM:
                emblemType = 'player'
                zoom = 0.06
            else:
                emblemType = 'inscription'
                zoom = 0.1
            self.__updateAnchorPositions()
            self.__locatedOnEmbelem = g_hangarSpace.space.locateCameraOnEmblem(areaID < 2, emblemType, regionID, zoom)
            self.as_cameraAutoRotateChangedS(True)
            BigWorld.callback(5, self.__cameraRotationFinished)

    def __cameraRotationFinished(self):
        self.as_cameraAutoRotateChangedS(False)

    def getOutfitsInfo(self):
        outfitsInfo = {}
        for season in SEASONS_ORDER:
            outfitsInfo[season] = OutfitInfo(self._originalOutfits[season], self._modifiedOutfits[season])

        return outfitsInfo

    def getStyleInfo(self):
        return OutfitInfo(self._originalStyle, self._modifiedStyle)

    def getPurchaseItems(self):
        return getCustomPurchaseItems(self.getOutfitsInfo()) if self._mode == C11nMode.CUSTOM else getStylePurchaseItems(self.getStyleInfo(), self._isCurrentStyleInstalled)

    def getItemInventoryCount(self, item):
        return getItemInventoryCount(item, self.getOutfitsInfo()) if self._mode == C11nMode.CUSTOM else getStyleInventoryCount(item, self.getStyleInfo())

    def getCurrentOutfit(self):
        return self._currentOutfit

    def getModifiedStyle(self):
        return self._modifiedStyle

    def getModifiedOutfit(self, season):
        return self._modifiedOutfits.get(season)

    def getMode(self):
        return self._mode

    def getCurrentSeason(self):
        return self._currentSeason

    def getCurrentTab(self):
        return self._tabIndex

    def getAppliedItems(self, isOriginal=True):
        outfits = self._originalOutfits if isOriginal else self._modifiedOutfits
        style = self._originalStyle if isOriginal else self._modifiedStyle
        seasons = SeasonType.COMMON_SEASONS if isOriginal else (self._currentSeason,)
        appliedItems = set()
        for seasonType in seasons:
            outfit = outfits[seasonType]
            appliedItems.update((i.intCD for i in outfit.items()))

        if style:
            appliedItems.add(style.intCD)
        return appliedItems

    def isItemInOutfit(self, item):
        return any((outfit.has(item) for outfit in self._originalOutfits.itervalues())) or any((outfit.has(item) for outfit in self._modifiedOutfits.itervalues()))

    @process('buyAndInstall')
    def buyAndExit(self, purchaseItems):
        self.itemsCache.onSyncCompleted -= self.__onCacheResync
        cart = getTotalPurchaseInfo(purchaseItems)
        groupHasItems = {AdditionalPurchaseGroups.STYLES_GROUP_ID: False,
         SeasonType.WINTER: False,
         SeasonType.SUMMER: False,
         SeasonType.DESERT: False}
        modifiedOutfits = {season:outfit.copy() for season, outfit in self._modifiedOutfits.iteritems()}
        results = []
        for pItem in purchaseItems:
            if not pItem.selected:
                if pItem.slot:
                    slot = modifiedOutfits[pItem.group].getContainer(pItem.areaID).slotFor(pItem.slot)
                    slot.remove(pItem.regionID)
            groupHasItems[pItem.group] = True

        if self._mode == C11nMode.CUSTOM:
            groupHasItems[self._currentSeason] = True
        empty = self.service.getEmptyOutfit()
        for season in SeasonType.COMMON_SEASONS:
            if groupHasItems[season]:
                yield OutfitApplier(g_currentVehicle.item, empty, season).request()

        for season in SeasonType.COMMON_SEASONS:
            if groupHasItems[season]:
                outfit = modifiedOutfits[season]
                result = yield OutfitApplier(g_currentVehicle.item, outfit, season).request()
                results.append(result)

        if groupHasItems[AdditionalPurchaseGroups.STYLES_GROUP_ID]:
            result = yield StyleApplier(g_currentVehicle.item, self._modifiedStyle).request()
            results.append(result)
        errorCount = 0
        for result in results:
            if not result.success:
                errorCount += 1
            if result.userMsg:
                SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)

        if not errorCount:
            if cart.totalPrice != ITEM_PRICE_EMPTY:
                msgCtx = {'money': formatPrice(cart.totalPrice.price),
                 'count': cart.numSelected}
                SystemMessages.pushI18nMessage(MESSENGER.SERVICECHANNELMESSAGES_SYSMSG_CONVERTER_CUSTOMIZATIONSBUY, type=CURRENCY_TO_SM_TYPE.get(cart.totalPrice.getCurrency(byWeight=True), SM_TYPE.PurchaseForGold), **msgCtx)
            else:
                SystemMessages.pushI18nMessage(MESSENGER.SERVICECHANNELMESSAGES_SYSMSG_CONVERTER_CUSTOMIZATIONS, type=SM_TYPE.Information)
            self.__onConfirmCloseWindow(proceed=True)
        else:
            self.__onCacheResync()
        self.itemsCache.onSyncCompleted += self.__onCacheResync

    @process('sellItem')
    def sellItem(self, intCD, count):
        if not count:
            return
        self._needFullRebuild = self._carouselDP.getOwnedFilter()
        item = self.itemsCache.items.getItemByCD(intCD)
        if item.fullInventoryCount(g_currentVehicle.item) < count:
            if self._mode == C11nMode.CUSTOM:
                for season, outfit in getOutfitWithoutItems(self.getOutfitsInfo(), intCD, count):
                    yield OutfitApplier(g_currentVehicle.item, outfit, season).request()

            else:
                yield StyleApplier(g_currentVehicle.item).request()
        yield CustomizationsSeller(g_currentVehicle.item, item, count).request()
        nextTick(self.refreshOutfit)()

    def onAnchorsShown(self, anchors):
        if self._vehicleCustomizationAnchorsUpdater is not None:
            self._vehicleCustomizationAnchorsUpdater.setAnchors(anchors, self._tabIndex in C11nTabs.REGIONS)
        return

    def _populate(self):
        super(MainView, self)._populate()
        self.soundManager.playInstantSound(SOUNDS.ENTER)
        self.__viewLifecycleWatcher.start(self.app.containerManager, [_C11nWindowsLifecycleHandler()])
        self._isDeferredRenderer = self.settingsCore.getSetting(GRAPHICS.RENDER_PIPELINE) == 0
        g_clientUpdateManager.addMoneyCallback(self.__setBuyingPanelData)
        self.lobbyContext.addHeaderNavigationConfirmator(self.__confirmHeaderNavigation)
        self.lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingChanged
        self.service.onCarouselFilter += self.__onCarouselFilter
        self.service.onRemoveItems += self.removeItems
        self.service.onOutfitChanged += self.__onOutfitChanged
        g_eventBus.addListener(CameraRelatedEvents.IDLE_CAMERA, self.__onNotifyHangarCameraIdleStateChanged)
        g_hangarSpace.onSpaceCreate += self.__onSpaceCreateHandler
        g_hangarSpace.onSpaceDestroy += self.__onSpaceDestroyHandler
        g_hangarSpace.onSpaceRefresh += self.__onSpaceRefreshHandler
        self.service.onRegionHighlighted += self.__onRegionHighlighted
        self.itemsCache.onSyncCompleted += self.__onCacheResync
        self.__carveUpOutfits()
        if self._originalStyle and self._isCurrentStyleInstalled:
            self._mode = C11nMode.STYLE
        elif self._originalOutfits[self._currentSeason].isInstalled():
            self._mode = C11nMode.CUSTOM
        else:
            self._mode = C11nMode.STYLE
        self._carouselDP = CustomizationCarouselDataProvider(g_currentVehicle, self._carouseItemWrapper, self)
        self._carouselDP.setFlashObject(self.as_getDataProviderS())
        self._carouselDP.setEnvironment(self.app)
        self.__setHeaderInitData()
        self.__setFooterInitData()
        self.__setBuyingPanelData()
        self.__setSeasonData()
        self._vehicleCustomizationAnchorsUpdater = _VehicleCustomizationAnchorsUpdater(self.service)
        self._vehicleCustomizationAnchorsUpdater.startUpdater(self.settingsCore.interfaceScale.get())
        self.refreshOutfit()
        self.settingsCore.interfaceScale.onScaleExactlyChanged += self.__onInterfaceScaleChanged
        self.settingsCore.onSettingsChanged += self.__onSettingsChanged
        self.__updateCameraParalaxFlag()

    def _dispose(self):
        if g_appLoader.getSpaceID() != _SPACE_ID.LOGIN:
            self.__releaseItemSound()
            self.soundManager.playInstantSound(SOUNDS.EXIT)
        self.settingsCore.onSettingsChanged -= self.__onSettingsChanged
        self.settingsCore.interfaceScale.onScaleExactlyChanged -= self.__onInterfaceScaleChanged
        self._vehicleCustomizationAnchorsUpdater.stopUpdater()
        self._vehicleCustomizationAnchorsUpdater = None
        if self.__locatedOnEmbelem and g_hangarSpace.spaceInited:
            space = g_hangarSpace.space
            space.clearSelectedEmblemInfo()
            space.locateCameraToPreview()
        self.__viewLifecycleWatcher.stop()
        self.service.stopHighlighter()
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.lobbyContext.deleteHeaderNavigationConfirmator(self.__confirmHeaderNavigation)
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingChanged
        self.service.onCarouselFilter -= self.__onCarouselFilter
        self.service.onRemoveItems -= self.removeItems
        self.service.onOutfitChanged -= self.__onOutfitChanged
        g_eventBus.removeListener(CameraRelatedEvents.IDLE_CAMERA, self.__onNotifyHangarCameraIdleStateChanged)
        g_hangarSpace.onSpaceCreate -= self.__onSpaceCreateHandler
        g_hangarSpace.onSpaceDestroy -= self.__onSpaceDestroyHandler
        g_hangarSpace.onSpaceRefresh -= self.__onSpaceRefreshHandler
        self.service.onRegionHighlighted -= self.__onRegionHighlighted
        self.itemsCache.onSyncCompleted -= self.__onCacheResync
        if g_currentVehicle.item:
            g_tankActiveCamouflage[g_currentVehicle.item.intCD] = self._currentSeason
            g_currentVehicle.refreshModel()
        self._isCurrentStyleInstalled = False
        super(MainView, self)._dispose()
        return

    @adisp_process
    def _itemCtxMenuSelected(self, ctxMenuID, itemIntCD):
        item = self.itemsCache.items.getItemByCD(itemIntCD)
        if ctxMenuID == CustomizationOptions.BUY:
            yield DialogsInterface.showDialog(ConfirmC11nBuyMeta(itemIntCD))
        elif ctxMenuID == CustomizationOptions.SELL:
            inventoryCount = self.getItemInventoryCount(item)
            yield DialogsInterface.showDialog(ConfirmC11nSellMeta(itemIntCD, inventoryCount, self.sellItem))
        elif ctxMenuID == CustomizationOptions.REMOVE_FROM_TANK:
            self.removeItems(itemIntCD)

    def _getUpdatedAnchorPositions(self):
        anchorVOs = []
        anchorPosData = []
        cType = TABS_ITEM_MAPPING[self._tabIndex]
        if self._tabIndex == C11nTabs.STYLE:
            slotId = CustomizationSlotIdVO(0, GUI_ITEM_TYPE.STYLE, 0)
            anchorData = self.__getAnchorPositionData(slotId, 0)
            anchorPosData.append(anchorData)
        else:
            outfit = self.service.getEmptyOutfit()
            for container in outfit.containers():
                for slot in (x for x in container.slots() if x.getType() == cType):
                    for regionId, region in enumerate(slot.getRegions()):
                        slotId = CustomizationSlotIdVO(container.getAreaID(), slot.getType(), regionId)
                        anchorData = self.__getAnchorPositionData(slotId, region)
                        if anchorData is not None:
                            anchorPosData.append(anchorData)

        for zIdx, posData in enumerate(anchorPosData):
            anchorVOs.append(CustomizationAnchorPositionVO(zIdx, posData.slotId._asdict())._asdict())

        return CustomizationAnchorsSetVO(anchorVOs)._asdict()

    def _buildCustomizationCarouselDataVO(self):
        isZeroCount = self._carouselDP.itemCount == 0
        countStyle = text_styles.error if isZeroCount else text_styles.main
        displayString = text_styles.main('{} / {}'.format(countStyle(str(self._carouselDP.itemCount)), str(self._carouselDP.totalItemCount)))
        shouldShow = self._carouselDP.itemCount < self._carouselDP.totalItemCount
        return CustomizationCarouselDataVO(displayString, isZeroCount, shouldShow, itemLayoutSize=self._carouselDP.getItemSizeData(), bookmarks=self._carouselDP.getBookmarkData())._asdict()

    def _carouseItemWrapper(self, itemCD):
        item = self.itemsCache.items.getItemByCD(itemCD)
        itemInventoryCount = self.getItemInventoryCount(item)
        if item.itemTypeID == GUI_ITEM_TYPE.MODIFICATION:
            showUnsupportedAlert = not self._isDeferredRenderer
        else:
            showUnsupportedAlert = False
        isCurrentlyApplied = itemCD in self._carouselDP.getCurrentlyApplied()
        return buildCustomizationItemDataVO(item, itemInventoryCount, showUnsupportedAlert=showUnsupportedAlert, isCurrentlyApplied=isCurrentlyApplied)

    def __carveUpOutfits(self):
        for season in SeasonType.COMMON_SEASONS:
            outfit = self.service.getCustomOutfit(season)
            self._modifiedOutfits[season] = outfit.copy()
            if outfit.isInstalled():
                self._originalOutfits[season] = outfit.copy()
            self._originalOutfits[season] = self.service.getEmptyOutfit()
            for slot in self._modifiedOutfits[season].slots():
                for idx in range(slot.capacity()):
                    item = slot.getItem(idx)
                    if item and item.isHidden and item.fullInventoryCount(g_currentVehicle.item) == 0:
                        slot.remove(idx)

        style = self.service.getCurrentStyle()
        self._isCurrentStyleInstalled = self.service.isCurrentStyleInstalled()
        if self._isCurrentStyleInstalled:
            self._originalStyle = style
            self._modifiedStyle = style
        else:
            self._originalStyle = None
            if style and style.isHidden and style.fullInventoryCount(g_currentVehicle.item) == 0:
                self._modifiedStyle = None
            else:
                self._modifiedStyle = style
        return

    def __updateAnchorPositions(self, _=None):
        self.as_setAnchorPositionsS(self._getUpdatedAnchorPositions())

    def __onRegionHighlighted(self, typeID, tankPartID, regionID, selected, hovered):
        slotId = None
        if hovered:
            self.soundManager.playInstantSound(SOUNDS.HOVER)
            return
        else:
            if self._tabIndex == C11nTabs.EFFECT:
                tankPartID = Area.MISC
                typeID = GUI_ITEM_TYPE.MODIFICATION
            if tankPartID != -1 and regionID != -1:
                slotId = CustomizationSlotIdVO(tankPartID, typeID, regionID)._asdict()
                if selected:
                    self.soundManager.playInstantSound(SOUNDS.CHOOSE)
            self.as_onRegionHighlightedS(slotId)
            return

    def __onSpaceCreateHandler(self):
        Waiting.hide('loadHangarSpace')
        self.refreshOutfit()
        self.__updateAnchorPositions()

    def __onSpaceDestroyHandler(self, _):
        Waiting.hide('loadHangarSpace')
        self.__onConfirmCloseWindow(proceed=True)

    def __onSpaceRefreshHandler(self):
        Waiting.show('loadHangarSpace')

    def __onConfirmCloseWindow(self, proceed):
        if proceed:
            self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_HANGAR), scope=EVENT_BUS_SCOPE.LOBBY)

    def __onCarouselFilter(self, **kwargs):
        if 'group' in kwargs:
            self._carouselDP.setActiveGroupIndex(kwargs['group'])
        if 'historic' in kwargs:
            self._carouselDP.setHistoricalFilter(kwargs['historic'])
        if 'inventory' in kwargs:
            self._carouselDP.setOwnedFilter(kwargs['inventory'])
        if 'applied' in kwargs:
            self._carouselDP.setAppliedFilter(kwargs['applied'])
        self.refreshCarousel(rebuild=True)
        self.refreshHotFilters()

    def __onOutfitChanged(self):
        self.refreshOutfit()
        self.__setBuyingPanelData()

    def __onCacheResync(self, *_):
        if not g_currentVehicle.isPresent():
            self.__onConfirmCloseWindow(proceed=True)
            return
        self.__preserveState()
        self.__carveUpOutfits()
        self.__restoreState()
        self.__setHeaderInitData()
        self.__setBuyingPanelData()
        if self._mode == C11nMode.CUSTOM:
            self.as_hideAnchorPropertySheetS()
        else:
            self.as_refreshAnchorPropertySheetS()
        self.refreshCarousel(rebuild=self._needFullRebuild)
        self.refreshOutfit()
        self._needFullRebuild = False

    def __preserveState(self):
        self._state.update(modifiedStyle=self._modifiedStyle, modifiedOutfits={season:outfit.copy() for season, outfit in self._modifiedOutfits.iteritems()})

    def __restoreState(self):
        self._modifiedStyle = self._state.get('modifiedStyle')
        self._modifiedOutfits = self._state.get('modifiedOutfits')
        if self._modifiedStyle:
            self._modifiedStyle = self.itemsCache.items.getItemByCD(self._modifiedStyle.intCD)
        self._state.clear()

    def __onServerSettingChanged(self, diff):
        if 'isCustomizationEnabled' in diff and not diff.get('isCustomizationEnabled', True):
            SystemMessages.pushI18nMessage(SYSTEM_MESSAGES.CUSTOMIZATION_UNAVAILABLE, type=SystemMessages.SM_TYPE.Warning)
            self.__onConfirmCloseWindow(proceed=True)

    def __setBuyingPanelData(self, *_):
        purchaseItems = self.getPurchaseItems()
        cartInfo = getTotalPurchaseInfo(purchaseItems)
        totalPriceVO = getItemPricesVO(cartInfo.totalPrice)
        accountMoney = self.itemsCache.items.stats.money
        if cartInfo.totalPrice != ITEM_PRICE_EMPTY:
            label = _ms(VEHICLE_CUSTOMIZATION.COMMIT_BUY)
            self.as_showBuyingPanelS()
        else:
            label = _ms(VEHICLE_CUSTOMIZATION.COMMIT_APPLY)
            self.as_hideBuyingPanelS()
        isAtLeastOneOufitNotEmpty = False
        for season in SeasonType.COMMON_SEASONS:
            if not self._modifiedOutfits[season].isEmpty():
                isAtLeastOneOufitNotEmpty = True
                break

        isApplyEnabled = cartInfo.minPriceItem.isDefined() and cartInfo.minPriceItem <= accountMoney or cartInfo.isAtLeastOneItemFromInventory or cartInfo.isAtLeastOneItemDismantled or self._mode == C11nMode.CUSTOM and not self._originalOutfits[self._currentSeason].isInstalled() and isAtLeastOneOufitNotEmpty
        shortage = self.itemsCache.items.stats.money.getShortage(cartInfo.totalPrice.price)
        self.as_setBottomPanelHeaderS({'buyBtnEnabled': isApplyEnabled,
         'buyBtnLabel': label,
         'enoughMoney': getItemPricesVO(ItemPrice(shortage, shortage))[0],
         'pricePanel': totalPriceVO[0]})

    def __setSeasonData(self):
        seasonRenderersList = []
        for season in SEASONS_ORDER:
            seasonName = SEASON_TYPE_TO_NAME.get(season)
            seasonRenderersList.append({'seasonName': VEHICLE_CUSTOMIZATION.getSeasonName(seasonName),
             'seasonIconSmall': RES_ICONS.getSeasonIcon(seasonName)})

        self.as_setSeasonPanelDataS({'seasonRenderersList': seasonRenderersList})

    def __setAnchorsInitData(self, tabIndex, doRegions, update=False):

        def customizationSlotIdToUid(customizationSlotIdVO):
            s = struct.pack('bbh', customizationSlotIdVO.areaId, customizationSlotIdVO.slotId, customizationSlotIdVO.regionId)
            return struct.unpack('I', s)[0]

        anchorVOs = []
        cType = TABS_ITEM_MAPPING[tabIndex]
        if tabIndex == C11nTabs.STYLE:
            slotId = CustomizationSlotIdVO(0, GUI_ITEM_TYPE.STYLE, 0)
            uid = customizationSlotIdToUid(slotId)
            popoverAlias = CUSTOMIZATION_POPOVER_ALIASES[GUI_ITEM_TYPE.STYLE]
            anchorVOs.append(CustomizationSlotUpdateVO(slotId._asdict(), popoverAlias, -1, uid)._asdict())
        else:
            for container in self._currentOutfit.containers():
                for slot in (x for x in container.slots() if x.getType() == cType):
                    for regionId, region in enumerate(slot.getRegions()):
                        slotId = CustomizationSlotIdVO(container.getAreaID(), slot.getType(), regionId)
                        popoverAlias = CUSTOMIZATION_POPOVER_ALIASES[slot.getType()]
                        item = slot.getItem(regionId)
                        itemIntCD = item.intCD if item is not None else 0
                        uid = customizationSlotIdToUid(slotId)
                        if self.__getAnchorPositionData(slotId, region) is not None:
                            anchorVOs.append(CustomizationSlotUpdateVO(slotId._asdict(), popoverAlias, itemIntCD, uid)._asdict())

        if update:
            self.as_updateAnchorDataS(CustomizationAnchorInitVO(anchorVOs, doRegions)._asdict())
        else:
            self.as_setAnchorInitS(CustomizationAnchorInitVO(anchorVOs, doRegions)._asdict())
        return

    def __setHeaderInitData(self):
        vehicle = g_currentVehicle.item
        self.as_setHeaderDataS({'tankTier': str(int2roman(vehicle.level)),
         'tankName': vehicle.shortUserName,
         'tankType': '{}_elite'.format(vehicle.type) if vehicle.isElite else vehicle.type,
         'isElite': vehicle.isElite,
         'closeBtnTooltip': VEHICLE_CUSTOMIZATION.CUSTOMIZATION_HEADERCLOSEBTN,
         'historicVO': self.__getHistoricIndicatorData()})

    def __setFooterInitData(self):
        tabsData = self.__getItemTabsData()
        self._tabIndex = first(tabsData, {}).get('id')
        self.as_setBottomPanelInitDataS({'tabData': {'tabData': tabsData,
                     'selectedTab': self._tabIndex},
         'tabsAvailableRegions': C11nTabs.AVAILABLE_REGIONS,
         'defaultStyleLabel': VEHICLE_CUSTOMIZATION.DEFAULTSTYLE_LABEL,
         'carouselInitData': self.__getCarouselInitData(),
         'switcherInitData': self.__getSwitcherInitData()})
        self.as_setCarouselFiltersInitDataS({'popoverAlias': VIEW_ALIAS.CUSTOMIZATION_FILTER_POPOVER,
         'mainBtn': {'value': RES_ICONS.MAPS_ICONS_BUTTONS_FILTER,
                     'tooltip': VEHICLE_CUSTOMIZATION.CAROUSEL_FILTER_MAINBTN},
         'hotFilters': [{'value': RES_ICONS.MAPS_ICONS_CUSTOMIZATION_STORAGE_ICON,
                         'tooltip': VEHICLE_CUSTOMIZATION.CAROUSEL_FILTER_STORAGEBTN,
                         'selected': self._carouselDP.getOwnedFilter()}, {'value': RES_ICONS.MAPS_ICONS_BUTTONS_EQUIPPED_ICON,
                         'tooltip': VEHICLE_CUSTOMIZATION.CAROUSEL_FILTER_EQUIPPEDBTN,
                         'selected': self._carouselDP.getAppliedFilter()}]})

    def onSelectHotFilter(self, index, value):
        (self._carouselDP.setOwnedFilter, self._carouselDP.setAppliedFilter)[index](value)
        self.refreshCarousel(rebuild=True)

    def __getSwitcherInitData(self):
        return {'leftLabel': VEHICLE_CUSTOMIZATION.SWITCHER_NAME_CUSTSOMSTYLE,
         'rightLabel': VEHICLE_CUSTOMIZATION.SWITCHER_NAME_DEFAULTSTYLE,
         'leftEvent': 'installStyle',
         'rightEvent': 'installStyles',
         'isLeft': self._mode == C11nMode.CUSTOM}

    def __getHistoricIndicatorData(self):
        isDefault = all((outfit.isEmpty() for outfit in self._modifiedOutfits.itervalues()))
        if self._mode == C11nMode.STYLE:
            if self._modifiedStyle:
                isHistorical = self._modifiedStyle.isHistorical()
                name = self._modifiedStyle.userName
            else:
                isHistorical = True
                name = ''
        else:
            isHistorical = all((outfit.isHistorical() for outfit in self._modifiedOutfits.itervalues()))
            name = _ms(VEHICLE_CUSTOMIZATION.HISTORICINDICATOR_STYLENAME_CUSTSOMSTYLE) if not isDefault else ''
        txtStyle = text_styles.stats if isHistorical else text_styles.tutorial
        return {'historicText': txtStyle(toUpper(name)),
         'isDefaultAppearance': isDefault,
         'isHistoric': isHistorical,
         'tooltip': TOOLTIPS.CUSTOMIZATION_NONHISTORICINDICATOR if not isHistorical else ''}

    @staticmethod
    def __getCarouselInitData():
        return {'message': '{}{}\n{}'.format(icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_ATTENTIONICONFILLED, vSpace=-3), text_styles.neutral(VEHICLE_CUSTOMIZATION.CAROUSEL_MESSAGE_HEADER), text_styles.main(VEHICLE_CUSTOMIZATION.CAROUSEL_MESSAGE_DESCRIPTION))}

    def __getAnchorPositionData(self, slotId, region):
        if self._tabIndex in C11nTabs.REGIONS:
            anchorPos = self.service.getPointForRegionLeaderLine(region)
            anchorNorm = anchorPos
        else:
            anchorPos = self.service.getPointForAnchorLeaderLine(slotId.areaId, slotId.slotId, slotId.regionId)
            anchorNorm = self.service.getNormalForAnchorLeaderLine(slotId.areaId, slotId.slotId, slotId.regionId)
        return None if anchorPos is None or anchorNorm is None else AnchorPositionData(cameras.get2DAngleFromCamera(anchorNorm), cameras.projectPoint(anchorPos), slotId)

    def __getItemTabsData(self):
        data = []
        for tabIdx in self.__getVisibleTabs():
            itemTypeID = TABS_ITEM_MAPPING[tabIdx]
            typeName = GUI_ITEM_TYPE_NAMES[itemTypeID]
            data.append({'label': _ms(ITEM_TYPES.customizationPlural(typeName)),
             'tooltip': makeTooltip(ITEM_TYPES.customizationPlural(typeName), TOOLTIPS.customizationItemTab(typeName)),
             'id': tabIdx})

        return data

    def __getVisibleTabs(self):
        visibleTabs = []
        anchorsData = g_currentVehicle.hangarSpace.getSlotPositions()
        for tabIdx in C11nTabs.VISIBLE:
            if tabIdx == C11nTabs.CAMOUFLAGE and g_currentVehicle.item.descriptor.type.hasCustomDefaultCamouflage:
                continue
            itemTypeID = TABS_ITEM_MAPPING[tabIdx]
            data = self._carouselDP.getSeasonAndTabData(tabIdx, self._currentSeason)
            if not data.itemCount:
                continue
            if itemTypeID in (GUI_ITEM_TYPE.INSCRIPTION, GUI_ITEM_TYPE.EMBLEM):
                for areaData in anchorsData.itervalues():
                    if areaData.get(itemTypeID):
                        hasSlots = True
                        break
                else:
                    hasSlots = False

                if not hasSlots:
                    continue
            visibleTabs.append(tabIdx)

        return visibleTabs

    def __onNotifyHangarCameraIdleStateChanged(self, event):
        isIdle = event.ctx.get('started', False)
        self.as_cameraAutoRotateChangedS(isIdle)

    @async
    @adisp_process
    def __confirmHeaderNavigation(self, callback):
        purchaseItems = self.getPurchaseItems()
        cart = getTotalPurchaseInfo(purchaseItems)
        if cart.numTotal:
            result = yield DialogsInterface.showI18nConfirmDialog('customization/close')
        else:
            result = True
        callback(result)

    def __releaseItemSound(self):
        if self.itemIsPicked:
            self.soundManager.playInstantSound(SOUNDS.RELEASE)
            self.itemIsPicked = False

    def __onSettingsChanged(self, diff):
        if GAME.HANGAR_CAM_PARALLAX_ENABLED in diff:
            self.__updateCameraParalaxFlag()

    def __updateCameraParalaxFlag(self):
        paralaxEnabled = bool(self.settingsCore.getSetting(GAME.HANGAR_CAM_PARALLAX_ENABLED))
        self.as_setParallaxFlagS(paralaxEnabled)

    def __onInterfaceScaleChanged(self, scale):
        if self._vehicleCustomizationAnchorsUpdater is not None:
            self._vehicleCustomizationAnchorsUpdater.setInterfaceScale(scale)
        return
