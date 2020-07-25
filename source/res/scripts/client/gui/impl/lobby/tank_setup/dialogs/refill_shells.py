# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/dialogs/refill_shells.py
import typing
from frameworks.wulf import ViewSettings, ViewFlags
from gui.impl.gen import R
from gui.impl.gen.view_models.constants.fitting_types import FittingTypes
from gui.impl.gen.view_models.views.lobby.tank_setup.dialogs.confirm_bottom_content_type import ConfirmBottomContentType
from gui.impl.gen.view_models.views.lobby.tank_setup.dialogs.refill_shells_model import RefillShellsModel
from gui.impl.lobby.dialogs.contents.exchange_content import ExchangeContentResult
from gui.impl.lobby.dialogs.contents.multiple_items_content import MultipleItemsContent
from gui.impl.lobby.tank_setup.dialogs.bottom_content.bottom_contents import PriceBottomContent
from gui.impl.lobby.dialogs.buy_and_exchange import BuyAndExchange
from gui.impl.lobby.dialogs.auxiliary.buy_and_exchange_state_machine import BuyAndExchangeStateEnum
from gui.shared.gui_items.gui_item_economics import ITEM_PRICE_ZERO
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.gui_item_economics import ItemPrice

class RefillShells(BuyAndExchange):
    __slots__ = ('__price', '_buyContent', '_mainContent', '__shells')

    def __init__(self, *args, **kwargs):
        self.__price = kwargs.pop('price', ITEM_PRICE_ZERO)
        settings = ViewSettings(layoutID=R.views.lobby.tanksetup.dialogs.RefillShells(), flags=ViewFlags.TOP_WINDOW_VIEW, model=RefillShellsModel())
        settings.args = args
        settings.kwargs = kwargs
        startState = kwargs.pop('startState', None)
        self._buyContent = None
        self._mainContent = None
        self.__shells = kwargs.pop('shells', [])
        super(RefillShells, self).__init__(settings, price=self.__price.price, startState=startState)
        return

    @property
    def viewModel(self):
        return self.getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(RefillShells, self)._onLoading(*args, **kwargs)
        self._buyContent = PriceBottomContent(viewModel=self.viewModel.dealPanel, price=self.__price.price, defPrice=self.__price.defPrice)
        self._buyContent.onLoading()
        self._mainContent = MultipleItemsContent(viewModel=self.viewModel.mainContent, items=self.__shells, itemsType=FittingTypes.SHELL)
        self._mainContent.onLoading()

    def _initialize(self, *args, **kwargs):
        super(RefillShells, self)._initialize()
        if self._buyContent is not None:
            self._buyContent.initialize()
        if self._mainContent is not None:
            self._mainContent.initialize()
        return

    def _finalize(self):
        if self._mainContent is not None:
            self._mainContent.finalize()
        if self._buyContent is not None:
            self._buyContent.finalize()
        super(RefillShells, self)._finalize()
        return

    def _onInventoryResync(self, *args, **kwargs):
        super(RefillShells, self)._onInventoryResync(*args, **kwargs)
        if self._buyContent is not None:
            self._buyContent.update()
        return

    def _exchangeComplete(self, result):
        if result == ExchangeContentResult.IS_OK:
            self._onAccept()

    def _stateToContent(self):
        stateToContent = super(RefillShells, self)._stateToContent()
        stateToContent[BuyAndExchangeStateEnum.BUY_NOT_REQUIRED] = ConfirmBottomContentType.SAVE_SLOTS_CONTENT
        return stateToContent

    def _buyNotRequiredAccept(self):
        self._onAccept()


class ExitFromShellsConfirm(RefillShells):
    __slots__ = ('__rollBack',)

    def __init__(self, *args, **kwargs):
        super(ExitFromShellsConfirm, self).__init__(*args, **kwargs)
        self.__rollBack = False

    def _onLoading(self, *args, **kwargs):
        super(ExitFromShellsConfirm, self)._onLoading(*args, **kwargs)
        self.viewModel.setWithRollback(True)

    def _getAdditionalData(self):
        return {'rollBack': self.__rollBack}

    def _onCancelClicked(self):
        self.__rollBack = True
        self._onCancel()
