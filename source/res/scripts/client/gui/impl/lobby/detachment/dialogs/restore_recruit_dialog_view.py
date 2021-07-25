# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/dialogs/restore_recruit_dialog_view.py
import logging
from async import await, async
from frameworks.wulf import ViewSettings
from gui import SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.game_control.restore_contoller import getTankmenRestoreInfo
from gui.impl import backport
from gui.impl.auxiliary.detachment_helper import fillRecruitModel
from gui.impl.backport.backport_tooltip import createAndLoadBackportTooltipWindow
from gui.impl.dialogs.dialogs import showConvertCurrencyForRestoreTankmanView
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.dialogs.restore_recruit_view_model import RestoreRecruitViewModel
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogView
from gui.impl.pub.dialog_window import DialogButtons
from gui.shared.event_dispatcher import mayObtainWithMoneyExchange, getLoadedView
from gui.shared.gui_items.processors.common import GoldToCreditsExchanger
from gui.shared.money import Currency
from gui.shared.tooltips.tankman import formatRecoveryLeftValue
from gui.shared.utils import decorators
from helpers import dependency
from skeletons.gui.game_control import IRestoreController
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)
SUF_PNG = '.png'

class RestoreRecruitDialogView(FullScreenDialogView):
    __itemsCache = dependency.descriptor(IItemsCache)
    __restoreController = dependency.descriptor(IRestoreController)
    __slots__ = ('__recruitID', '__layoutID')

    def __init__(self, recruitID):
        self.__layoutID = R.views.lobby.detachment.dialogs.RestoreRecruitDialogView()
        self.__recruitID = recruitID
        settings = ViewSettings(layoutID=self.__layoutID, model=RestoreRecruitViewModel())
        super(RestoreRecruitDialogView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(RestoreRecruitDialogView, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            if tooltipId == TOOLTIPS_CONSTANTS.NOT_ENOUGH_MONEY:
                return createAndLoadBackportTooltipWindow(self.getParentWindow(), isSpecial=True, tooltipId=tooltipId, specialArgs=(self.__shortage(), self.__currencyType()))
        return super(RestoreRecruitDialogView, self).createToolTip(event)

    def _onLoading(self):
        super(RestoreRecruitDialogView, self)._onLoading()
        self.__fillViewModel()

    def _onAcceptClicked(self):
        if self.__shortage():
            if self.__currencyType() == Currency.CREDITS:
                self.__showExchangeDialog()
        else:
            self._onAccept()

    def _onCancel(self):
        exchangeView = getLoadedView(R.views.lobby.detachment.dialogs.ConvertCurrencyView())
        if exchangeView:
            exchangeView.destroy()
        super(RestoreRecruitDialogView, self)._onCancel()

    def _addListeners(self):
        super(RestoreRecruitDialogView, self)._addListeners()
        self.__restoreController.onTankmenBufferUpdated += self.__updateBufferChanges
        g_clientUpdateManager.addMoneyCallback(self.__updateClient)

    def _removeListeners(self):
        self.__restoreController.onTankmenBufferUpdated -= self.__updateBufferChanges
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(RestoreRecruitDialogView, self)._removeListeners()

    def __updateClient(self, *args, **kwargs):
        self.__fillViewModel()

    def __updateBufferChanges(self, *args, **kwargs):
        dismissRecruit = self.__itemsCache.items.getTankman(self.__recruitID)
        if not dismissRecruit:
            self._onCancel()

    @async
    def __showExchangeDialog(self):
        sdr = yield await(showConvertCurrencyForRestoreTankmanView(ctx={'needCredits': self.__shortage(),
         'tankmanInvID': self.__recruitID}))
        if sdr.busy:
            return
        isOk, data = sdr.result
        if isOk == DialogButtons.SUBMIT:
            self.__exchange(int(data['gold']))
        self.__fillViewModel()

    def __tankman(self):
        tankman = self.__itemsCache.items.getTankman(self.__recruitID)
        if tankman is None:
            _logger.error('Attempt to dismiss tankman by invalid invID: %r', self.__recruitID)
            return
        else:
            return tankman

    def __getPrice(self):
        price, _ = self.__retoreInfo()
        return price

    def __retoreInfo(self):
        return getTankmenRestoreInfo(self.__tankman())

    def __shortage(self):
        shortage = self._stats.money.getShortage(self.__getPrice())
        return shortage.get(self.__currencyType())

    def __currencyType(self):
        return self.__getPrice().getCurrency()

    def __disabledAccept(self):
        shortage = self.__shortage()
        if self.__currencyType() == Currency.CREDITS and shortage:
            return not self.__checkEnoughGoldForExchangeToCredits()
        return False if self.__currencyType() == Currency.GOLD else bool(shortage)

    def __checkEnoughGoldForExchangeToCredits(self):
        return mayObtainWithMoneyExchange(self.__getPrice(), itemsCache=self.__itemsCache)

    def __fillViewModel(self):
        tankman = self.__tankman()
        price, timeLeft = self.__retoreInfo()
        with self.viewModel.transaction() as vm:
            if not price:
                vm.setIsShowPrice(False)
            else:
                vm.setIsShowPrice(True)
                vm.priceModel.setType(self.__currencyType())
                vm.priceModel.setHasDiscount(False)
                vm.setIsAcceptDisabled(self.__disabledAccept())
                vm.priceModel.setValue(price.get(self.__currencyType()))
                vm.priceModel.setIsEnough(not bool(self.__shortage()))
                vm.setTimeLeft(formatRecoveryLeftValue(timeLeft))
            descr = '{}, {} {}'.format(tankman.roleUserName, backport.text(R.strings.menu.tankmen.dyn(tankman.vehicleNativeType)()), tankman.vehicleNativeDescr.type.shortUserString)
            fillRecruitModel(vm.recruitModel, tankman, descr)

    @decorators.process('transferMoney')
    def __exchange(self, gold):
        result = yield GoldToCreditsExchanger(gold, withConfirm=False).request()
        if result and result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
            self._onAccept()
