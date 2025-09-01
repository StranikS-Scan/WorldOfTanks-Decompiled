# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/dialogs/purchase_dialog.py
import logging
import BigWorld
from gui.Scaleform.lobby_entry import getLobbyStateMachine
from shared_utils import findFirst
from shared_utils import first
from Comp7Lighting import Comp7Lighting, Comp7LightingTriggers
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.backport import BackportTooltipWindow
from gui.impl.backport.backport_tooltip import createTooltipData
from gui.impl.lobby.tooltips.vehicle_role_descr_view import VehicleRolesTooltipView
from comp7.gui.impl.gen.view_models.views.lobby.base_product_model import ProductTypes
from comp7.gui.impl.gen.view_models.views.lobby.dialogs.purchase_dialog_model import PurchaseDialogModel, PageState
from comp7.gui.impl.gen.view_models.views.lobby.style3d_product_model import Style3dProductModel
from comp7.gui.impl.lobby.comp7_helpers.comp7_lobby_sounds import FlybySounds, playSound
from comp7.gui.impl.lobby.meta_view.products_helper import packProduct, setProductModelData
from comp7.gui.impl.lobby.meta_view.rotatable_view_helper import RotatableViewHelper, Comp7Cameras
from comp7.skeletons.gui.game_control import IComp7ShopController
from frameworks.wulf import WindowFlags, WindowLayer
from frameworks.wulf.view.array import fillViewModelsArray
from gui.impl.gen import R
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.shared.items_cache import CACHE_SYNC_REASON
from gui.shared.view_helpers.blur_manager import CachedBlur
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.game_control import IOverlayController
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
from wg_async import wg_async
from gui.impl.lobby.page.wallet_presenter import WalletPresenter, CrystalProvider, GoldProvider, CreditsProvider, FreeXpProvider
from gui.impl.pub.view_component import ViewComponent
_logger = logging.getLogger(__name__)

class PurchaseDialog(ViewComponent):
    __overlayCtrl = dependency.instance(IOverlayController)
    __itemsCache = dependency.instance(IItemsCache)
    __comp7ShopController = dependency.instance(IComp7ShopController)
    __hangarSpace = dependency.descriptor(IHangarSpace)
    __appLoader = dependency.descriptor(IAppLoader)
    __BLUR_INTENSITY = 0.5

    def __init__(self, productCode):
        super(PurchaseDialog, self).__init__(R.views.comp7.mono.lobby.dialogs.purchase_dialog(), PurchaseDialogModel)
        self.__productCode = productCode
        self.__rotationHelper = RotatableViewHelper()
        self.__prevCameraName = None
        self.__blur = None
        return

    @property
    def viewModel(self):
        return super(PurchaseDialog, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            tooltipData = None
            if tooltipId == TOOLTIPS_CONSTANTS.SHOP_VEHICLE:
                vehicleCD = int(event.getArgument('vehicleCD'))
                tooltipData = createTooltipData(isSpecial=True, specialAlias=tooltipId, specialArgs=(vehicleCD,))
            if tooltipData:
                window = BackportTooltipWindow(tooltipData, self.getParentWindow())
                window.load()
                return window
        return super(PurchaseDialog, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.ranked.tooltips.RankedBattlesRolesTooltipView():
            vehicleCD = int(event.getArgument('vehicleCD'))
            return VehicleRolesTooltipView(vehicleCD)
        else:
            return None

    def _getChildComponents(self):
        header = R.aliases.lobby_header.default
        return {header.Wallet(): lambda : WalletPresenter((CrystalProvider(),
                           GoldProvider(),
                           CreditsProvider(),
                           FreeXpProvider()))}

    def _onLoading(self, *args, **kwargs):
        super(PurchaseDialog, self)._onLoading()
        with self.viewModel.transaction() as tx:
            tx.setPageState(PageState.CONFIRMATION)
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
        from comp7.gui.impl.lobby.hangar.states import Comp7ModeState
        lsm = getLobbyStateMachine()
        isComp7State = lsm.getStateByCls(Comp7ModeState).isEntered()
        if isComp7State:
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
