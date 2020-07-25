# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/dialogs/need_repair.py
import typing
from frameworks.wulf import ViewSettings, ViewFlags
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.tank_setup.dialogs.need_repair_bottom_content_type import NeedRepairBottomContentType
from gui.impl.gen.view_models.views.lobby.tank_setup.dialogs.need_repair_model import NeedRepairModel
from gui.impl.lobby.dialogs.contents.exchange_content import ExchangeContentResult
from gui.impl.lobby.tank_setup.dialogs.bottom_content.bottom_contents import NeedRepairBottomContent
from gui.impl.lobby.dialogs.buy_and_exchange import BuyAndExchange
from gui.impl.lobby.dialogs.auxiliary.buy_and_exchange_state_machine import BuyAndExchangeStateEnum
from gui.impl.lobby.tank_setup.dialogs.main_content.main_contents import NeedRepairMainContent
from gui.shared.gui_items.gui_item_economics import Money
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.Vehicle import Vehicle

class NeedRepair(BuyAndExchange):
    __slots__ = ('__vehicle', '_buyContent', '_mainContent')

    def __init__(self, *args, **kwargs):
        self.__vehicle = kwargs.pop('vehicle', None)
        settings = ViewSettings(layoutID=R.views.lobby.tanksetup.dialogs.NeedRepair(), flags=ViewFlags.TOP_WINDOW_VIEW, model=NeedRepairModel())
        settings.args = args
        settings.kwargs = kwargs
        startState = kwargs.pop('startState', None)
        self._buyContent = None
        self._mainContent = None
        super(NeedRepair, self).__init__(settings, price=self.__getPrice(), startState=startState)
        return

    @property
    def viewModel(self):
        return self.getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(NeedRepair, self)._onLoading(*args, **kwargs)
        self._buyContent = NeedRepairBottomContent(viewModel=self.viewModel.dealPanel, vehicle=self.__vehicle)
        self._buyContent.onLoading()
        self._mainContent = NeedRepairMainContent(viewModel=self.viewModel.needRepairContent, repairPercentage=self.__calculateRepairPercentage())
        self._mainContent.onLoading()

    def _initialize(self, *args, **kwargs):
        super(NeedRepair, self)._initialize(*args, **kwargs)
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
        super(NeedRepair, self)._finalize()
        return

    def _onInventoryResync(self, *args, **kwargs):
        super(NeedRepair, self)._onInventoryResync(*args, **kwargs)
        if self._buyContent is not None:
            self._buyContent.update()
        return

    def _stateToContent(self):
        stateToContent = super(NeedRepair, self)._stateToContent()
        stateToContent[BuyAndExchangeStateEnum.BUY_NOT_REQUIRED] = NeedRepairBottomContentType.NOT_NEED_REPAIR
        return stateToContent

    def _exchangeComplete(self, result):
        if result == ExchangeContentResult.IS_OK:
            self._onAccept()

    def _onAccept(self):
        if self._buyContent is not None:
            self._buyContent.processAutoRepair()
        super(NeedRepair, self)._onAccept()
        return

    def _onCancel(self):
        if self._buyContent is not None:
            self._buyContent.processAutoRepair()
        super(NeedRepair, self)._onCancel()
        return

    def __calculateRepairPercentage(self):
        repairCost = self.__vehicle.repairCost
        maxRepairCost = self.__vehicle.descriptor.getMaxRepairCost()
        return round((maxRepairCost - repairCost) * 100 / maxRepairCost)

    def __getPrice(self):
        return Money(credits=self.__vehicle.repairCost)
