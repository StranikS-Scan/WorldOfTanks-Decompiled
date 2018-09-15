# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/main_view.py
import math
import BigWorld
from collections import namedtuple
from functools import partial
from adisp import async
from AvatarInputHandler import cameras, mathUtils
from CurrentVehicle import g_currentVehicle
from account_helpers.settings_core.settings_constants import GRAPHICS
from gui import DialogsInterface, g_tankActiveCamouflage, makeHtmlString, SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.dialogs import I18nConfirmDialogMeta, DIALOG_BUTTON_ID, HtmlMessageLocalDialogMeta
from gui.Scaleform.daapi.view.lobby.customization import CustomizationItemCMHandler
from gui.Scaleform.daapi.view.lobby.customization.customization_carousel import CustomizationCarouselDataProvider
from gui.Scaleform.daapi.view.lobby.customization.customization_cm_handlers import CustomizationOptions
from gui.Scaleform.daapi.view.lobby.customization.customization_item_vo import buildCustomizationItemDataVO
from gui.Scaleform.daapi.view.lobby.customization.shared import C11N_MODE, CUSTOMIZATION_POPOVER_ALIASES, TABS_ITEM_MAPPING, CUSTOMIZATION_TABS, SEASON_IDX_TO_TYPE, SEASON_TYPE_TO_NAME, SEASONS_ORDER, getCustomPurchaseItems, getStylePurchaseItems, getTotalPurchaseInfo, OutfitInfo, getItemInventoryCount, getStyleInventoryCount, AdditionalPurchaseGroups
from gui.Scaleform.framework.entities.View import ViewKey, ViewKeyDynamic
from gui.Scaleform.framework.managers.view_lifecycle_watcher import IViewLifecycleHandler, ViewLifecycleWatcher
from gui.Scaleform.genConsts.CUSTOMIZATION_ALIASES import CUSTOMIZATION_ALIASES
from gui.Scaleform.daapi.view.meta.CustomizationMainViewMeta import CustomizationMainViewMeta
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.Scaleform.locale.VEHICLE_CUSTOMIZATION import VEHICLE_CUSTOMIZATION
from gui.Scaleform.locale.ITEM_TYPES import ITEM_TYPES
from gui.shared import events, g_eventBus
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.formatters import text_styles, icons, getItemPricesVO
from gui.shared.gui_items import GUI_ITEM_TYPE, GUI_ITEM_TYPE_NAMES
from gui.shared.gui_items.customization.outfit import Area
from gui.shared.gui_items.gui_item_economics import ITEM_PRICE_EMPTY
from gui.shared.gui_items.processors.common import OutfitApplier, StyleApplier, CustomizationsSeller
from gui.shared.utils.HangarSpace import g_hangarSpace
from gui.shared.utils.decorators import process
from gui.shared.utils.functions import makeTooltip
from helpers import dependency, int2roman
from helpers.i18n import makeString as _ms
from items.components.c11n_constants import SeasonType
from shared_utils import first
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from gui.Scaleform.daapi.view.dialogs.confirm_customization_item_dialog_meta import ConfirmCustomizationItemMeta
from gui.shared.utils import toUpper

class _C11nWindowsLifecycleHandler(IViewLifecycleHandler):
    """ Class responsible for suspending highlighter whenever modal windows pops up.
    """
    service = dependency.descriptor(ICustomizationService)
    __SUB_VIEWS = (VIEW_ALIAS.SETTINGS_WINDOW, VIEW_ALIAS.CUSTOMIZATION_PURCHASE_WINDOW, VIEW_ALIAS.LOBBY_MENU)
    __DIALOGS = (VIEW_ALIAS.SIMPLE_DIALOG, CUSTOMIZATION_ALIASES.CONFIRM_CUSTOMIZATION_ITEM_DIALOG)

    def __init__(self):
        super(_C11nWindowsLifecycleHandler, self).__init__([ ViewKey(alias) for alias in self.__SUB_VIEWS ] + [ ViewKeyDynamic(alias) for alias in self.__DIALOGS ])

    def onViewCreated(self, _):
        self.service.suspendHighlighter()

    def onViewDestroyed(self, _):
        self.service.resumeHighlighter()


