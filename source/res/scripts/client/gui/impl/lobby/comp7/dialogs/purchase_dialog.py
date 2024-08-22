# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/comp7/dialogs/purchase_dialog.py
import logging
import BigWorld
import typing
from shared_utils import findFirst
from shared_utils import first
from Comp7Lighting import Comp7Lighting, Comp7LightingTriggers
from frameworks.wulf import ViewSettings, WindowFlags, WindowLayer
from frameworks.wulf.view.array import fillViewModelsArray
from gui.impl import backport
from gui.impl.auxiliary.tooltips.simple_tooltip import createSimpleTooltip
from gui.impl.backport import BackportTooltipWindow, createTooltipData
from gui.impl.dialogs.dialog_template_utils import getCurrencyTooltipAlias
from gui.impl.dialogs.sub_views.top_right.money_balance import NO_WGM_TOOLTIP_DATA
from gui.impl.gen import R
from gui.impl.gen.view_models.views.dialogs.sub_views.currency_view_model import CurrencyType
from gui.impl.gen.view_models.views.lobby.comp7.base_product_model import ProductTypes
from gui.impl.gen.view_models.views.lobby.comp7.dialogs.purchase_dialog_model import PurchaseDialogModel, PageState
from gui.impl.gen.view_models.views.lobby.comp7.style3d_product_model import Style3dProductModel
from gui.impl.lobby.comp7.comp7_lobby_sounds import FlybySounds, playSound
from gui.impl.lobby.comp7.comp7_purchase_helpers import getComp7BalanceModel, updateComp7BalanceModel
from gui.impl.lobby.comp7.meta_view.products_helper import packProduct, setProductModelData
from gui.impl.lobby.comp7.meta_view.rotatable_view_helper import RotatableViewHelper, Comp7Cameras
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.shared.items_cache import CACHE_SYNC_REASON
from gui.shared.view_helpers.blur_manager import CachedBlur
from helpers import dependency
from skeletons.gui.game_control import IOverlayController, IComp7ShopController
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
from wg_async import wg_async
from skeletons.gui.app_loader import IAppLoader
if typing.TYPE_CHECKING:
    from typing import Optional
    from frameworks.wulf import ViewEvent, Window
_logger = logging.getLogger(__name__)

