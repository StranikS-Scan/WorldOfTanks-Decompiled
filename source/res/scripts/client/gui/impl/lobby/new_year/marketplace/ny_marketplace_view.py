# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/marketplace/ny_marketplace_view.py
import BigWorld
import logging
import typing
from functools import partial
from itertools import chain
from operator import itemgetter
from CurrentVehicle import g_currentPreviewVehicle, g_currentVehicle
from gui import SystemMessages
from gui.Scaleform.daapi.view.lobby.vehicle_preview.items_kit_helper import getSuitableStyledVehicle
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.ny_constants import Resource
from gui.impl.gen.view_models.views.lobby.new_year.views.marketplace.card_model import CardModel
from gui.impl.gen.view_models.views.lobby.new_year.views.marketplace.ny_marketplace_view_model import KitState, VehicleState
from gui.impl.lobby.new_year.dialogs.marketplace.market_purchase_dialog import MarketPurchaseDialogView
from gui.impl.lobby.new_year.marketplace import getMarketRewards, getMarketItemBonusesFromItem, getSettingsName, bonusChecker, showStyleFromMarketPlace
from gui.impl.lobby.new_year.ny_selectable_logic_presenter import SelectableLogicPresenter
from gui.impl.lobby.new_year.scene_rotatable_view import SceneRotatableView
from gui.impl.lobby.new_year.tooltips.ny_market_card_tooltip import NyMarketCardTooltip
from gui.impl.lobby.new_year.tooltips.ny_market_discount_tooltip import NyMarketDiscountTooltip
from gui.impl.lobby.new_year.tooltips.ny_market_lack_the_res_tooltip import NyMarketLackTheResTooltip
from gui.impl.new_year.navigation import NewYearNavigation
from gui.impl.new_year.new_year_helper import backportTooltipDecorator
from gui.server_events.bonuses import CustomizationsBonus
from gui.shared import EVENT_BUS_SCOPE
from gui.shared.events import NyMarketPlaceRewardEvent
from gui.shared.event_dispatcher import showNyMarketplaceRewardsWindow
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.notifications import NotificationPriorityLevel
from gui.shared.utils import decorators
from gui.shared.view_helpers.blur_manager import CachedBlur
from helpers import dependency
from items import vehicles
from items.components.ny_constants import NY_CURRENCY_NAME_TO_IDX, NyCurrency
from new_year.ny_constants import NyWidgetTopMenu, Collections, NyTabBarMarketplaceView, SyncDataKeys
from new_year.ny_marketplace_helper import getNYMarketplaceConfig, isCollectionItemReceived
from new_year.ny_processor import BuyMarketplaceItemProcessor
from shared_utils import findFirst, first
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.game_control import IHeroTankController
from skeletons.gui.shared.utils import IHangarSpace
from skeletons.new_year import INewYearController
_logger = logging.getLogger(__name__)
if typing.TYPE_CHECKING:
    from gui.shared.event_dispatcher import NYTabCtx
    from gui.impl.gen.view_models.views.lobby.new_year.views.marketplace.ny_marketplace_view_model import NyMarketplaceViewModel
_DEFAULT_VEHICLE = 'germany:G42_Maus'
_DEFAULT_VEHICLES_2018 = {'soviet': 'ussr:R45_IS-7',
 'traditionalWestern': 'france:F10_AMX_50B',
 'modernWestern': 'japan:J20_Type_2605',
 'asian': 'china:Ch41_WZ_111_5A'}
_EASING_TRANSITION_DURATION = 0.8