def _getSellItemDialogMeta(customizationItem):
    """
    Creates the meta object used for populating the sell back dialog
    :param customizationItem: customization item to build from
    :return: new instance of I18nConfirmDialogMeta for building the sell dialog
    """
    itemSellPrice = customizationItem.getSellPrice()
    creditPrice = itemSellPrice.price.credits
    l10nParams = {'price': creditPrice,
     'name': customizationItem.userName}
    return I18nConfirmDialogMeta('customizationConfirmSell', meta=HtmlMessageLocalDialogMeta('html_templates:lobby/dialogs', 'customizationConfirmSell', ctx=l10nParams), focusedID=DIALOG_BUTTON_ID.CLOSE)


CustomizationCarouselDataVO = namedtuple('CustomizationCarouselDataVO', ('displayString', 'isZeroCount', 'shouldShow', 'itemLayoutSize', 'bookmarks'))
CustomizationAnchorInitVO = namedtuple('CustomizationAnchorInitVO', ('anchorUpdateVOs', 'doRegions'))
CustomizationSlotUpdateVO = namedtuple('CustomizationSlotUpdateVO', ('slotId', 'propertySheetAlias', 'itemIntCD'))
CustomizationSlotIdVO = namedtuple('CustomizationSlotIdVO', ('areaId', 'slotId', 'regionId'))
CustomizationAnchorsSetVO = namedtuple('CustomizationAnchorsSetVO', ('rendererList',))
CustomizationAnchorPositionVO = namedtuple('CustomizationAnchorPositionVO', ('clipX', 'clipY', 'alpha', 'scale', 'zIndex', 'slotId'))
AnchorPositionData = namedtuple('AnchorPositionData', ('angleToCamera', 'clipSpacePos', 'slotId'))
ANCHOR_UPDATE_TIMER_DELAY = 2
ANCHOR_UPDATE_FREQUENCY = 1 / 30
ANCHOR_FADE_EXPO = 1.1
ANCHOR_ALPHA_MIN = 0.15

