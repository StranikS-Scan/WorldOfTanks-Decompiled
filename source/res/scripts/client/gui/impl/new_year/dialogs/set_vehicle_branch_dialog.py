# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/dialogs/set_vehicle_branch_dialog.py
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.dialogs.contents.common_balance_content import CommonBalanceContent, CurrencyStatus
from gui.impl.lobby.dialogs.contents.prices_content import DialogPricesContent
from gui.impl.pub.dialog_window import DialogButtons
from gui.impl.pub.lobby_dialog_window import LobbyDialogWindow
from gui.shared.money import Currency
from helpers import dependency
from skeletons.gui.game_control import IWalletController
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import INewYearController

class SetVehicleBranchDialogWindow(LobbyDialogWindow):
    _itemsCache = dependency.descriptor(IItemsCache)
    _nyController = dependency.descriptor(INewYearController)
    _wallet = dependency.descriptor(IWalletController)
    __slots__ = ('__veh', '__slot')

    def __init__(self, invID, slotID):
        self.__veh = self._itemsCache.items.getVehicle(invID)
        self.__slot = self._nyController.getVehicleBranch().getVehicleSlots()[slotID]
        super(SetVehicleBranchDialogWindow, self).__init__(bottomContent=DialogPricesContent(), balanceContent=CommonBalanceContent(), enableBlur=True)

    def _initialize(self):
        super(SetVehicleBranchDialogWindow, self)._initialize()
        with self.viewModel.transaction() as model:
            if self.__slot.getVehicle():
                applyText = R.strings.ny.dialogs.setVehicleBranch.btnApply()
            else:
                applyText = R.strings.ny.dialogs.setVehicleBranch.btnSelect()
            self._addButton(DialogButtons.PURCHASE, applyText, isFocused=True)
            self._addButton(DialogButtons.CANCEL, R.strings.ny.dialogs.setVehicleBranch.btnCancel(), invalidateAll=True)
            self.__setTitle(model)
            self.__setBottomContent()
            self.__updateIsEnough()
        g_clientUpdateManager.addMoneyCallback(self.__onMoneyUpdated)

    def _finalize(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(SetVehicleBranchDialogWindow, self)._finalize()

    def __setBottomContent(self):
        cost = self.__slot.getChangePrice()
        currency = cost.getCurrency()
        if currency == Currency.CREDITS:
            img = R.images.gui.maps.icons.library.CreditsIcon_1()
        else:
            img = R.images.gui.maps.icons.library.GoldIcon_1()
        with self.bottomContentViewModel.transaction() as model:
            model.valueMain.setValue(backport.getIntegralFormat(cost.get(currency)))
            model.valueMain.setIcon(img)

    def __setTitle(self, model):
        model.setTitle(R.strings.ny.dialogs.setVehicleBranch.title() if self.__slot.getVehicle() else R.strings.ny.dialogs.setVehicleBranch.addVehicleTitle())
        model.setIsTitleFmtArgsNamed(False)
        if self.__slot.getVehicle():
            model.getTitleArgs().addString(self.__slot.getVehicle().userName)
        model.getTitleArgs().addString(self.__veh.userName)
        model.getTitleArgs().invalidate()

    def __updateIsEnough(self):
        price = self.__slot.getChangePrice()
        currency = price.getCurrency()
        isAvailable = self._wallet.componentsStatuses[currency] == CurrencyStatus.AVAILABLE
        if currency == Currency.CREDITS:
            isEnough = price.credits <= self._itemsCache.items.stats.credits
        else:
            isEnough = price.gold <= self._itemsCache.items.stats.gold
        self.bottomContentViewModel.valueMain.setNotEnough(not isEnough)
        self._setButtonEnabled(DialogButtons.PURCHASE, isEnough and isAvailable)

    def __onMoneyUpdated(self, _):
        self.__updateIsEnough()