class _KitSettings(object):

    def __init__(self):
        self.__yearName = ''
        self.__kitId = 0
        self.__resource = Resource.CRYSTAL
        self.__styleID = None
        self.__openStyleOnVehicleInvID = None
        self.__findNotRecived = True
        return

    @property
    def yearName(self):
        return self.__yearName

    @property
    def kitId(self):
        return self.__kitId

    @property
    def resource(self):
        return self.__resource

    @property
    def resourceValue(self):
        return self.__resource.value

    @property
    def styleID(self):
        return self.__styleID

    @property
    def openStyleOnVehicle(self):
        return self.__openStyleOnVehicleInvID

    @property
    def findNotRecived(self):
        return self.__findNotRecived

    def getCategoryIndex(self):
        return NyTabBarMarketplaceView.REVERSED_ALL.index(self.__yearName)

    def getResourceIndex(self):
        return NY_CURRENCY_NAME_TO_IDX.get(self.resourceValue)

    def setYearName(self, value):
        self.__yearName = value

    def setKitId(self, value):
        self.__kitId = value

    def setResource(self, value):
        self.__resource = value

    def setStyleID(self, value):
        self.__styleID = value

    def setOpenStyleOnVehicle(self, value):
        self.__openStyleOnVehicleInvID = value

    def setFindNotRecived(self, value):
        self.__findNotRecived = value


