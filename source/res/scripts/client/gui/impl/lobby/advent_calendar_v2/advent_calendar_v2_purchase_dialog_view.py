# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/advent_calendar_v2/advent_calendar_v2_purchase_dialog_view.py
from collections import namedtuple
from frameworks.wulf import ViewSettings
from gui.game_control.wallet import WalletController
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.advent_calendar.advent_calendar_purchase_dialog_model import AdventCalendarPurchaseDialogModel
from gui.impl.lobby.advent_calendar_v2.advent_calendar_v2_parent_view import AdventCalendarParentView
from gui.impl.lobby.advent_calendar_v2.ny_components.advent_calendar_v2_ny_kit_view import AdventCalendarNYKit
from gui.impl.lobby.advent_calendar_v2.ny_components.advent_calendar_v2_ny_resources_balance_view import AdventCalendarNYResourceBalance
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogBaseView
from gui.impl.new_year.new_year_helper import backportTooltipDecorator
from gui.impl.pub.dialog_window import DialogButtons
from gui.shared.event_dispatcher import showLootBoxEntry
from helpers import dependency
from skeletons.gui.game_control import IWalletController
from skeletons.new_year import INewYearController
PurchaseData = namedtuple('PurchaseData', ('dayId', 'resourceStr'))

class AdventCalendarPurchaseDialogView(AdventCalendarParentView, FullScreenDialogBaseView):
    _nyController = dependency.descriptor(INewYearController)
    _wallet = dependency.descriptor(IWalletController)

    def __init__(self, dayId, price, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.advent_calendar.PurchaseDialogView())
        settings.args, settings.kwargs, settings.model = args, kwargs, AdventCalendarPurchaseDialogModel()
        self.__dayId = dayId
        self.__price = price
        super(AdventCalendarPurchaseDialogView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(AdventCalendarPurchaseDialogView, self).getViewModel()

    @backportTooltipDecorator()
    def createToolTip(self, event):
        return super(AdventCalendarPurchaseDialogView, self).createToolTip(event)

    @staticmethod
    def canBeClosed():
        return True

    def _registerSubModels(self):
        return [AdventCalendarNYResourceBalance(self.viewModel.balance, self, self.__onClose, self.__nyKitUpdated), AdventCalendarNYKit(self.viewModel.resources, self, self.__price)]

    def _onLoading(self, *args, **kwargs):
        super(AdventCalendarPurchaseDialogView, self)._onLoading(args, kwargs)
        with self.viewModel.transaction() as model:
            model.setDayId(self.__dayId)
            currencyStatus = self._wallet.dynamicComponentsStatuses.get(self.viewModel.resources.getCurrentResource())
            model.setIsWalletAvailable(currencyStatus == WalletController.STATUS.AVAILABLE)

    def _getEvents(self):
        return ((self.viewModel.onAccept, self.__onAccept),
         (self.viewModel.onCancel, self.__onClose),
         (self.viewModel.onSwithToBoxes, self.__onOpenBoxes),
         (self._wallet.onWalletStatusChanged, self.__onWalletStatusChanged))

    def _getAdditionalData(self):
        return PurchaseData(dayId=self.__dayId, resourceStr=self.viewModel.resources.getCurrentResource().encode('utf-8'))

    def __onClose(self):
        self._setResult(DialogButtons.CANCEL)

    def __onOpenBoxes(self):
        self._setResult(DialogButtons.CANCEL)
        self.destroyWindow()
        showLootBoxEntry()

    def __onAccept(self):
        self._setResult(DialogButtons.PURCHASE)

    def __nyKitUpdated(self):
        pass

    def __onWalletStatusChanged(self, *_):
        with self.viewModel.transaction() as model:
            currencyStatus = self._wallet.dynamicComponentsStatuses.get(self.viewModel.resources.getCurrentResource())
            model.setIsWalletAvailable(currencyStatus == WalletController.STATUS.AVAILABLE)