class PurchaseDialog(ViewImpl):
    __slots__ = ('__productCode', '__rotationHelper', '__prevCameraName', '__blur')
    __overlayCtrl = dependency.instance(IOverlayController)
    __itemsCache = dependency.instance(IItemsCache)
    __comp7ShopController = dependency.instance(IComp7ShopController)
    __hangarSpace = dependency.descriptor(IHangarSpace)
    __appLoader = dependency.descriptor(IAppLoader)
    __BLUR_INTENSITY = 0.5

    def __init__(self, productCode):
        settings = ViewSettings(R.views.lobby.comp7.dialogs.PurchaseDialog())
        settings.model = PurchaseDialogModel()
        super(PurchaseDialog, self).__init__(settings)
        self.__productCode = productCode
        self.__rotationHelper = RotatableViewHelper()
        self.__prevCameraName = None
        self.__blur = None
        return

    @property
    def viewModel(self):
        return super(PurchaseDialog, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.dialogs.common.DialogTemplateGenericTooltip():
            currency = event.getArgument('currency')
            if currency is not None:
                return self.createCurrencyTooltip(event, currency)
        return super(PurchaseDialog, self).createToolTip(event)

    def createCurrencyTooltip(self, event, currency):
        if self.__itemsCache.items.stats.mayConsumeWalletResources:
            window = BackportTooltipWindow(createTooltipData(isSpecial=True, specialAlias=getCurrencyTooltipAlias(currency), specialArgs=[]), self.getParentWindow())
            window.load()
            return window
        else:
            params = NO_WGM_TOOLTIP_DATA.get(CurrencyType(currency))
            return createSimpleTooltip(self.getParentWindow(), event, backport.text(params['header']), backport.text(params['body'])) if params is not None else None

    def _onLoading(self, *args, **kwargs):
        super(PurchaseDialog, self)._onLoading()
        with self.viewModel.transaction() as tx:
            tx.setPageState(PageState.CONFIRMATION)
            self.__setBalance(tx)
            self.__setProducts(tx)
        self.__prevCameraName = self.__rotationHelper.getCameraManager().getCurrentCameraName()
        self.__rotationHelper.switchCamera(Comp7Cameras.PURCHASE.value, False)
        self.__overlayCtrl.setOverlayState(True)
        lobby = self.__appLoader.getDefLobbyApp()
        lobby.containerManager.showContainers((WindowLayer.TOP_WINDOW,), 300)
        self.__blur = CachedBlur(enabled=not self.__isCameraFlybyNeeded(), blurRadius=self.__BLUR_INTENSITY)

    def _finalize(self):
        super(PurchaseDialog, self)._finalize()
        if self.__isCameraFlybyNeeded():
            self.__setLightingTrigger(Comp7LightingTriggers.DEFAULT.value)
        self.__rotationHelper.switchCamera(self.__prevCameraName, False)
        self.__overlayCtrl.setOverlayState(False)
        if self.__blur is not None:
            self.__blur.fini()
            self.__blur = None
        self.__rotationHelper = None
        return

    def _getEvents(self):
        events = self.__rotationHelper.getCameraEvents(self.viewModel)
        cameraManager = self.__rotationHelper.getCameraManager()
        if cameraManager is not None:
            events.append((cameraManager.onCameraSwitched, self.__onCameraSwitched))
        events.extend([(self.viewModel.onClose, self.__onClose),
         (self.viewModel.onConfirm, self.__onConfirm),
         (self.__itemsCache.onSyncCompleted, self.__onItemsCacheSync),
         (self.__comp7ShopController.onDataUpdated, self.__updateData),
         (self.__comp7ShopController.onShopStateChanged, self.__onShopStateChanged)])
        return events

    def __onClose(self):
        self.destroyWindow()

    @wg_async
    def __onConfirm(self):
        self.viewModel.setIsPurchaseProcessing(True)
        result = yield self.__comp7ShopController.buyProduct(self.__productCode)
        if result:
            self.__setSuccessPurchaseState()
        else:
            self.viewModel.setPageState(PageState.ERROR)
            self.__blur.enable()
        self.viewModel.setIsPurchaseProcessing(False)

    def __onItemsCacheSync(self, reason, *_):
        if reason == CACHE_SYNC_REASON.CLIENT_UPDATE:
            self.__updateData()

    def __setBalance(self, viewModel):
        balance = getComp7BalanceModel()
        fillViewModelsArray(balance, viewModel.getBalance())
        viewModel.setIsWGMAvailable(self.__itemsCache.items.stats.mayConsumeWalletResources)

    def __setProducts(self, viewModel):
        products = self.__comp7ShopController.getProducts()
        if not products:
            _logger.warning('Failed to set product info, no products')
        productModel = packProduct(products[self.__productCode])
        fillViewModelsArray([productModel], viewModel.getProduct())
        if isinstance(productModel, Style3dProductModel):
            viewModel.setHasSuitableVehicle(productModel.getCanGoToCustomization())

    def __updateData(self, *_):
        if self.viewModel.getPageState() == PageState.CONFIRMATION:
            products = self.__comp7ShopController.getProducts()
            if not products:
                _logger.warning('Failed to update product info, no products')
            productData = products[self.__productCode]
            productModel = first(self.viewModel.getProduct())
            setProductModelData(productData, productModel)
            updateComp7BalanceModel(self.viewModel.getBalance())

    def __onCameraSwitched(self, cameraName):
        if cameraName == Comp7Cameras.PRE_FLYBY.value:
            self.__startCameraFlyby()

    def __isCameraFlybyNeeded(self):
        productModel = first(self.viewModel.getProduct())
        return productModel.getType() in (ProductTypes.VEHICLE, ProductTypes.STYLE3D)

    def __setSuccessPurchaseState(self):
        if self.__isCameraFlybyNeeded():
            self.__rotationHelper.switchCamera(Comp7Cameras.PRE_FLYBY.value, False)
            self.viewModel.setPageState(PageState.FLYBY)
        else:
            self.viewModel.setPageState(PageState.CONGRATULATION)

    def __startCameraFlyby(self):
        self.__setLightingTrigger(Comp7LightingTriggers.FLYBY.value)
        cameraManager = self.__rotationHelper.getCameraManager()
        if cameraManager is not None:
            playSound(FlybySounds.START.value)
            cameraManager.activateCameraFlyby(self.__onFlybyFinished)
        else:
            _logger.warning('Could not start comp7 fly-by, camera manager is None')
        return

    def __onFlybyFinished(self):
        playSound(FlybySounds.STOP.value)
        self.viewModel.setPageState(PageState.CONGRATULATION)

    def __setLightingTrigger(self, trigger):
        entity = findFirst(lambda entity: isinstance(entity, Comp7Lighting), BigWorld.entities.values())
        if entity is not None:
            entity.setTrigger(trigger)
        else:
            _logger.warning('Comp7Lighting entity must be placed in comp7 hangar space!')
        return

    def __onShopStateChanged(self):
        if not self.__comp7ShopController.isShopEnabled:
            self.__onClose()


class PurchaseDialogWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, productCode, parent=None):
        super(PurchaseDialogWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=PurchaseDialog(productCode), layer=WindowLayer.TOP_WINDOW, parent=parent)