class NyMarketplaceView(SceneRotatableView, SelectableLogicPresenter):
    __slots__ = ('_tooltips', '__settings', '__needToResetAppearance', '__needResetBloor', '__cameraCallbackId', '__blur', '__tabName')
    _VEHICLE_COLLISION_AUTO_ACTIVATE = True
    __hangarSpace = dependency.descriptor(IHangarSpace)
    __service = dependency.descriptor(ICustomizationService)
    __nyController = dependency.descriptor(INewYearController)
    __heroTankController = dependency.descriptor(IHeroTankController)

    def __init__(self, viewModel, parentView, *args, **kwargs):
        super(NyMarketplaceView, self).__init__(viewModel, parentView, *args, **kwargs)
        self._tooltips = {}
        self.__settings = _KitSettings()
        self.__needToResetAppearance = False
        self.__needResetBloor = False
        self.__cameraCallbackId = None
        self.__blur = None
        _, self.__tabName = self.__nyController.getFirstNonReceivedMarketPlaceCollectionData()
        return

    def initialize(self, *args, **kwargs):
        super(NyMarketplaceView, self).initialize(args, kwargs)
        self.__blur = CachedBlur(fadeTime=_EASING_TRANSITION_DURATION)
        tabName = self._tabCache.getMarketplaceTab() or self.__tabName
        self.__settings.setResource(max([ (r, self._nyController.currencies.getResouceBalance(r.value)) for r in Resource ], key=itemgetter(1))[0])
        self.__heroTankController.setInteractive(False)
        self.__hangarSpace.setVehicleSelectable(False)
        self.__onTabSelect(tabName, kitIdx=self.__settings.kitId, forced=True)

    def finalize(self):
        self.__doClear()
        super(NyMarketplaceView, self).finalize()

    def clear(self):
        self.__settings = None
        super(NyMarketplaceView, self).clear()
        return

    @backportTooltipDecorator()
    def createToolTip(self, event):
        return super(NyMarketplaceView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.new_year.tooltips.NyMarketDiscountTooltip():
            return NyMarketDiscountTooltip(int(event.getArgument('discount')), str(event.getArgument('collection')), str(event.getArgument('year')))
        if contentID == R.views.lobby.new_year.tooltips.NyMarketLackTheResTooltip():
            return NyMarketLackTheResTooltip(str(event.getArgument('resourceType')), int(event.getArgument('price')))
        return NyMarketCardTooltip(str(event.getArgument('kitState')), str(event.getArgument('kitName')), str(event.getArgument('currentTabName')), int(event.getArgument('kitIndex')), str(event.getArgument('currentResource'))) if contentID == R.views.lobby.new_year.tooltips.NyMarketCardTooltip() else super(NyMarketplaceView, self).createToolTipContent(event, contentID)

    @property
    def viewModel(self):
        return self.getViewModel()

    def _getEvents(self):
        events = super(NyMarketplaceView, self)._getEvents()
        return events + ((self.viewModel.kit.onBuy, self.__onKitBuy),
         (self.viewModel.kit.onSwitchResource, self.__onKitSwitchResource),
         (self.viewModel.kit.onOpenStyle, self.__onKitOpenStyle),
         (self.viewModel.onSwitchKit, self.__onCardsSwitchKit),
         (NewYearNavigation.onSidebarSelected, self.__onSideBarSelected),
         (NewYearNavigation.onPreSwitchView, self.__onPreSwitchViewEvent),
         (self.__hangarSpace.onVehicleChangeStarted, self.__onVehicleChangeStarted),
         (self.__hangarSpace.onVehicleChanged, self.__onVehicleChanged),
         (self._nyController.onDataUpdated, self.__onNyDataUpdate),
         (self._nyController.currencies.onBalanceUpdated, self.__onBalanceUpdated))

    def _getCallbacks(self):
        return (('inventory', self.__onInventoryUpdate), ('cache', self.__onCacheUpdated))

    def _getListeners(self):
        listeners = super(NyMarketplaceView, self)._getListeners()
        return listeners + ((NyMarketPlaceRewardEvent.ON_VEHICLE_APPEARANCE_RESET, self.__onTryStyleOpen, EVENT_BUS_SCOPE.LOBBY),)

    def __onTryStyleOpen(self, event):
        self.__needToResetAppearance = False

    def __onPreSwitchViewEvent(self, ctx):
        if ctx.menuName != NyWidgetTopMenu.MARKETPLACE:
            self.__doClear()

    def __unsubscribeVehicleChange(self):
        entity = self.__hangarSpace.getVehicleEntity()
        if entity and entity.appearance:
            entity.appearance.loadState.unsubscribe(self.__onVehicleLoadFinished, self.__onVehicleLoadStarted)

    def __subscribeVehicleChange(self):
        entity = self.__hangarSpace.getVehicleEntity()
        if entity and entity.appearance:
            entity.appearance.loadState.subscribe(self.__onVehicleLoadFinished, self.__onVehicleLoadStarted)

    def __onVehicleLoadStarted(self):
        pass

    def __onVehicleLoadFinished(self):
        self.__resetBlur()

    def __onSideBarSelected(self, ctx):
        if ctx.menuName != NyWidgetTopMenu.MARKETPLACE:
            return
        self.__settings.setFindNotRecived(True)
        self.__onTabSelect(ctx.tabName, kitIdx=0)

    def __onTabSelect(self, tabName, kitIdx=0, forced=False):
        if not self._tabCache.setMarketplaceTab(tabName) and not forced:
            return
        self.__updateModel(tabName, kitIdx)

    def __updateModel(self, yearName, kitIdx=0):
        config = getNYMarketplaceConfig()
        items = config.getCategoryItems(yearName)
        with self.viewModel.transaction() as model:
            model.setCurrentTabName(yearName)
            cards = model.getCards()
            cards.clear()
            for index, item in enumerate(items):
                kitState = self.__getKitState(item)
                kitName = getSettingsName(item)
                collectionDistributions = self._itemsCache.items.festivity.getCollectionDistributions()
                discount = item.calculateDiscount(collectionDistributions, bonusChecker)
                card = CardModel()
                card.setKitIndex(index)
                card.setKitState(kitState.value)
                card.setKitName(kitName)
                card.setDiscount(discount)
                cards.addViewModel(card)

            cards.invalidate()
        self.__settings.setYearName(yearName)
        self.__selectCard(yearName, kitIdx)

    def __selectCard(self, yearName, kitIdx):
        isCamMoving = self.__cameraCallbackId is not None
        self.__clearCalbackId()
        kitIdx = self.__tryFindNotRecived(yearName, kitIdx)
        config = getNYMarketplaceConfig()
        item = config.getCategoryItem(yearName, kitIdx)
        if item is None:
            return
        else:
            self.__settings.setKitId(kitIdx)
            styleId = self.__getStyleFromRewards(item)
            prevStyle = self.__settings.styleID
            self.__settings.setStyleID(styleId)
            collectionName = getSettingsName(item)
            if styleId:
                self.__needResetBloor = prevStyle is None
                if isCamMoving:
                    self.__resetBlur()
                self.__showStyle(yearName, collectionName, styleId)
                self.__updateKitModel(collectionName, item, styleId, False)
            else:
                self.viewModel.setIsInteractive(False)
                self._resetCamera(duration=_EASING_TRANSITION_DURATION)
                self.__cameraCallbackId = BigWorld.callback(_EASING_TRANSITION_DURATION, partial(self.__updateKitModel, collectionName, item, None, True))
                self.__blur.enable()
            return

    def __updateKitModel(self, collectionName, item, styleId, removeVehicle):
        self.__cameraCallbackId = None
        if removeVehicle:
            self.__hangarSpace.removeVehicle()
            g_currentPreviewVehicle.destroy()
            g_currentPreviewVehicle.resetAppearance()
        kitState = self.__getKitState(item)
        kitRewards = getMarketRewards(item, isMerge=True)
        installedOn = ''
        if styleId:
            style = self.__service.getItemByID(GUI_ITEM_TYPE.STYLE, styleId)
            vehicleIntCDs = style.getInstalledVehicles()
            if vehicleIntCDs:
                vehNames = map(self.__getVehicleShortName, vehicleIntCDs)
                installedOn = ','.join(vehNames)
        with self.viewModel.transaction() as model:
            kit = model.kit
            kit.setStyleOnVehicle(installedOn)
            rewards = kit.getRewards()
            rewards.clear()
            for index, (bonus, tooltip) in enumerate(kitRewards):
                tooltipId = str(index)
                bonus.setTooltipId(tooltipId)
                bonus.setIndex(index)
                self._tooltips[tooltipId] = tooltip
                rewards.addViewModel(bonus)

            rewards.invalidate()
            resources = kit.getResources()
            resources.clear()
            for currency in NyCurrency.ALL:
                resources.addString(currency)

            resources.invalidate()
            model.setKitState(kitState)
            model.setCurrentKitName(collectionName)
            model.setIsInteractive(True)
        self.__updatePrice()
        return

    def __updatePrice(self):
        collectionDistributions = self._itemsCache.items.festivity.getCollectionDistributions()
        config = getNYMarketplaceConfig()
        item = config.getCategoryItem(self._tabCache.getMarketplaceTab(), self.__settings.kitId)
        if item is None:
            return
        else:
            with self.viewModel.transaction() as model:
                priceWithDiscount = item.getTotalPrice(collectionDistributions, bonusChecker)
                currency = self.__settings.resourceValue
                balance = self._nyController.currencies.getResouceBalance(currency)
                kit = model.kit
                kit.setCurrentResource(currency)
                kit.setPrice(item.getPrice())
                kit.setPriceWithDiscount(priceWithDiscount)
                kit.setDiscount(item.calculateDiscount(collectionDistributions, bonusChecker))
                kit.setNotEnoughResource(priceWithDiscount > balance)
            return

    def __getStyleFromRewards(self, item):
        rewards = []
        bonuses = [ bonus for bonus in getMarketItemBonusesFromItem(item) if isinstance(bonus, CustomizationsBonus) ]
        for bonus in bonuses:
            rewards.extend(bonus.getCustomizations())

        style = findFirst(lambda r: r.get('custType') == 'style', rewards)
        return style.get('id') if style else None

    def __showStyle(self, yearName, collectionName, styleId):
        style = self.__service.getItemByID(GUI_ITEM_TYPE.STYLE, styleId)
        if not style:
            return
        vehicleIntCDs = style.getInstalledVehicles()
        if vehicleIntCDs:
            vehicleIntCD = first(vehicleIntCDs)
        else:
            vehicleIntCD = getSuitableStyledVehicle(styleId, inInventory=True)
        if not vehicleIntCD:
            if yearName != Collections.NewYear18:
                vehTypeName = _DEFAULT_VEHICLE
            else:
                vehTypeName = _DEFAULT_VEHICLES_2018.get(collectionName)
            if vehTypeName:
                vehDescr = vehicles.VehicleDescr(typeName=vehTypeName)
                vehicleIntCD = vehDescr.type.compactDescr
        if not vehicleIntCD:
            return
        vehicleEntiry = self.__hangarSpace.getVehicleEntity()
        isVehicleLoaded = vehicleEntiry.isVehicleLoaded
        if g_currentPreviewVehicle.item and g_currentPreviewVehicle.item.intCD == vehicleIntCD and style.mayInstall(g_currentPreviewVehicle.item):
            if isVehicleLoaded:
                g_currentPreviewVehicle.previewStyle(style)
            else:
                self.__loadVehicle(g_currentPreviewVehicle.item, style)
        else:
            vehicle = self._itemsCache.items.getItemByCD(vehicleIntCD)
            if style.mayInstall(vehicle):
                self.__loadVehicle(vehicle, style)

    def __loadVehicle(self, vehicle, style=None):
        self.__hangarSpace.removeVehicle(waitingSoftStart=True, showWaitingBg=False)
        self.__needToResetAppearance = True
        g_currentPreviewVehicle.selectHeroTank(False)
        g_currentPreviewVehicle.selectVehicle(vehicle.intCD, None, style, waitingSoftStart=True, showWaitingBg=False)
        return

    def __onKitBuy(self):
        self.__buyCollectionKit(self.__settings)

    def __onKitSwitchResource(self, args):
        resourceValue = args.get('resource')
        resource = first([ item for item in Resource if item.value == resourceValue ], Resource.CRYSTAL)
        self.__settings.setResource(resource)
        self.__updatePrice()

    def __onKitOpenStyle(self):
        vehicle = g_currentPreviewVehicle.item
        actualVehicle = self._itemsCache.items.getItemByCD(vehicle.intCD) if vehicle else None
        if not actualVehicle or not actualVehicle.isCustomizationEnabled():
            return
        elif g_currentVehicle.isInBattle():
            g_currentVehicle.selectVehicle(actualVehicle.invID, callback=self.__onKitOpenStyle)
            return
        else:
            self.__settings.setOpenStyleOnVehicle(actualVehicle.invID)
            self.__hangarSpace.onVehicleChanged += self.__delayedShowCustomization
            self.__hangarSpace.onSpaceChanged += self.__delayedShowCustomization
            self.__resetAppearance()
            return

    def __delayedShowCustomization(self):
        self.__hangarSpace.onVehicleChanged -= self.__delayedShowCustomization
        self.__hangarSpace.onSpaceChanged -= self.__delayedShowCustomization
        showStyleFromMarketPlace(self.__settings.styleID, self.__settings.openStyleOnVehicle)

    def __onCardsSwitchKit(self, args):
        kitIdx = int(args.get('kitIndex'))
        if kitIdx >= 0:
            self.__selectCard(self._tabCache.getMarketplaceTab(), kitIdx)

    def __getKitState(self, item):
        if isCollectionItemReceived(item):
            return KitState.RECEIVED
        return KitState.AVAILABLE if self._nyController.isMaxAtmosphereLevel() else KitState.UNAVAILABLE

    def __tryFindNotRecived(self, yearName, kitIdx):
        if self.__settings.findNotRecived:
            config = getNYMarketplaceConfig()
            items = config.getCategoryItems(yearName)
            for index in chain(xrange(kitIdx, len(items)), xrange(0, kitIdx)):
                if self.__getKitState(items[index]) != KitState.RECEIVED:
                    kitIdx = index
                    break

            self.__settings.setFindNotRecived(False)
        return kitIdx

    @decorators.adisp_process('newYear/buyCollectionWaiting')
    def __buyCollectionKit(self, kitSettings):
        config = getNYMarketplaceConfig()
        item = config.getCategoryItem(kitSettings.yearName, kitSettings.kitId)
        dialog = MarketPurchaseDialogView(kitSettings.yearName, kitSettings.kitId, kitSettings.resource)
        result = yield BuyMarketplaceItemProcessor(item, kitSettings.getCategoryIndex(), kitSettings.kitId, kitSettings.resourceValue, dialog).request()
        if result.userMsg:
            SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType, priority=NotificationPriorityLevel.MEDIUM)
        if result.success:
            rewards = result.auxData
            kitName = getSettingsName(item)
            showNyMarketplaceRewardsWindow(kitSettings.yearName, kitName, rewards)
            kitSettings.setFindNotRecived(True)
            self.__selectCard(kitSettings.yearName, kitSettings.kitId)

    def __onNyDataUpdate(self, diff, _):
        if SyncDataKeys.POINTS in diff:
            self.__updateKitState()

    def __onInventoryUpdate(self, invDiff):
        if GUI_ITEM_TYPE.CUSTOMIZATION in invDiff:
            self.__updateModel(self.__settings.yearName, self.__settings.kitId)

    def __onCacheUpdated(self, diff):
        if 'vehsLock' in diff:
            self.__updateVehicleState()

    def __resetAppearance(self):
        if self.__needToResetAppearance:
            g_currentPreviewVehicle.selectNoVehicle()
            g_currentPreviewVehicle.resetAppearance()
            self.__needToResetAppearance = False

    def __updateKitState(self):
        config = getNYMarketplaceConfig()
        with self.viewModel.transaction() as model:
            items = config.getCategoryItems(self.__settings.yearName)
            kitState = self.__getKitState(items[self.__settings.kitId])
            model.setKitState(kitState)
            cards = model.getCards()
            for card in cards:
                index = card.getKitIndex()
                if 0 <= index < len(items):
                    item = items[index]
                    kitState = self.__getKitState(item)
                    card.setKitState(kitState.value)

            cards.invalidate()

    def __onVehicleChanged(self):
        self.__subscribeVehicleChange()

    def __onVehicleChangeStarted(self):
        self.__unsubscribeVehicleChange()
        self.__updateVehicleState()

    def __onBalanceUpdated(self):
        self.__updatePrice()
        self.__updateKitState()

    def __clearCalbackId(self):
        if self.__cameraCallbackId is not None:
            BigWorld.cancelCallback(self.__cameraCallbackId)
            self.__cameraCallbackId = None
        return

    def __resetBlur(self):
        if self.__needResetBloor:
            self.__needResetBloor = False
            self.__blur.disable()

    def __doClear(self):
        self.__heroTankController.setInteractive(True)
        self.__hangarSpace.setVehicleSelectable(True)
        self.__clearCalbackId()
        self.__unsubscribeVehicleChange()
        self.__resetAppearance()
        self._tooltips.clear()
        if self.__blur:
            self.__resetBlur()
            self.__blur.fini()
            self.__blur = None
        return

    def __getVehicleShortName(self, vehicleCD):
        return self._itemsCache.items.getItemByCD(vehicleCD).shortUserName

    def __updateVehicleState(self):
        vehicle = g_currentPreviewVehicle.item
        actualVehicle = self._itemsCache.items.getItemByCD(vehicle.intCD) if vehicle else None
        if actualVehicle:
            with self.viewModel.transaction() as model:
                model.setIsVehicleCustomizationEnabled(actualVehicle.isCustomizationEnabled())
                if actualVehicle.isCustomizationEnabled():
                    model.setVehicleState(VehicleState.DEFAULT)
                elif not actualVehicle.isInInventory:
                    model.setVehicleState(VehicleState.NOT_IN_INVENTORY)
                elif actualVehicle.isInUnit:
                    model.setVehicleState(VehicleState.IN_UNIT)
                elif actualVehicle.isBroken:
                    model.setVehicleState(VehicleState.BROKEN)
                elif actualVehicle.isInBattle:
                    model.setVehicleState(VehicleState.IN_BATTLE)
                else:
                    model.setVehicleState(VehicleState.CUSTOMIZATION_UNAVAILABLE)
        return
