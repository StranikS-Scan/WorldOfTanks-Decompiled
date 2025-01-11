# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: advent_calendar/scripts/client/advent_calendar/gui/impl/lobby/feature/purchase_dialog_view.py
from collections import namedtuple
from advent_calendar.gui.impl.gen.view_models.views.lobby.purchase_dialog_model import PurchaseDialogModel
from advent_calendar.gui.impl.lobby.feature.container_view import AdventCalendarContainerView
from advent_calendar.gui.impl.lobby.feature.ny_components.ny_kit_view import AdventCalendarNYKit
from advent_calendar.gui.impl.lobby.feature.ny_components.ny_resources_balance_view import NYResourceBalance
from frameworks.wulf import ViewSettings
from gui.game_control.wallet import WalletController
from gui.impl.gen import R
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogBaseView
from gui.impl.new_year.new_year_helper import backportTooltipDecorator
from gui.impl.pub.dialog_window import DialogButtons
from gui.shared.event_dispatcher import showLootBoxEntry
from helpers import dependency
from skeletons.gui.game_control import IWalletController
from skeletons.new_year import INewYearController
PurchaseData = namedtuple('PurchaseData', ('dayId', 'resourceStr'))

class PurchaseDialogView(AdventCalendarContainerView, FullScreenDialogBaseView):
    _nyController = dependency.descriptor(INewYearController)
    _wallet = dependency.descriptor(IWalletController)

    def __init__(self, dayId, price, *args, **kwargs):
        settings = ViewSettings(R.views.advent_calendar.lobby.feature.PurchaseDialogView(), model=PurchaseDialogModel(), args=args, kwargs=kwargs)
        self.__dayId = dayId
        self.__price = price
        super(PurchaseDialogView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(PurchaseDialogView, self).getViewModel()

    @backportTooltipDecorator()
    def createToolTip(self, event):
        return super(PurchaseDialogView, self).createToolTip(event)

    def _registerSubModels(self):
        return [NYResourceBalance(self.viewModel.balance, self, self.__onClose, self.__nyKitUpdated), AdventCalendarNYKit(self.viewModel.resources, self, self.__price)]

    def _onLoading(self, *args, **kwargs):
        super(PurchaseDialogView, self)._onLoading(args, kwargs)
        with self.viewModel.transaction() as model:
            model.setDayId(self.__dayId)
            currencyStatus = self._wallet.dynamicComponentsStatuses.get(self.viewModel.resources.getCurrentResource())
            model.setIsWalletAvailable(currencyStatus == WalletController.STATUS.AVAILABLE)

    def _getEvents(self):
        return ((self.viewModel.onAccept, self.__onAccept),
         (self.viewModel.onCancel, self.__onClose),
         (self.viewModel.onSwitchToBoxes, self.__onOpenBoxes),
         (self._wallet.onWalletStatusChanged, self.__onWalletStatusChanged))

    def _getAdditionalData(self):
        return PurchaseData(dayId=self.__dayId, resourceStr=self.viewModel.resources.getCurrentResource().encode('utf-8'))

    def __onClose(self):
        self._setResult(DialogButtons.CANCEL)

    def __onAccept(self):
        self._setResult(DialogButtons.PURCHASE)

    def __onOpenBoxes(self):
        self._setResult(DialogButtons.CANCEL)
        self.destroyWindow()
        showLootBoxEntry()

    def __nyKitUpdated(self):
        pass

    def __onWalletStatusChanged(self, *_):
        with self.viewModel.transaction() as model:
            currencyStatus = self._wallet.dynamicComponentsStatuses.get(self.viewModel.resources.getCurrentResource())
            model.setIsWalletAvailable(currencyStatus == WalletController.STATUS.AVAILABLE)
