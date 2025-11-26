# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/meta_view/pages/shop_page.py
import logging
from functools import partial
import typing
from gui.Scaleform.lobby_entry import getLobbyStateMachine
from shared_utils import first, findFirst
from CurrentVehicle import g_currentPreviewVehicle, g_currentVehicle
from comp7.gui.game_control.comp7_shop_controller import ShopControllerStatus
from comp7.gui.impl.gen.view_models.views.lobby.base_product_model import ProductTypes, ProductState
from comp7.gui.impl.gen.view_models.views.lobby.enums import MetaRootViews, Rank
from comp7.gui.impl.gen.view_models.views.lobby.meta_view.pages.rank_discount_model import RankDiscountModel
from comp7.gui.impl.gen.view_models.views.lobby.meta_view.pages.shop_model import ShopModel, ShopState
from comp7.gui.impl.lobby.comp7_helpers import comp7_model_helpers, comp7_shared
from comp7.gui.impl.lobby.meta_view.meta_view_helper import setDivisionData, setRankData, getRankDivisions
from comp7.gui.impl.lobby.meta_view.pages import PageSubModelPresenter
from comp7.gui.impl.lobby.meta_view.products_helper import packProduct, getItemType, getVehicleCDAndStyle, addSeenProduct
from comp7.gui.impl.lobby.meta_view.rotatable_view_helper import RotatableViewHelper, Comp7Cameras
from comp7.gui.impl.lobby.tooltips.fifth_rank_tooltip import FifthRankTooltip
from comp7.gui.impl.lobby.tooltips.general_rank_tooltip import GeneralRankTooltip
from comp7.gui.impl.lobby.tooltips.sixth_rank_tooltip import SixthRankTooltip
from comp7.gui.shared import event_dispatcher as comp7_events
from comp7.skeletons.gui.game_control import IComp7ShopController
from frameworks.wulf.view.array import fillViewModelsArray
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi.view.lobby.customization.shared import CustomizationTabs
from gui.Scaleform.daapi.view.lobby.vehicle_compare.formatters import resolveStateTooltip
from gui.Scaleform.daapi.view.lobby.vehicle_preview.configurable_vehicle_preview import OptionalBlocks
from gui.Scaleform.genConsts.STORAGE_CONSTANTS import STORAGE_CONSTANTS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.VEH_COMPARE import VEH_COMPARE
from gui.customization.constants import CustomizationModes
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from gui.impl.backport import BackportTooltipWindow
from gui.impl.backport.backport_tooltip import TooltipData
from gui.impl.gen import R
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.tooltips.vehicle_role_descr_view import VehicleRolesTooltipView
from gui.platform.products_fetcher.fetch_result import ResponseStatus
from gui.shared import g_eventBus
from gui.shared.event_dispatcher import showStorage
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.items_cache import CACHE_SYNC_REASON
from gui.shared.view_helpers.blur_manager import CachedBlur
from helpers import dependency
from items import customizations
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.game_control import IComp7Controller, IVehicleComparisonBasket
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.gui_items import IGuiItemsFactory
from skeletons.gui.shared.utils import IHangarSpace
_logger = logging.getLogger(__name__)
_PRODUCT_TYPE_ORDER = [ProductTypes.VEHICLE, ProductTypes.STYLE3D, ProductTypes.REWARD]
_SHOP_BACKGROUND_ALPHA = 0.0
if typing.TYPE_CHECKING:
    from typing import Dict
    from comp7.helpers.comp7_server_settings import Comp7RanksConfig
    from comp7.gui.game_control.comp7_shop_controller import ShopPageProductInfo
    from gui.Scaleform.framework.application import AppEntry

@dependency.replace_none_kwargs(service=ICustomizationService, hangarSpace=IHangarSpace)
def _onCustomizationLoadedCallback(styleCD, service=None, hangarSpace=None):
    if not styleCD:
        return
    style = service.getItemByCD(styleCD)
    ctx = service.getCtx()
    ctx.changeMode(CustomizationModes.STYLE_3D if style.is3D else CustomizationModes.STYLE_2D)
    ctx.mode.changeTab(tabId=CustomizationTabs.STYLES_3D if style.is3D else CustomizationTabs.STYLES_2D)
    entity = hangarSpace.getVehicleEntity()
    isVehicleLoaded = entity and entity.appearance and entity.appearance.isLoaded()
    if isVehicleLoaded:
        ctx.selectItem(styleCD)
    else:
        styleSlotItem = ctx.mode.getItemFromSlot(ctx.mode.STYLE_SLOT)
        if not styleSlotItem or styleSlotItem.intCD != styleCD:
            ctx.mode.installItem(styleCD, ctx.mode.STYLE_SLOT)
        g_eventBus.addListener(CameraRelatedEvents.VEHICLE_LOADING, __onVehicleLoadFinished)


