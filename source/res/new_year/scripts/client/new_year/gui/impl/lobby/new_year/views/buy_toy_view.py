# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/lobby/new_year/views/buy_toy_view.py
from debug_utils import LOG_ERROR
from frameworks.wulf import ViewSettings
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogView
from helpers import dependency
from skeletons.gui.game_control import IWalletController
from new_year.gui.impl.gen.view_models.common.ny_currency_type_model import NyCurrencyType
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.buy_toy_view_model import BuyToyViewModel
from new_year.gui.impl.lobby.new_year.tooltips.ny_common_tooltip import NyCommonTooltip, getCommonTooltipArgsFromEvent
from new_year.gui.shared.ny_currency_provider import NyCurrencyProvider
from new_year.skeletons.new_year import INewYearController

class BuyToyView(FullScreenDialogView):
    __nyController = dependency.descriptor(INewYearController)
    __wallet = dependency.descriptor(IWalletController)
    __slots__ = ('__toyID', '__currencyProvider')
    LAYOUT_ID = R.views.new_year.lobby.new_year.views.BuyToyView()

    def __init__(self, toyID, *args, **kwargs):
        settings = ViewSettings(self.LAYOUT_ID)
        settings.model = BuyToyViewModel()
        settings.args = args
        settings.kwargs = kwargs
        super(BuyToyView, self).__init__(settings)
        self.__toyID = toyID
        self.__currencyProvider = NyCurrencyProvider()

    @property
    def viewModel(self):
        return super(BuyToyView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        tooltips = R.views.new_year.lobby.new_year.tooltips
        return NyCommonTooltip(*getCommonTooltipArgsFromEvent(event)) if contentID == tooltips.CommonTooltip() else super(BuyToyView, self).createToolTipContent(event, contentID)

    def _addListeners(self):
        self.viewModel.onBuy += self.__onBuy
        self.viewModel.onClose += self.__onClose

    def _removeListeners(self):
        self.viewModel.onBuy -= self.__onBuy
        self.viewModel.onClose -= self.__onClose

    def _setBaseParams(self, model):
        pass

    def _getAdditionalData(self):
        return {}

    def __onBuy(self):
        self._onAccept()
        self.destroy()

    def __onClose(self):
        self._onExitClicked()
        self.destroy()

    def _onLoading(self, *args, **kwargs):
        super(BuyToyView, self)._onLoading(*args, **kwargs)
        if self.__toyID is None:
            LOG_ERROR("Toy id can't be None")
            return
        else:
            toy = self.__nyController.getToyByID(self.__toyID)
            if not toy:
                LOG_ERROR("Can't get toy from cache by it id=({})".format(self.__toyID))
                return
            self.__fillModel(toy)
            return

    def __fillModel(self, toy):
        goldPrice = toy.getPrice().gold
        toyName = backport.text(toy.getName())
        toyIcon = toy.getIconName()
        currentCurrencyAmount = self.__currencyProvider.getCurrencyCount(NyCurrencyType.GOLD)
        isBuyButtonDisable = currentCurrencyAmount < goldPrice or not self.__wallet.isAvailable
        with self.viewModel.transaction() as tx:
            tx.setIsBuyBtnDisable(isBuyButtonDisable)
            tx.setCost(goldPrice)
            tx.setToyName(toyName)
            tx.setToyIcon(toyIcon)
