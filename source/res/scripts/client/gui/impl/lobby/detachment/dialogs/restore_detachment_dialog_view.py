# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/dialogs/restore_detachment_dialog_view.py
from async import await, async
from crew2 import settings_globals
from frameworks.wulf import ViewSettings
from gui import SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.auxiliary.detachment_helper import fillRoseSheetsModel, fillDetachmentBaseModel, getDetachmentRestorePrice
from gui.impl.backport.backport_tooltip import createAndLoadBackportTooltipWindow
from gui.impl.dialogs.dialogs import buyDormitory, showConvertCurrencyForRestoreDetachmentView
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.dialogs.restore_detachment_dialog_view_model import RestoreDetachmentDialogViewModel
from gui.impl.lobby.detachment.tooltips.detachment_info_tooltip import DetachmentInfoTooltip
from gui.impl.lobby.detachment.tooltips.instructor_tooltip import getInstructorTooltip
from gui.impl.lobby.detachment.tooltips.level_badge_tooltip_view import LevelBadgeTooltipView
from gui.impl.lobby.detachment.tooltips.skills_branch_view import SkillsBranchTooltipView
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogView
from gui.impl.pub.dialog_window import DialogButtons
from gui.shared.event_dispatcher import mayObtainWithMoneyExchange, getLoadedView
from gui.shared.gui_items.processors.common import GoldToCreditsExchanger, DormitoryBuyer
from gui.shared.items_cache import hasFreeDormsRooms, needDormsBlock
from gui.shared.money import Currency, MONEY_UNDEFINED
from gui.shared.utils import decorators
from gui.shop import showBuyGoldForDetachmentRestore
from helpers import dependency
from helpers import time_utils
from helpers.CallbackDelayer import CallbackDelayer
from items import ITEM_TYPES
from items.components.dormitory_constants import BuyDormitoryReason
from skeletons.gui.detachment import IDetachmentCache
from skeletons.gui.shared import IItemsCache
from uilogging.detachment.constants import ACTION, GROUP
from uilogging.detachment.loggers import DetachmentLogger, g_detachmentFlowLogger