@dependency.replace_none_kwargs(service=ICustomizationService, hangarSpace=IHangarSpace)
def __onVehicleLoadFinished(ctxEvent, service=None, hangarSpace=None):
    if ctxEvent.ctx.get('started'):
        return
    g_eventBus.removeListener(CameraRelatedEvents.VEHICLE_LOADING, __onVehicleLoadFinished)
    entity = hangarSpace.getVehicleEntity()
    isVehicleLoaded = entity and entity.appearance and entity.appearance.isLoaded()
    if not isVehicleLoaded:
        return
    ctx = service.getCtx()
    ctx.refreshOutfit()


class ShopPage(PageSubModelPresenter):
    __slots__ = ('__currentPreviewVehicle', '__currentPreviewStyle', '__currentItemCD', '__productSelectorMethods', '__productSetterMethods', '__blur', '__rotationHelper', '__requestStatus', '__products', '__productItems', '__productCdToCode', '__switchCameraToDefault', '__switchVehicleToDefault', '__hangarVehId')
    __appLoader = dependency.descriptor(IAppLoader)
    __comp7Controller = dependency.descriptor(IComp7Controller)
    __comp7ShopController = dependency.descriptor(IComp7ShopController)
    __hangarSpace = dependency.descriptor(IHangarSpace)
    __c11nService = dependency.descriptor(ICustomizationService)
    __itemsCache = dependency.descriptor(IItemsCache)
    __comparisonBasket = dependency.descriptor(IVehicleComparisonBasket)
    __guiItemsFactory = dependency.descriptor(IGuiItemsFactory)
    __DEFAULT_PRODUCT_SELECTOR_NAME = 'default'
    __BLUR_INTENSITY = 0.5

    def __init__(self, viewModel, parentView):
        super(ShopPage, self).__init__(viewModel, parentView)
        self.__currentItemCD = None
        self.__blur = None
        self.__rotationHelper = None
        self.__switchCameraToDefault = None
        self.__switchVehicleToDefault = None
        self.__productSelectorMethods = {}
        self.__productSetterMethods = {}
        self.__productCdToCode = {}
        self.__requestStatus = None
        self.__products = {}
        self.__hangarVehId = None
        return

    @property
    def pageId(self):
        return MetaRootViews.SHOP

    @property
    def viewModel(self):
        return super(ShopPage, self).getViewModel()

    @property
    def ranksConfig(self):
        return self.__comp7Controller.getRanksConfig()

    @property
    def currentItemCD(self):
        return self.__currentItemCD

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId', None)
            itemCD = int(event.getArgument('id'))
            tooltipData = None
            if tooltipId in (TOOLTIPS_CONSTANTS.SHOP_VEHICLE, TOOLTIPS_CONSTANTS.SHOP_MODULE, TOOLTIPS_CONSTANTS.SHOP_CUSTOMIZATION_ITEM):
                tooltipData = TooltipData(tooltip=tooltipId, isSpecial=True, specialAlias=tooltipId, specialArgs=[itemCD])
            if tooltipData:
                window = BackportTooltipWindow(tooltipData, self.getParentWindow())
                window.load()
                return window
        return

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.comp7.mono.lobby.tooltips.general_rank_tooltip():
            params = {'rank': Rank(event.getArgument('rank')),
             'divisions': event.getArgument('divisions'),
             'from': event.getArgument('from'),
             'to': event.getArgument('to')}
            return GeneralRankTooltip(params=params)
        elif contentID == R.views.comp7.mono.lobby.tooltips.fifth_rank_tooltip():
            return FifthRankTooltip()
        elif contentID == R.views.comp7.mono.lobby.tooltips.sixth_rank_tooltip():
            return SixthRankTooltip()
        elif contentID == R.views.lobby.ranked.tooltips.RankedBattlesRolesTooltipView():
            vehicleCD = int(event.getArgument('vehicleCD'))
            return VehicleRolesTooltipView(vehicleCD)
        else:
            return None

    def initialize(self, **params):
        self.__rotationHelper = RotatableViewHelper()
        self.__switchCameraToDefault = True
        self.__switchVehicleToDefault = True
        self.__rotationHelper.switchCamera(Comp7Cameras.SHOP.value, False)
        self.__disableBackgroundAlpha()
        super(ShopPage, self).initialize(**params)
        self.__productSelectorMethods = {GUI_ITEM_TYPE.VEHICLE: self.__selectVehicle,
         GUI_ITEM_TYPE.STYLE: self.__selectStyle,
         GUI_ITEM_TYPE.OPTIONALDEVICE: self.__selectEquipment}
        if 'productCD' in params:
            self.__currentItemCD = params['productCD']
        self.__blur = CachedBlur(blurRadius=self.__BLUR_INTENSITY)
        if self.__hangarVehId is None:
            self.__hangarVehId = g_currentVehicle.invID
        g_currentVehicle.selectNoVehicle()
        self.__updateData()
        return

    def finalize(self):
        super(ShopPage, self).finalize()
        g_currentPreviewVehicle.onHeroStateUpdated -= self.__onHeroStateChanged
        if self.__switchVehicleToDefault:
            g_currentPreviewVehicle.selectNoVehicle()
            g_currentVehicle.selectVehicle(self.__hangarVehId)
        self.__productSelectorMethods = {}
        self.__productCdToCode = {}
        from comp7.gui.impl.lobby.hangar.states import Comp7ModeState
        lsm = getLobbyStateMachine()
        isComp7State = lsm.getStateByCls(Comp7ModeState).isEntered()
        if self.__switchCameraToDefault and isComp7State:
            self.__rotationHelper.switchCamera(Comp7Cameras.DEFAULT.value, False)
        self.__rotationHelper = None
        if self.__blur is not None:
            self.__blur.fini()
        self.__hideWaiting()
        return

    def _getEvents(self):
        events = self.__rotationHelper.getCameraEvents(self.viewModel)
        events.extend([(self.viewModel.onAddToVehicleCompare, self.__onAddToVehicleCompare),
         (self.viewModel.onGoToPreview, self.__goToPreview),
         (self.viewModel.onGoToHangar, self.__goToVehicle),
         (self.viewModel.onGoToCustomization, self.__goToStyle),
         (self.viewModel.onProductPurchase, self.__openPurchaseView),
         (self.viewModel.onProductRestore, self.__openRestoreView),
         (self.viewModel.onProductSelect, self.__onProductSelect),
         (self.viewModel.onProductSeen, self.__onProductSeen),
         (self.__itemsCache.onSyncCompleted, self.__onSyncCompleted),
         (self.__comp7ShopController.onShopStateChanged, self.__onShopStateChanged),
         (self.__comp7ShopController.onDataUpdated, self.__onDataUpdated),
         (self.__comparisonBasket.onChange, self.__switchComparisonBasketState)])
        return events

    def __disableBackgroundAlpha(self):
        app = self.__appLoader.getApp()
        app.setBackgroundAlpha(_SHOP_BACKGROUND_ALPHA)

    def __updateData(self, *_, **__):
        self.viewModel.setShopState(ShopState.INITIAL)
        if not self.__comp7ShopController.isShopEnabled:
            _logger.warning('comp7 shop disabled')
            self.__switchToErrorState()
            return
        self.__products = self.__comp7ShopController.getProducts()
        if self.__products:
            self.__processData()
        else:
            self.__showWaiting()

    def __processData(self):
        with self.viewModel.transaction() as tx:
            self.__products = self.__products or self.__comp7ShopController.getProducts()
            hasDataError = len(self.__products) == 0
            if hasDataError:
                _logger.warning('no products were found for comp7 shop')
                self.__switchToErrorState()
                return
            self.__switchToSuccessState()
            if not self.__comp7Controller.isQualificationActive():
                comp7_model_helpers.setRankInfo(tx)
                comp7_model_helpers.setMaxRankInfo(tx)
            self.__updateProductsData(tx)
            self.__selectInitialItem()

    def __onSyncCompleted(self, reason, *_):
        if reason == CACHE_SYNC_REASON.CLIENT_UPDATE:
            self.__updateData()

    def __onShopStateChanged(self):
        self.__updateData()

    def __switchToErrorState(self):
        g_currentPreviewVehicle.selectNoVehicle()
        g_currentVehicle.selectNoVehicle()
        self.viewModel.setShopState(ShopState.ERROR)
        self.__currentItemCD = None
        self.__blur.enable()
        self.__hideWaiting()
        return

    def __switchToSuccessState(self):
        self.viewModel.setShopState(ShopState.SUCCESS)
        self.__hideWaiting()

    def __showWaiting(self):
        if self.viewModel.getShopState() == ShopState.ERROR:
            return
        Waiting.show('loadingData', overlapsUI=False, isSingle=True)

    def __hideWaiting(self):
        Waiting.hide('loadingData')

    def __onDataUpdated(self, status):
        if status == ShopControllerStatus.DATA_READY:
            self.__processData()
        elif status == ShopControllerStatus.ERROR:
            self.__switchToErrorState()

    def __updateProductsData(self, shopModel):
        productItems = []
        for productCode, productData in self.__products.iteritems():
            productModel = packProduct(productData)
            if productModel is not None:
                self.__productCdToCode[productModel.getId()] = productCode
                productItems.append(productModel)

        productItems.sort(key=self.__sortingKey)
        self.__productItems = productItems
        fillViewModelsArray(productItems, shopModel.getProducts())
        return

    def __selectInitialItem(self):
        if self.__currentItemCD is None:
            self.__currentItemCD = int(self.__getStartProductCD(self.__productItems))
        self.__selectProduct()
        return

    def __updateProductDiscounts(self):
        with self.viewModel.transaction() as tx:
            discountItems = []
            productCode = self.__productCdToCode[self.__currentItemCD]
            product = self.__products[productCode]
            for rankName, discount in product.discounts.iteritems():
                discountModel = RankDiscountModel()
                rank = comp7_shared.getRankByName(rankName)
                setRankData(discountModel, rank.value, self.ranksConfig)
                setDivisionData(discountModel, getRankDivisions(rank.value, self.ranksConfig))
                discountModel.setValue(discount)
                maxRankNumber = self.__comp7Controller.getMaxRankNumberForSeason()
                productRankNumber = comp7_shared.getRankOrder(rank)
                discountModel.setWasUnlocked(productRankNumber <= maxRankNumber)
                discountItems.append(discountModel)

            sortedDiscounts = sorted(discountItems, key=lambda d: comp7_shared.getRankOrder(d.getRank()))
            fillViewModelsArray(sortedDiscounts, tx.getRankDiscounts())

    def __sortingKey(self, product):
        if product.getType() == ProductTypes.VEHICLE:
            return (-product.getRank(),
             _PRODUCT_TYPE_ORDER.index(product.getType()),
             product.vehicleInfo.getTier(),
             product.vehicleInfo.getNation(),
             product.vehicleInfo.getName())
        productName = product.getName() if product.getType() == ProductTypes.STYLE3D else product.reward.getLabel()
        return (-product.getRank(),
         _PRODUCT_TYPE_ORDER.index(product.getType()),
         0,
         '',
         productName)

    def __goToPreview(self):
        itemType = getItemType(self.__currentItemCD)
        if itemType == GUI_ITEM_TYPE.VEHICLE:
            params = {'resetAppearance': False,
             'heroInteractive': False,
             'hiddenBlocks': (OptionalBlocks.BUYING_PANEL,)}
            comp7_events.showComp7VehiclePreview(self.__currentItemCD, **params)
        elif itemType == GUI_ITEM_TYPE.STYLE:
            vehCD, style = getVehicleCDAndStyle(self.__currentItemCD)
            params = {'resetAppearance': False}
            comp7_events.showComp7StylePreview(vehCD, style, **params)

    def __goToVehicle(self):
        self.__hangarVehId = self.__itemsCache.items.getItemByCD(self.__currentItemCD).invID
        self.parentView.getViewModel().onClose()

    def __goToStyle(self):
        self.__switchCameraToDefault = False
        self.__switchVehicleToDefault = False
        customizationCallback = partial(_onCustomizationLoadedCallback, styleCD=self.__currentItemCD)
        if self.__c11nService.getCtx() is None:
            self.__c11nService.showCustomization(g_currentPreviewVehicle.invID, callback=customizationCallback)
        else:
            customizationCallback()
        return

    def __openPurchaseView(self):
        self.__switchVehicleToDefault = False
        productCode = self.__productCdToCode[self.__currentItemCD]
        comp7_events.showComp7PurchaseDialog(productCode, self.getParentWindow())

    def __openRestoreView(self):
        showStorage(STORAGE_CONSTANTS.IN_HANGAR, STORAGE_CONSTANTS.VEHICLES_TAB_RESTORE)

    @args2params(int)
    def __onProductSelect(self, cd):
        if self.__currentItemCD == cd:
            return
        self.__currentItemCD = cd
        self.__selectProduct()

    @args2params(int)
    def __onProductSeen(self, cd):
        productModel = findFirst(lambda model: model.getId() == cd, self.viewModel.getProducts())
        if productModel.getIsNew():
            addSeenProduct(cd)
            productModel.setIsNew(False)
            self.parentView.updateTabNotifications()

    def __onAddToVehicleCompare(self):
        self.__comparisonBasket.addVehicle(self.__currentItemCD)

    def __switchComparisonBasketState(self, _):
        with self.viewModel.transaction() as tx:
            self.__checkComparisonBasketState(tx)

    def __getStartProductCD(self, products):
        if self.__currentItemCD:
            return self.__currentItemCD
        notPurchasedProduct = self.__getFirstNotPurchasedProduct(products)
        return notPurchasedProduct.getId() if notPurchasedProduct else products[0].getId()

    def __getFirstNotPurchasedProduct(self, products):
        return findFirst(lambda product: product.getState() != ProductState.PURCHASED, products)

    def __selectProduct(self):
        itemType = getItemType(self.__currentItemCD)
        if itemType in self.__productSelectorMethods:
            selectorMethod = self.__productSelectorMethods[itemType]
        else:
            selectorMethod = self.__productSelectorMethods[self.__DEFAULT_PRODUCT_SELECTOR_NAME]
        with self.viewModel.transaction() as tx:
            tx.setSelectedProductId(self.__currentItemCD)
        selectorMethod()
        self.__updateProductDiscounts()
        self.__rotationHelper.resetCamera()

    def __selectVehicle(self):
        if self.__currentItemCD and g_currentPreviewVehicle.intCD == self.__currentItemCD:
            vehDescr = g_currentPreviewVehicle.item.descriptor
            customizationOutfit = customizations.getNationalEmblemsOutfit(vehDescr)
            outfit = self.__guiItemsFactory.createOutfit(component=customizationOutfit, vehicleCD=vehDescr.makeCompactDescr())
            self.__hangarSpace.updateVehicleOutfit(outfit)
        elif not g_currentPreviewVehicle.isHeroTank:
            g_currentPreviewVehicle.selectVehicle(self.__currentItemCD)
        else:
            g_currentPreviewVehicle.onHeroStateUpdated += self.__onHeroStateChanged
        with self.viewModel.transaction() as tx:
            self.__checkComparisonBasketState(tx)
        self.__blur.disable()

    def __onHeroStateChanged(self):
        itemType = getItemType(self.__currentItemCD)
        if itemType == GUI_ITEM_TYPE.VEHICLE:
            self.__selectVehicle()
        elif itemType == GUI_ITEM_TYPE.STYLE:
            self.__selectStyle()
        g_currentPreviewVehicle.onHeroStateUpdated -= self.__onHeroStateChanged

    def __checkComparisonBasketState(self, model):
        state, tooltip = resolveStateTooltip(self.__comparisonBasket, g_currentPreviewVehicle.item, enabledTooltip=VEH_COMPARE.VEHPREVIEW_COMPAREVEHICLEBTN_TOOLTIPS_ADDTOCOMPARE, fullTooltip=VEH_COMPARE.VEHPREVIEW_COMPAREVEHICLEBTN_TOOLTIPS_DISABLED)
        model.setIsVehiclesCompareEnabled(state)
        model.setVehicleCompareTooltipId(tooltip)

    def __selectStyle(self):
        if g_currentPreviewVehicle.isHeroTank:
            g_currentPreviewVehicle.onHeroStateUpdated += self.__onHeroStateChanged
            return
        vCompDescr, style = getVehicleCDAndStyle(self.__currentItemCD)
        if g_currentPreviewVehicle.intCD != vCompDescr:
            g_currentPreviewVehicle.selectVehicle(vCompDescr, style=style)
        else:
            outfit = style.getOutfit(season=first(style.seasons), vehicleCD=g_currentPreviewVehicle.item.descriptor.makeCompactDescr())
            if not outfit:
                return
            self.__hangarSpace.updateVehicleOutfit(outfit)
        self.__blur.disable()

    def __selectEquipment(self):
        self.__blur.enable()
        if g_currentPreviewVehicle.item:
            g_currentPreviewVehicle.selectNoVehicle()
        if g_currentVehicle.item:
            g_currentVehicle.selectNoVehicle()
