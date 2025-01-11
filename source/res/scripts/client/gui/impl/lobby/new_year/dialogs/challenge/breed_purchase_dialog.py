# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/dialogs/challenge/breed_purchase_dialog.py
import typing
from frameworks.wulf import WindowLayer, ViewSettings
from gui import SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.pub.dialog_window import DialogFlags
from gui.shared.view_helpers.blur_manager import CachedBlur
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_purchase_model import PurchaseState, NyPurchaseModel
from gui.impl.lobby.new_year.dialogs.dialog_helper import initBalance
from gui.impl.new_year.new_year_helper import backportTooltipDecorator
from gui.shared.money import Currency
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.shared.notifications import NotificationPriorityLevel
from gui.shared.utils import decorators
from gui.shop import showBuyGoldForBreed
from helpers import dependency
from items.components.ny_constants import NY_DOG_BREED_ID_TO_INDEX
from messenger.m_constants import SCH_CLIENT_MSG_TYPE
from new_year.celebrity.celebrity_quests_helpers import getBreedPrice, getNextBreedIDToBuy
from new_year.ny_processor import BuyDogBreedProcessor
from skeletons.gui.game_control import IWalletController
from skeletons.gui.shared import IItemsCache
from skeletons.gui.system_messages import ISystemMessages
from skeletons.new_year import INewYearController
BALANCE_ORDER = (Currency.CREDITS, Currency.GOLD)

class BreedPurchaseDialog(ViewImpl):
    __slots__ = ('__currentBreedIdx', '__isRequestToBuyProcessing')
    __wallet = dependency.descriptor(IWalletController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __nyController = dependency.descriptor(INewYearController)
    __systemMessages = dependency.descriptor(ISystemMessages)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.new_year.dialogs.challenge.BreedPurchaseDialog())
        settings.args = args
        settings.kwargs = kwargs
        settings.model = NyPurchaseModel()
        self.__isRequestToBuyProcessing = False
        self.__currentBreedIdx = NY_DOG_BREED_ID_TO_INDEX.get(getNextBreedIDToBuy(), 1)
        super(BreedPurchaseDialog, self).__init__(settings)

    @property
    def viewModel(self):
        return super(BreedPurchaseDialog, self).getViewModel()

    @backportTooltipDecorator()
    def createToolTip(self, event):
        return super(BreedPurchaseDialog, self).createToolTip(event)

    def canBeClosed(self):
        return not self.__isRequestToBuyProcessing

    def _onLoading(self, *args, **kwargs):
        super(BreedPurchaseDialog, self)._onLoading(*args, **kwargs)
        g_clientUpdateManager.addMoneyCallback(self.__onMoneyChangeHandler)
        self.__update()

    def _finalize(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(BreedPurchaseDialog, self)._finalize()

    def _getEvents(self):
        return ((self.__wallet.onWalletStatusChanged, self.__onWalletStatusChanged), (self.viewModel.onBuy, self.__onBuy), (self.viewModel.onBuyGold, self.__onBuyGold))

    def __updateBalance(self, model):
        initBalance(model, BALANCE_ORDER)

    def __updatePrice(self):
        status = PurchaseState.UNAVAILABLE if self.__wallet.isNotAvailable else PurchaseState.AVAILABLE
        price = getBreedPrice(self.__currentBreedIdx)
        currency = price.getCurrency()
        priceValue = price.get(currency, 0)
        money = self.__itemsCache.items.stats.money
        isEnough = money.get(currency, 0) >= priceValue
        with self.viewModel.transaction() as model:
            model.setCurrency(currency)
            model.setPrice(priceValue)
            model.setPurchaseState(status)
            model.setIsEnough(isEnough)

    def __update(self):
        with self.viewModel.transaction() as model:
            self.__updateBalance(model.getBalance())
            self.__updatePrice()

    def __onMoneyChangeHandler(self, *_):
        self.__update()

    def __onWalletStatusChanged(self, _):
        self.__update()

    @decorators.adisp_process('newYear/buyBreed')
    def __onBuy(self):
        self.__isRequestToBuyProcessing = True
        result = yield BuyDogBreedProcessor(self.__currentBreedIdx).request()
        if result.success:
            self.__nyController.onBoughtToy()
            self.__nyController.setHangToyEffectEnabled(True)
            serviceChannel = self.__systemMessages.proto.serviceChannel
            serviceChannel.pushClientMessage(result.auxData, SCH_CLIENT_MSG_TYPE.NY_BREED_BOUGHT_MESSAGE)
        elif result.userMsg:
            SystemMessages.pushMessage(text=backport.text(R.strings.system_messages.newYear.breed.bought.error.body()), type=SystemMessages.SM_TYPE.ErrorHeader, priority=NotificationPriorityLevel.MEDIUM, messageData={'header': backport.text(R.strings.system_messages.newYear.breed.bought.error.header())})
        self.__isRequestToBuyProcessing = False
        self.destroyWindow()

    def __onBuyGold(self):
        price = getBreedPrice(self.__currentBreedIdx)
        currency = price.getCurrency()
        value = price.get(currency, 0)
        if value and currency and currency == Currency.GOLD:
            showBuyGoldForBreed(value)


class BreedPurchaseDialogWindow(LobbyWindow):
    __slots__ = ('_blur',)

    def __init__(self, parent=None, layer=WindowLayer.FULLSCREEN_WINDOW, *args, **kwargs):
        super(BreedPurchaseDialogWindow, self).__init__(DialogFlags.TOP_FULLSCREEN_WINDOW, content=BreedPurchaseDialog(*args, **kwargs), layer=layer, parent=parent)
        self._blur = None
        return

    def _initialize(self):
        super(BreedPurchaseDialogWindow, self)._initialize()
        self._blur = CachedBlur(enabled=True, ownLayer=self.layer - 1)

    def _finalize(self):
        if self._blur:
            self._blur.fini()
            self._blur = None
        super(BreedPurchaseDialogWindow, self)._finalize()
        return