class RestoreDetachmentDialogView(FullScreenDialogView):
    __itemsCache = dependency.descriptor(IItemsCache)
    __detachmentCache = dependency.descriptor(IDetachmentCache)
    _SPECIAL_RESTORE_TERM = settings_globals.g_detachmentSettings.specialRestoreTerm * time_utils.ONE_DAY
    _HOLD_IN_RECYCLE_BIN_TERM = settings_globals.g_detachmentSettings.holdInRecycleBinTerm * time_utils.ONE_DAY
    uiLogger = DetachmentLogger(GROUP.RESTORE_DETACHMENT_DIALOG)
    __slots__ = ('__detInvID', '__detachment', '__priceMoney', '__currentCurrency', '__callbackExpSpecialTerm', '__callbackExpHoldTerm', '__isDiscount', '__defPriceMoney', '__specialTerm')

    def __init__(self, ctx):
        settings = ViewSettings(R.views.lobby.detachment.dialogs.RestoreDetachmentDialogView())
        settings.model = RestoreDetachmentDialogViewModel()
        super(RestoreDetachmentDialogView, self).__init__(settings)
        self.__detInvID = ctx.get('detInvID')
        self.__detachment = self.__detachmentCache.getDetachment(self.__detInvID)
        self.__priceMoney = MONEY_UNDEFINED
        self.__currentCurrency = Currency.CREDITS
        self.__defPriceMoney = MONEY_UNDEFINED
        self.__isDiscount = False
        self.__specialTerm = 0
        self.__callbackExpSpecialTerm = CallbackDelayer()
        self.__callbackExpHoldTerm = CallbackDelayer()

    @property
    def viewModel(self):
        return self.getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            currency = self.__currentCurrency
            shortage = self._shortage()
            if tooltipId == TOOLTIPS_CONSTANTS.NOT_ENOUGH_MONEY:
                return createAndLoadBackportTooltipWindow(self.getParentWindow(), isSpecial=True, tooltipId=tooltipId, specialArgs=(shortage, currency))
            if tooltipId == RestoreDetachmentDialogViewModel.PRICE_TOOLTIP:
                isDiscount = self.__isDiscount
                if bool(shortage) and not isDiscount:
                    return createAndLoadBackportTooltipWindow(self.getParentWindow(), isSpecial=True, tooltipId=TOOLTIPS_CONSTANTS.NOT_ENOUGH_MONEY, specialArgs=(shortage, currency))
                if isDiscount:
                    specialArgs = (self._currentPrice(),
                     self._defPrice(),
                     currency,
                     not bool(shortage),
                     not bool(self._shortageDef()))
                    return createAndLoadBackportTooltipWindow(self.getParentWindow(), isSpecial=True, tooltipId=TOOLTIPS_CONSTANTS.PRICE_DISCOUNT, specialArgs=specialArgs)
        return super(RestoreDetachmentDialogView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        detachmentID = event.getArgument('detachmentId')
        if contentID == R.views.lobby.detachment.tooltips.InstructorTooltip():
            instructorID = event.getArgument('instructorInvID')
            detachment = self.__detachmentCache.getDetachment(detachmentID)
            tooltip = getInstructorTooltip(instructorID, detachment)
            if hasattr(tooltip, 'uiLogger'):
                tooltip.uiLogger.setGroup(self.uiLogger.group)
            return tooltip
        if contentID == R.views.lobby.detachment.tooltips.SkillsBranchTooltip():
            course = event.getArgument('course')
            SkillsBranchTooltipView.uiLogger.setGroup(self.uiLogger.group)
            return SkillsBranchTooltipView(detachmentID=detachmentID, branchID=int(course) + 1)
        if event.contentID == R.views.lobby.detachment.tooltips.DetachmentInfoTooltip():
            return DetachmentInfoTooltip(detachmentInvID=self.__detInvID)
        return LevelBadgeTooltipView(self.__detInvID) if event.contentID == R.views.lobby.detachment.tooltips.LevelBadgeTooltip() else super(RestoreDetachmentDialogView, self).createToolTipContent(event, contentID)

    def _addListeners(self):
        super(RestoreDetachmentDialogView, self)._addListeners()
        self.__itemsCache.onSyncCompleted += self.__onUpdate
        g_clientUpdateManager.addCallbacks({'inventory.{}'.format(ITEM_TYPES.detachment): self.__onUpdate,
         'shop.detachmentPriceGroups': self.__onUpdate,
         'stats.gold': self.__onUpdate,
         'stats.credits': self.__onUpdate})

    def _removeListeners(self):
        self.__itemsCache.onSyncCompleted -= self.__onUpdate
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(RestoreDetachmentDialogView, self)._removeListeners()

    def _onAccept(self):
        self.uiLogger.log(ACTION.DIALOG_CONFIRM)
        self.__callbackExpSpecialTerm.destroy()
        self.__callbackExpHoldTerm.destroy()
        super(RestoreDetachmentDialogView, self)._onAccept()

    def _onAcceptClicked(self):
        if self._shortage():
            if self.__currentCurrency == Currency.GOLD:
                self.uiLogger.log(ACTION.BUY_GOLD)
                showBuyGoldForDetachmentRestore(self._currentPrice())
            elif self.__currentCurrency == Currency.CREDITS:
                self.uiLogger.log(ACTION.CONVERT_GOLD_TO_CREDITS)
                self.__showExchangeDialog()
        elif not hasFreeDormsRooms(itemsCache=self.__itemsCache):
            g_detachmentFlowLogger.flow(self.uiLogger.group, GROUP.BUY_DORMITORY_DIALOG)
            self.__buyDormitoryDialog()
        else:
            self._onAccept()

    def _onCancelClicked(self):
        self.uiLogger.log(ACTION.DIALOG_EXIT)
        super(RestoreDetachmentDialogView, self)._onCancelClicked()

    def _onExitClicked(self):
        self.uiLogger.log(ACTION.DIALOG_CANCEL)
        super(RestoreDetachmentDialogView, self)._onExitClicked()

    def _onCancel(self):
        self.__callbackExpSpecialTerm.destroy()
        self.__callbackExpHoldTerm.destroy()
        exchangeView = getLoadedView(R.views.lobby.detachment.dialogs.ConvertCurrencyView())
        if exchangeView:
            exchangeView.destroy()
        dormitoryView = getLoadedView(R.views.lobby.detachment.dialogs.BuyDormitoryDialogView())
        if dormitoryView:
            dormitoryView.destroy()
        super(RestoreDetachmentDialogView, self)._onCancel()

    def _setRoseData(self):
        with self.viewModel.transaction() as vm:
            fillRoseSheetsModel(vm.detachmentLine.roseModel, self.__detachment)

    def _onLoading(self, *args, **kwargs):
        super(RestoreDetachmentDialogView, self)._onLoading(*args, **kwargs)
        self.__fillModel()
        self.__initTimeCallback()

    def _getMoneyPrice(self, specialTerm):
        price = getDetachmentRestorePrice(self.__detInvID, specialTerm)
        defaultPrice = getDetachmentRestorePrice(self.__detInvID, specialTerm, default=True)
        return (price, defaultPrice, price.getCurrency())

    def _getPrice(self):
        currency = self.__currentCurrency
        return (self.__priceMoney.get(currency, 0), self.__defPriceMoney.get(currency, 0))

    def _currentPrice(self):
        return self.__priceMoney.get(self.__currentCurrency, 0)

    def _defPrice(self):
        return self.__defPriceMoney.get(self.__currentCurrency, 0)

    def _discountPercent(self, price, defPrice):
        return max(0, 100 - int(price * 100.0 / defPrice))

    def _shortage(self):
        priceMoney, _, _ = self._getMoneyPrice(self.__specialTerm)
        shortage = self._stats.money.getShortage(priceMoney)
        return shortage.get(self.__currentCurrency)

    def _shortageDef(self):
        _, defPriceMoney, _ = self._getMoneyPrice(self.__specialTerm)
        shortage = self._stats.money.getShortage(defPriceMoney)
        return shortage.get(self.__currentCurrency)

    def _getSpecialTerm(self):
        dismissalLength = time_utils.getTimeDeltaTillNow(self.__detachment.expDate - self._HOLD_IN_RECYCLE_BIN_TERM)
        isSpecialTerm = dismissalLength <= self._SPECIAL_RESTORE_TERM
        return (int(isSpecialTerm), self.__detachment.expDate) if not isSpecialTerm else (int(isSpecialTerm), 0)

    def __fillModel(self):
        with self.viewModel.transaction() as vm:
            self.__specialTerm, expDate = self._getSpecialTerm()
            self.__priceMoney, self.__defPriceMoney, self.__currentCurrency = self._getMoneyPrice(self.__specialTerm)
            currentPrice, defPrice = self._getPrice()
            self.__isDiscount = isDiscount = defPrice > 0 and defPrice > currentPrice
            fillDetachmentBaseModel(vm.detachmentLine, self.__detachment)
            vm.setTitleBody(R.strings.dialogs.detachment.restore.title())
            vm.setAcceptButtonText(R.strings.dialogs.detachment.restore.action())
            vm.setCancelButtonText(R.strings.detachment.common.cancel())
            vm.setIsAcceptDisabled(self.__disabledAccept())
            vm.price.setType(self.__currentCurrency)
            vm.price.setValue(currentPrice)
            vm.price.setIsEnough(not bool(self._shortage()))
            vm.price.setHasDiscount(isDiscount)
            if isDiscount:
                vm.price.setDiscountValue(self._discountPercent(currentPrice, defPrice))
            vm.setEndRestoreTime(int(expDate * time_utils.MS_IN_SECOND))
        self._setRoseData()

    def _getAdditionalData(self):
        return {'detInvID': self.__detInvID,
         'curPrice': self.__priceMoney,
         'curCurrency': self.__currentCurrency,
         'specialTerm': self.__specialTerm}

    def __onUpdate(self, *args, **kwargs):
        self.__fillModel()

    def __initTimeCallback(self):
        dismissalLength = time_utils.getTimeDeltaTillNow(self.__detachment.expDate - self._HOLD_IN_RECYCLE_BIN_TERM)
        delta = self._SPECIAL_RESTORE_TERM - dismissalLength
        if delta >= 0:
            self.__callbackExpSpecialTerm.delayCallback(delta + 1, self.__fillModel)
        delta = self._HOLD_IN_RECYCLE_BIN_TERM - dismissalLength
        seconds = delta if delta > 0 else 0
        self.__callbackExpHoldTerm.delayCallback(seconds, self._onCancel)

    def __disabledAccept(self):
        shortage = self._shortage()
        if self.__currentCurrency == Currency.CREDITS and shortage:
            return not self.__checkEnoughGoldForExchangeToCredits()
        return False if self.__currentCurrency == Currency.GOLD else bool(shortage)

    def __checkEnoughGoldForExchangeToCredits(self):
        return mayObtainWithMoneyExchange(self.__priceMoney, itemsCache=self.__itemsCache)

    @async
    def __buyDormitoryDialog(self):
        countBlocks = needDormsBlock(itemsCache=self.__itemsCache, detachmentCache=self.__detachmentCache)
        sdr = yield await(buyDormitory(self.getParentWindow(), countBlocks=countBlocks, reason=BuyDormitoryReason.RECOVER_DETACHMENT))
        if sdr.result:
            self.__buyDormitory(countBlocks)
        self.__fillModel()

    @decorators.process('buyDormitory')
    def __buyDormitory(self, countBlocks):
        result = yield DormitoryBuyer(countBlocks).request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
            self._onAccept()

    @async
    def __showExchangeDialog(self):
        sdr = yield await(showConvertCurrencyForRestoreDetachmentView(ctx={'needCredits': self._shortage(),
         'detInvID': self.__detInvID}))
        if sdr.busy:
            return
        isOk, data = sdr.result
        if isOk == DialogButtons.SUBMIT:
            self.__exchange(int(data['gold']))
        self.__fillModel()

    @decorators.process('transferMoney')
    def __exchange(self, gold):
        result = yield GoldToCreditsExchanger(gold, withConfirm=False).request()
        if result and result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
            self._onAccept()