class MainView(CustomizationMainViewMeta):
    lobbyContext = dependency.descriptor(ILobbyContext)
    itemsCache = dependency.descriptor(IItemsCache)
    service = dependency.descriptor(ICustomizationService)
    settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, ctx=None):
        super(MainView, self).__init__()
        self.__viewLifecycleWatcher = ViewLifecycleWatcher()
        self.fadeAnchorsOut = False
        self.anchorMinScale = 0.75
        self._currentSeason = SeasonType.SUMMER
        self._tabIndex = CUSTOMIZATION_TABS.PAINT
        self._lastTab = CUSTOMIZATION_TABS.PAINT
        self._originalStyle = None
        self._modifiedStyle = None
        self._originalOutfits = {}
        self._modifiedOutfits = {}
        self._currentOutfit = None
        self._mode = C11N_MODE.CUSTOM
        self._isDeferredRenderer = True
        self.__anchorPositionCallbackID = None
        self._state = {}
        self.__hangarSpace = g_hangarSpace.space
        self.__locatedOnEmbelem = False
        return

    def showBuyWindow(self):
        """  Displays the purchase / buy window or apply immediately.
        """
        purchaseItems = self.getPurchaseItems()
        cart = getTotalPurchaseInfo(purchaseItems)
        if cart.totalPrice == ITEM_PRICE_EMPTY:
            self.buyAndExit(purchaseItems)
        else:
            self.as_hideAnchorPropertySheetS()
            self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.CUSTOMIZATION_PURCHASE_WINDOW), EVENT_BUS_SCOPE.LOBBY)

    def onSelectItem(self, index):
        """ Select item in the carousel
        """
        self._carouselDP.selectItemIdx(index)

    def changeSeason(self, seasonIdx):
        """ Change the current season.
        """
        self._currentSeason = SEASON_IDX_TO_TYPE[seasonIdx]
        self.refreshOutfit()
        self.refreshCarousel(rebuild=True)
        self.as_refreshAnchorPropertySheetS()
        doRegions = self._tabIndex in CUSTOMIZATION_TABS.REGIONS
        self.__setAnchorsInitData(self._tabIndex, doRegions, True)

    def refreshCarousel(self, rebuild=False):
        if rebuild:
            self._carouselDP.buildList(self._tabIndex, self._currentSeason, refresh=False)
            self.as_setCarouselDataS(self._buildCustomizationCarouselDataVO())
        self._carouselDP.refresh()

    def refreshOutfit(self):
        """ Apply any changes to the vehicle's 3d model.
        """
        if self._mode == C11N_MODE.STYLE:
            if self._modifiedStyle:
                self._currentOutfit = self._modifiedStyle.getOutfit(self._currentSeason)
            else:
                self._currentOutfit = self.service.getEmptyOutfit()
        else:
            self._currentOutfit = self._modifiedOutfits[self._currentSeason]
        self.service.tryOnOutfit(self._currentOutfit)
        g_tankActiveCamouflage[g_currentVehicle.item.intCD] = self._currentSeason

    def showGroupFromTab(self, tabIndex):
        """ This is called when a tab change occurs in the front end.
        
        Initialize the new anchor or region set for the new tab group.
        Rebuild the carousel's DAAPIDataProvider
        Build bookmark data and send to ActionScript
        
        :param tabIndex: index of the newly selected tab
        """
        self._tabIndex = tabIndex
        doRegions = self._tabIndex in CUSTOMIZATION_TABS.REGIONS
        if doRegions:
            self.service.startHighlighter(CUSTOMIZATION_TABS.REGIONS[self._tabIndex])
        else:
            self.service.stopHighlighter()
        self.__stopTimer()
        self.__setAnchorsInitData(self._tabIndex, doRegions)
        if self.__locatedOnEmbelem:
            self.__hangarSpace.clearSelectedEmblemInfo()
            self.__hangarSpace.locateCameraToPreview()
            self.__startTimer(ANCHOR_UPDATE_TIMER_DELAY, self.__updateAnchorPositions)
        else:
            self.__updateAnchorPositions()
        if self._tabIndex == CUSTOMIZATION_TABS.STYLE:
            slotIdVO = CustomizationSlotIdVO(0, GUI_ITEM_TYPE.STYLE, 0)._asdict()
        elif self._tabIndex == CUSTOMIZATION_TABS.EFFECT:
            slotIdVO = CustomizationSlotIdVO(Area.MISC, GUI_ITEM_TYPE.MODIFICATION, 0)._asdict()
        else:
            slotIdVO = None
        self.as_updateSelectedRegionsS(slotIdVO)
        self.refreshCarousel(rebuild=True)
        return

    def installCustomizationElement(self, intCD, areaId, slotId, regionId, seasonIdx):
        """ Install the given item on a vehicle.
        """
        item = self.itemsCache.items.getItemByCD(intCD)
        if self._mode == C11N_MODE.STYLE:
            self._modifiedStyle = item
        else:
            season = SEASON_IDX_TO_TYPE.get(seasonIdx, self._currentSeason)
            outfit = self._modifiedOutfits[season]
            outfit.getContainer(areaId).slotFor(slotId).set(item, idx=regionId)
            outfit.invalidate()
        self.refreshOutfit()
        self.__setBuyingPanelData()
        self.__setHeaderInitData()
        self.refreshCarousel(rebuild=False)

    def clearCustomizationItem(self, areaId, slotId, regionId, seasonIdx):
        """ Removes the item from the given region.
        (called from property sheet).
        """
        season = SEASON_IDX_TO_TYPE.get(seasonIdx, self._currentSeason)
        outfit = self._modifiedOutfits[season]
        outfit.getContainer(areaId).slotFor(slotId).remove(idx=regionId)
        self.refreshOutfit()
        doRegions = self._tabIndex in CUSTOMIZATION_TABS.REGIONS
        self.__setAnchorsInitData(self._tabIndex, doRegions, True)
        self.__setBuyingPanelData()
        self.__setHeaderInitData()
        self.refreshCarousel(rebuild=False)

    def switchToCustom(self, updateUI=True):
        """ Turn on the Custom customization mode
        (where you create vehicle's look by yourself).
        """
        self._mode = C11N_MODE.CUSTOM
        self._tabIndex = self._lastTab
        self.refreshOutfit()
        self.as_setBottomPanelTabsDataS({'tabData': self.__getItemTabsData(),
         'selectedTab': self._tabIndex})
        self._carouselDP.selectItem()
        self.__setBuyingPanelData()
        self.__setHeaderInitData()

    def switchToStyle(self):
        """ Turn on the Style customization mode
        (where you use predefined vehicle looks).
        """
        self._mode = C11N_MODE.STYLE
        self._lastTab = self._tabIndex
        self._tabIndex = CUSTOMIZATION_TABS.STYLE
        self.refreshOutfit()
        self.as_setBottomPanelTabsDataS({'tabData': self.__getItemTabsData(),
         'selectedTab': self._tabIndex})
        self._carouselDP.selectItem(self._modifiedStyle)
        self.__setBuyingPanelData()
        self.__setHeaderInitData()

    def fadeOutAnchors(self, isFadeOut):
        """ Set whether or not to fade anchors out
        """
        self.fadeAnchorsOut = isFadeOut

    def closeWindow(self):
        purchaseItems = self.getPurchaseItems()
        cart = getTotalPurchaseInfo(purchaseItems)
        if cart.numTotal:
            DialogsInterface.showDialog(I18nConfirmDialogMeta('customization/close'), self.__onConfirmCloseWindow)
        else:
            self.__onConfirmCloseWindow(proceed=True)

    def itemContextMenuDisplayed(self):
        """
        Actionscript initiated call that happens after the item context menu is displayed.
        Sets up an event for menu item presses
        """
        cmHandler = self.app.contextMenuManager.getCurrentHandler()
        if isinstance(cmHandler, CustomizationItemCMHandler):
            cmHandler.onSelected += self._itemCtxMenuSelected

    def resetFilter(self):
        """ Reset filter and rebuild carousel
        """
        self.clearFilter()
        self.refreshFilterData()
        self.refreshCarousel(rebuild=True)

    def clearFilter(self):
        """ Reset filter and rebuild carousel
        """
        self._carouselDP.clearFilter()

    def refreshFilterData(self):
        """ Send new filter data to AS3.
        """
        self.as_setFilterDataS(self._carouselDP.getFilterData())

    def getHistoricalPopoverData(self):
        """ Get the unhistorical items for the Unhistorical popover (in the header)
        """
        if self._mode == C11N_MODE.STYLE and self._modifiedStyle:
            if not self._modifiedStyle.isHistorical():
                return {'items': [self._modifiedStyle.intCD]}
            return {'items': []}
        items = []
        for outfit in self._modifiedOutfits.itervalues():
            items.extend((item.intCD for item in outfit.items() if not item.isHistorical()))

        return {'items': items}

    def removeItems(self, *intCDs):
        """ Remove the given item from every outfit.
        Don't care about mode there.
        """
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
        self.refreshCarousel(rebuild=False)
        return

    def updatePropertySheetButtons(self, areaId, slotId, regionId):
        self.service.onPropertySheetShow(areaId, slotId, regionId)

    def onLobbyClick(self):
        if self._tabIndex in (CUSTOMIZATION_TABS.EMBLEM, CUSTOMIZATION_TABS.INSCRIPTION):
            self.as_hideAnchorPropertySheetS()
        if self.__locatedOnEmbelem:
            self.__stopTimer()
            self.__hangarSpace.clearSelectedEmblemInfo()
            self.__hangarSpace.locateCameraToPreview()
            self.__startTimer(ANCHOR_UPDATE_TIMER_DELAY, self.__updateAnchorPositions)

    def setEnableMultiselectRegions(self, isEnabled):
        """ Turn off highlighting when doing pick'n'click.
        """
        self.service.setSelectHighlighting(isEnabled)

    def onChangeSize(self):
        self.__updateAnchorPositions()

    def onSelectAnchor(self, areaID, regionID):
        if self._tabIndex == CUSTOMIZATION_TABS.EMBLEM:
            emblemType = 'player'
            zoom = 0.06
        else:
            emblemType = 'inscription'
            zoom = 0.1
        self.__stopTimer()
        self.__startTimer(ANCHOR_UPDATE_TIMER_DELAY, self.__updateAnchorPositions)
        self.__locatedOnEmbelem = self.__hangarSpace.locateCameraOnEmblem(areaID < 2, emblemType, regionID, zoom)

    def getOutfitsInfo(self):
        outfitsInfo = {}
        for season in SEASONS_ORDER:
            outfitsInfo[season] = OutfitInfo(self._originalOutfits[season], self._modifiedOutfits[season])

        return outfitsInfo

    def getStyleInfo(self):
        return OutfitInfo(self._originalStyle, self._modifiedStyle)

    def getPurchaseItems(self):
        return getCustomPurchaseItems(self.getOutfitsInfo()) if self._mode == C11N_MODE.CUSTOM else getStylePurchaseItems(self.getStyleInfo())

    def getItemInventoryCount(self, item):
        return getItemInventoryCount(item, self.getOutfitsInfo()) if self._mode == C11N_MODE.CUSTOM else getStyleInventoryCount(item, self.getStyleInfo())

    def getCurrentOutfit(self):
        """ Returns current outfit applied on the vehicle.
        """
        return self._currentOutfit

    def getModifiedStyle(self):
        """ Returns current style applied on the vehicle.
        """
        return self._modifiedStyle

    def getModifiedOutfit(self, season):
        """ Returns modified outfit for the given season.
        """
        return self._modifiedOutfits.get(season)

    def getMode(self):
        return self._mode

    def getCurrentSeason(self):
        return self._currentSeason

    def isItemInOutfit(self, item):
        """ Check if item is in any outfit.
        """
        return any((outfit.has(item) for outfit in self._originalOutfits.itervalues())) or any((outfit.has(item) for outfit in self._modifiedOutfits.itervalues()))

    @process('buyAndInstall')
    def buyAndExit(self, purchaseItems):
        self.itemsCache.onSyncCompleted -= self.__onCacheResync
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

        if self._mode == C11N_MODE.CUSTOM and bool(self._originalStyle):
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
            self.__onConfirmCloseWindow(proceed=True)
        else:
            self.__onCacheResync()
        self.itemsCache.onSyncCompleted += self.__onCacheResync

    def _populate(self):
        super(MainView, self)._populate()
        self.__viewLifecycleWatcher.start(self.app.containerManager, [_C11nWindowsLifecycleHandler()])
        self._isDeferredRenderer = self.settingsCore.getSetting(GRAPHICS.RENDER_PIPELINE) == 0
        g_clientUpdateManager.addMoneyCallback(self.__setBuyingPanelData)
        self.lobbyContext.addHeaderNavigationConfirmator(self.__confirmHeaderNavigation)
        self.lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingChanged
        self.service.onCarouselFilter += self.__onCarouselFilter
        self.service.onRemoveItems += self.removeItems
        self.service.onOutfitChanged += self.__onOutfitChanged
        g_eventBus.addListener(events.LobbySimpleEvent.NOTIFY_SPACE_MOVED, self.__onNotifySpaceMoved)
        g_eventBus.addListener(events.LobbySimpleEvent.NOTIFY_CURSOR_DRAGGING, self.__onNotifyCursorDragging)
        g_hangarSpace.onSpaceCreate += self.__onSpaceCreateHandler
        self.service.onRegionHighlighted += self.__onRegionHighlighted
        self.itemsCache.onSyncCompleted += self.__onCacheResync
        self.__carveUpOutfits()
        if self._modifiedStyle:
            self._mode = C11N_MODE.STYLE
        else:
            self._mode = C11N_MODE.CUSTOM
        self._carouselDP = CustomizationCarouselDataProvider(g_currentVehicle, self._carouseItemWrapper, self)
        self._carouselDP.setFlashObject(self.as_getDataProviderS())
        self._carouselDP.setEnvironment(self.app)
        self.__setHeaderInitData()
        self.__setFooterInitData()
        self.__setBuyingPanelData()
        self.__setSeasonData()
        self.refreshOutfit()

    def _dispose(self):
        if self.__locatedOnEmbelem:
            self.__hangarSpace.clearSelectedEmblemInfo()
            self.__hangarSpace.locateCameraToPreview()
        self.__viewLifecycleWatcher.stop()
        self.__stopTimer()
        self.service.stopHighlighter()
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.lobbyContext.deleteHeaderNavigationConfirmator(self.__confirmHeaderNavigation)
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingChanged
        self.service.onCarouselFilter -= self.__onCarouselFilter
        self.service.onRemoveItems -= self.removeItems
        self.service.onOutfitChanged -= self.__onOutfitChanged
        g_eventBus.removeListener(events.LobbySimpleEvent.NOTIFY_SPACE_MOVED, self.__onNotifySpaceMoved)
        g_eventBus.removeListener(events.LobbySimpleEvent.NOTIFY_CURSOR_DRAGGING, self.__onNotifyCursorDragging)
        g_hangarSpace.onSpaceCreate -= self.__onSpaceCreateHandler
        self.service.onRegionHighlighted -= self.__onRegionHighlighted
        self.itemsCache.onSyncCompleted -= self.__onCacheResync
        if g_currentVehicle.item:
            g_tankActiveCamouflage[g_currentVehicle.item.intCD] = self._currentSeason
            g_currentVehicle.refreshModel()
        super(MainView, self)._dispose()

    def _itemCtxMenuSelected(self, ctxMenuID, itemIntCD):
        """ Event notification for when a item context menu is pressed
        
        :param ctxMenuID: ID of the menu item pressed
        :param itemIntCD: item CD for fetching the correct item
        """
        item = self.itemsCache.items.getItemByCD(itemIntCD)
        if ctxMenuID == CustomizationOptions.BUY:
            DialogsInterface.showDialog(ConfirmCustomizationItemMeta(itemIntCD), lambda _: None)
        elif ctxMenuID == CustomizationOptions.SELL:

            @process('sellItem')
            def __confirmSellResultCallback(shouldSell):
                """ Callback for Dialog sale customization icon
                :param shouldSell: If true, user pressed 'OK',
                                   false - 'Decline' or 'Close' button
                """
                if shouldSell:
                    yield CustomizationsSeller(g_currentVehicle.item, item).request()

            DialogsInterface.showI18nConfirmDialog('customizationConfirmSell', __confirmSellResultCallback, focusedID=DIALOG_BUTTON_ID.CLOSE, meta=_getSellItemDialogMeta(item))
        elif ctxMenuID == CustomizationOptions.REMOVE_FROM_TANK:
            self.removeItems(item.intCD)

    def _getUpdatedAnchorPositions(self):
        anchorVOs = []
        anchorPosData = []
        cType = TABS_ITEM_MAPPING[self._tabIndex]
        if self._tabIndex == CUSTOMIZATION_TABS.STYLE:
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

        anchorPosData.sort(key=lambda pos: pos.angleToCamera)
        for zIdx, posData in enumerate(anchorPosData):
            alpha = (posData.angleToCamera / math.pi) ** ANCHOR_FADE_EXPO
            alpha = mathUtils.clamp(ANCHOR_ALPHA_MIN, 1, alpha)
            if posData.angleToCamera > math.pi / 2:
                scale = (1 - self.anchorMinScale) * 2 * posData.angleToCamera / math.pi + 2 * self.anchorMinScale - 1
            else:
                scale = self.anchorMinScale
            anchorVOs.append(CustomizationAnchorPositionVO(posData.clipSpacePos.x, posData.clipSpacePos.y, alpha, scale, zIdx, posData.slotId._asdict())._asdict())

        return CustomizationAnchorsSetVO(anchorVOs)._asdict()

    def _buildCustomizationCarouselDataVO(self):
        """ Builds and returns a CustomizationCarouselDataVO, which handles bookmarks.
        
        :return: CustomizationCarouselDataVO with information on bookmarks.
        """
        isZeroCount = False
        if self._carouselDP.itemCount == 0:
            displayString = makeHtmlString('html_templates:lobby/customization', 'filterCounterZero', {'displayCount': str(self._carouselDP.itemCount),
             'totalCount': str(self._carouselDP.totalItemCount)})
            isZeroCount = True
        else:
            displayString = '{}/{}'.format(self._carouselDP.itemCount, self._carouselDP.totalItemCount)
        shouldShow = self._carouselDP.itemCount < self._carouselDP.totalItemCount
        return CustomizationCarouselDataVO(displayString, isZeroCount, shouldShow, itemLayoutSize=self._carouselDP.getItemSizeData(), bookmarks=self._carouselDP.getBookmarkData())._asdict()

    def _carouseItemWrapper(self, itemCD):
        item = self.itemsCache.items.getItemByCD(itemCD)
        itemInventoryCount = self.getItemInventoryCount(item)
        if item.itemTypeID == GUI_ITEM_TYPE.MODIFICATION:
            showUnsupportedAlert = not self._isDeferredRenderer
        else:
            showUnsupportedAlert = False
        return buildCustomizationItemDataVO(item, itemInventoryCount, showUnsupportedAlert=showUnsupportedAlert)

    def __carveUpOutfits(self):
        """ Fill up the internal structures with vehicle's outfits.
        """
        for season in SeasonType.COMMON_SEASONS:
            outfit = self.service.getCustomOutfit(season)
            self._originalOutfits[season] = outfit.copy()
            self._modifiedOutfits[season] = outfit.copy()

        style = self.service.getCurrentStyle()
        self._originalStyle = style
        self._modifiedStyle = style
        if style:
            self._currentOutfit = style.getOutfit(self._currentSeason)
        else:
            self._currentOutfit = self._modifiedOutfits[self._currentSeason]

    def __updateAnchorPositions(self, _=None):
        self.as_setAnchorPositionsS(self._getUpdatedAnchorPositions())

    def __onRegionHighlighted(self, typeID, tankPartID, regionID):
        slotId = None
        if self._tabIndex == CUSTOMIZATION_TABS.EFFECT:
            tankPartID = Area.MISC
            typeID = GUI_ITEM_TYPE.MODIFICATION
        if tankPartID != -1 and regionID != -1:
            slotId = CustomizationSlotIdVO(tankPartID, typeID, regionID)._asdict()
        self.as_onRegionHighlightedS(slotId)
        return

    def __onSpaceCreateHandler(self):
        self.refreshOutfit()
        self.__updateAnchorPositions()

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
        self.refreshCarousel(rebuild=True)

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
        if self._mode == C11N_MODE.CUSTOM:
            self.as_hideAnchorPropertySheetS()
        self.refreshCarousel(rebuild=False)
        self.refreshOutfit()

    def __preserveState(self):
        self._state.update(modifiedStyle=self._modifiedStyle, modifiedOutfits={season:outfit.copy() for season, outfit in self._modifiedOutfits.iteritems()})

    def __restoreState(self):
        self._modifiedStyle = self._state.get('modifiedStyle')
        self._modifiedOutfits = self._state.get('modifiedOutfits')
        self._state.clear()

    def __onServerSettingChanged(self, diff):
        if 'isCustomizationEnabled' in diff and not diff.get('isCustomizationEnabled', True):
            SystemMessages.pushI18nMessage(SYSTEM_MESSAGES.CUSTOMIZATION_UNAVAILABLE, type=SystemMessages.SM_TYPE.Warning)
            self.__onConfirmCloseWindow(proceed=True)

    def __setBuyingPanelData(self, *_):
        """ Update the buying panel according to the current state of cart.
        """
        purchaseItems = self.getPurchaseItems()
        cart = getTotalPurchaseInfo(purchaseItems)
        totalPriceVO = getItemPricesVO(cart.totalPrice)
        if cart.totalPrice != ITEM_PRICE_EMPTY:
            label = _ms(VEHICLE_CUSTOMIZATION.COMMIT_BUY)
            self.as_showBuyingPanelS()
        else:
            label = _ms(VEHICLE_CUSTOMIZATION.COMMIT_APPLY)
            self.as_hideBuyingPanelS()
        isApplyEnabled = bool(cart.numTotal) or self._mode == C11N_MODE.CUSTOM and bool(self._originalStyle)
        isEnoughMoney = not self.itemsCache.items.stats.money.getShortage(cart.totalPrice.price)
        self.as_setBottomPanelHeaderS({'enoughMoney': isEnoughMoney,
         'buyBtnEnabled': isApplyEnabled,
         'buyBtnLabel': label,
         'pricePanel': totalPriceVO[0]})

    def __setSeasonData(self):
        seasonRenderersList = []
        for season in SEASONS_ORDER:
            seasonName = SEASON_TYPE_TO_NAME.get(season)
            seasonRenderersList.append({'seasonName': VEHICLE_CUSTOMIZATION.getSeasonName(seasonName),
             'seasonIconSmall': RES_ICONS.getSeasonIcon(seasonName)})

        self.as_setSeasonPanelDataS({'seasonRenderersList': seasonRenderersList})

    def __setAnchorsInitData(self, tabIndex, doRegions, update=False):
        anchorVOs = []
        cType = TABS_ITEM_MAPPING[tabIndex]
        if tabIndex == CUSTOMIZATION_TABS.STYLE:
            slotId = CustomizationSlotIdVO(0, GUI_ITEM_TYPE.STYLE, 0)
            popoverAlias = CUSTOMIZATION_POPOVER_ALIASES[GUI_ITEM_TYPE.STYLE]
            anchorVOs.append(CustomizationSlotUpdateVO(slotId._asdict(), popoverAlias, -1)._asdict())
        else:
            for container in self._currentOutfit.containers():
                for slot in (x for x in container.slots() if x.getType() == cType):
                    for regionId, region in enumerate(slot.getRegions()):
                        slotId = CustomizationSlotIdVO(container.getAreaID(), slot.getType(), regionId)
                        popoverAlias = CUSTOMIZATION_POPOVER_ALIASES[slot.getType()]
                        item = slot.getItem(regionId)
                        itemIntCD = item.intCD if item is not None else 0
                        if self.__getAnchorPositionData(slotId, region) is not None:
                            anchorVOs.append(CustomizationSlotUpdateVO(slotId._asdict(), popoverAlias, itemIntCD)._asdict())

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
         'tabsAvailableRegions': CUSTOMIZATION_TABS.AVAILABLE_REGIONS,
         'defaultStyleLabel': VEHICLE_CUSTOMIZATION.DEFAULTSTYLE_LABEL,
         'carouselInitData': self.__getCarouselInitData(),
         'switcherInitData': self.__getSwitcherInitData()})

    def __getSwitcherInitData(self):
        """ Switcher is a style/custom selector.
        """
        return {'leftLabel': VEHICLE_CUSTOMIZATION.SWITCHER_NAME_CUSTSOMSTYLE,
         'rightLabel': VEHICLE_CUSTOMIZATION.SWITCHER_NAME_DEFAULTSTYLE,
         'leftEvent': 'installStyle',
         'rightEvent': 'installStyles',
         'isLeft': self._mode == C11N_MODE.CUSTOM}

    def __getHistoricIndicatorData(self):
        """ Historicity indicator and name of the current style or custom outfit.
        """
        isDefault = all((outfit.isEmpty() for outfit in self._modifiedOutfits.itervalues()))
        if self._mode == C11N_MODE.STYLE:
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
        return {'icoFilter': RES_ICONS.MAPS_ICONS_BUTTONS_FILTER,
         'message': '{}{}\n{}'.format(icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_ATTENTIONICONFILLED, vSpace=-3), text_styles.neutral(VEHICLE_CUSTOMIZATION.CAROUSEL_MESSAGE_HEADER), text_styles.main(VEHICLE_CUSTOMIZATION.CAROUSEL_MESSAGE_DESCRIPTION)),
         'filterTooltip': VEHICLE_CUSTOMIZATION.CAROUSEL_FILTER}

    def __getAnchorPositionData(self, slotId, region):
        if self._tabIndex in CUSTOMIZATION_TABS.REGIONS:
            anchorPos = self.service.getPointForRegionLeaderLine(region)
            anchorNorm = anchorPos
        else:
            anchorPos = self.service.getPointForAnchorLeaderLine(slotId.areaId, slotId.slotId, slotId.regionId)
            anchorNorm = self.service.getNormalForAnchorLeaderLine(slotId.areaId, slotId.slotId, slotId.regionId)
        return None if anchorPos is None or anchorNorm is None else AnchorPositionData(cameras.get2DAngleFromCamera(anchorNorm), cameras.projectPoint(anchorPos), slotId)

    def __getItemTabsData(self):
        """ Tabs with customization items.
        """
        data = []
        for tabIdx in self.__getVisibleTabs():
            itemTypeID = TABS_ITEM_MAPPING[tabIdx]
            typeName = GUI_ITEM_TYPE_NAMES[itemTypeID]
            data.append({'label': _ms(ITEM_TYPES.customizationPlural(typeName)),
             'tooltip': makeTooltip(ITEM_TYPES.customizationPlural(typeName), TOOLTIPS.customizationItemTab(typeName)),
             'id': tabIdx})

        return data

    def __getVisibleTabs(self):
        """ Get tabs that are actually visible.
        """
        visibleTabs = []
        anchorsData = g_currentVehicle.hangarSpace.getSlotPositions()
        for tabIdx in CUSTOMIZATION_TABS.VISIBLE:
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

    def __onNotifySpaceMoved(self, _):
        if self.__anchorPositionCallbackID is None:
            self.__startTimer(ANCHOR_UPDATE_TIMER_DELAY, self.__updateAnchorPositions)
        return

    def __onNotifyCursorDragging(self, event):
        isDragging = event.ctx.get('isDragging', False)
        if not isDragging and self.__anchorPositionCallbackID is None:
            self.__startTimer(ANCHOR_UPDATE_TIMER_DELAY, self.__updateAnchorPositions)
        return

    def __startTimer(self, delay, handler):
        self.__finishTime = BigWorld.time() + delay
        self.__updateTimer(handler)

    def __updateTimer(self, handler):
        if BigWorld.time() < self.__finishTime:
            self.__anchorPositionCallbackID = BigWorld.callback(ANCHOR_UPDATE_FREQUENCY, partial(self.__updateTimer, handler))
            handler()
        else:
            self.__stopTimer()

    def __stopTimer(self):
        if self.__anchorPositionCallbackID is not None:
            BigWorld.cancelCallback(self.__anchorPositionCallbackID)
            self.__anchorPositionCallbackID = None
            self.__finishTime = 0
        return

    @async
    def __confirmHeaderNavigation(self, callback):
        purchaseItems = self.getPurchaseItems()
        cart = getTotalPurchaseInfo(purchaseItems)
        if cart.numTotal:
            DialogsInterface.showI18nConfirmDialog('customization/close', callback)
        else:
            callback(True)
