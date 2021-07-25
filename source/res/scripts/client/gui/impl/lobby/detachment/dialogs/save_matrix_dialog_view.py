# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/dialogs/save_matrix_dialog_view.py
import math
from async import await, async
from frameworks.wulf import ViewSettings
from goodies.goodie_constants import RECERTIFICATION_FORM_ID
from gui import SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.lobby.detachment.detachment_setup_vehicle import g_detachmentTankSetupVehicle
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.impl.auxiliary.detachment_helper import getDropSkillsPrice, getFirstDropSkillsPrice
from gui.impl.backport.backport_tooltip import createAndLoadBackportTooltipWindow
from gui.impl.dialogs.dialogs import showConvertCurrencyForSaveMatrixView
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.common.perk_short_model import PerkShortModel
from gui.impl.gen.view_models.views.lobby.detachment.dialogs.save_matrix_dialog_view_model import SaveMatrixDialogViewModel
from gui.impl.gen.view_models.views.lobby.detachment.tooltips.perk_tooltip_model import PerkTooltipModel
from gui.impl.gen.view_models.windows.selector_dialog_item_model import SelectorDialogItemModel
from gui.impl.lobby.detachment.tooltips.perk_tooltip import PerkTooltip
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogView
from gui.impl.pub.dialog_window import DialogButtons
from gui.shared.event_dispatcher import mayObtainWithMoneyExchange
from gui.shared.gui_items.processors.common import GoldToCreditsExchanger
from gui.shared.money import Currency
from gui.shared.utils import decorators
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from gui.shared.formatters import text_styles
from gui.shop import showBuyGoldForDetachmentSkillDrop, showBuyGoldForDetachmentSkillEdit
from helpers.dependency import descriptor
from items import ITEM_TYPES
from skeletons.gui.detachment import IDetachmentCache
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.shared import IItemsCache
from uilogging.detachment.constants import ACTION
from uilogging.detachment.loggers import PerksMatrixDialogLogger
_BACKPORT_NO_ARGS_TOOLTIPS = (TOOLTIPS_CONSTANTS.CREDITS_INFO_FULL_SCREEN, TOOLTIPS_CONSTANTS.RECERTIFICATION_FORM)

class SaveMatrixDialogView(FullScreenDialogView):
    __goodiesCache = descriptor(IGoodiesCache)
    __itemsCache = descriptor(IItemsCache)
    __detachmentCache = descriptor(IDetachmentCache)
    uiLogger = PerksMatrixDialogLogger()
    __slots__ = ('_operationType', '_perks', '_points', '_blankCount', '_selectedItem', '_ultimates', '_arePerksRemoved', '_areUltimatesRemoved', '_detInvID')

    def __init__(self, ctx):
        settings = ViewSettings(R.views.lobby.detachment.dialogs.SaveMatrixDialogView())
        settings.model = SaveMatrixDialogViewModel()
        self._operationType = ctx.get('operationType')
        self._ultimates = ctx.get('ultimates', {})
        self._perks = ctx.get('perks', {})
        self._points = ctx.get('points', 0)
        self._arePerksRemoved = ctx.get('arePerksRemoved')
        self._areUltimatesRemoved = ctx.get('areUltimatesRemoved')
        self._detInvID = ctx['detInvID']
        self._blankCount = 0
        self._selectedItem = None
        super(SaveMatrixDialogView, self).__init__(settings)
        self.uiLogger.setOperationType(self._operationType)
        return

    @property
    def viewModel(self):
        return super(SaveMatrixDialogView, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            if tooltipId in _BACKPORT_NO_ARGS_TOOLTIPS:
                specialArgs = None
                if tooltipId == TOOLTIPS_CONSTANTS.CREDITS_INFO_FULL_SCREEN:
                    _, currentDropCostPrice, defDropCostPrice = self.dropSkillPrice
                    shortage = self.__itemsCache.items.stats.money.getShortage(currentDropCostPrice)
                    currentCurrency = currentDropCostPrice.getCurrency()
                    if self.discount > 0:
                        tooltipId = TOOLTIPS_CONSTANTS.PRICE_DISCOUNT
                        shortageDef = self.__itemsCache.items.stats.money.getShortage(defDropCostPrice).get(currentCurrency)
                        specialArgs = (int(currentDropCostPrice.get(currentCurrency)),
                         int(defDropCostPrice.get(currentCurrency)),
                         currentCurrency,
                         not bool(shortage),
                         not bool(shortageDef))
                    elif bool(shortage):
                        tooltipId = TOOLTIPS_CONSTANTS.NOT_ENOUGH_MONEY
                        specialArgs = (shortage.get(currentCurrency), currentCurrency)
                return createAndLoadBackportTooltipWindow(self.getParentWindow(), isSpecial=True, tooltipId=tooltipId, specialArgs=specialArgs)
        return super(SaveMatrixDialogView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if event.contentID == R.views.lobby.detachment.tooltips.PerkTooltip():
            perkId = event.getArgument('id')
            selectedVehicle = g_detachmentTankSetupVehicle.defaultItem
            tempPoints = event.getArgument('tempPoints')
            return PerkTooltip(perkId, detachmentInvID=self._detInvID, tooltipType=PerkTooltipModel.DETACHMENT_PERK_TOOLTIP_SHORT, vehIntCD=selectedVehicle.intCD if selectedVehicle else None, tempPoints=int(tempPoints) if tempPoints is not None else None)
        else:
            return super(SaveMatrixDialogView, self).createToolTipContent(event, contentID)

    @property
    def dropSkillPrice(self):
        return getDropSkillsPrice(self._detInvID)

    @property
    def hasEnoughMoney(self):
        items = self.__itemsCache.items
        playerMoney = items.stats.money
        _, price, _ = self.dropSkillPrice
        for currency in Currency.GUI_ALL:
            cost = price.get(currency, default=0)
            if cost > playerMoney.get(currency, default=0):
                return False

        return True

    @property
    def currencyCost(self):
        _, price, _ = self.dropSkillPrice
        for currency in Currency.GUI_ALL:
            cost = price.get(currency, default=0)
            if cost:
                return cost

    @property
    def defCost(self):
        _, _, defPrice = self.dropSkillPrice
        for currency in Currency.GUI_ALL:
            cost = defPrice.get(currency, default=0)
            if cost:
                return cost

    @property
    def discount(self):
        return max(0, 100 - int(self.currencyCost * 100.0 / self.defCost)) if self.defCost else 0

    def _onLoading(self, *args, **kwargs):
        super(SaveMatrixDialogView, self)._onLoading(*args, **kwargs)
        self.__fillModel(*args, **kwargs)

    def _finalize(self):
        self.uiLogger.reset()
        super(SaveMatrixDialogView, self)._finalize()

    def _addListeners(self):
        super(SaveMatrixDialogView, self)._addListeners()
        self.viewModel.selector.onSelectItem += self._onSelectItem
        g_clientUpdateManager.addMoneyCallback(self.__fillModel)
        g_clientUpdateManager.addCallbacks({'shop.detachmentPriceGroups': self.__fillModel,
         'inventory.{}'.format(ITEM_TYPES.detachment): self.__fillModel,
         'goodies.{}'.format(RECERTIFICATION_FORM_ID): self.__fillModel})

    def _removeListeners(self):
        self.viewModel.selector.onSelectItem -= self._onSelectItem
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(SaveMatrixDialogView, self)._removeListeners()

    def _getAdditionalData(self):
        return {'useBlank': (self._arePerksRemoved or self._areUltimatesRemoved) and self._selectedItem == SaveMatrixDialogViewModel.BLANK}

    def _onSelectItem(self, args=None):
        if args is not None:
            self._selectedItem = args.get('type')
            with self.viewModel.transaction() as vm:
                selectorItems = vm.selector.getItems()
                for item in selectorItems:
                    item.setIsSelected(item.getType() == self._selectedItem)

                selectorItems.invalidate()
                vm.setIsAcceptDisabled(self.__getIsAcceptDisabled())
        return

    @async
    def _onAcceptClicked(self):
        if self._selectedItem == SaveMatrixDialogViewModel.CREDITS and not self.hasEnoughMoney:
            playerMoney = self.__itemsCache.items.stats.money
            playerCredits = playerMoney.get(Currency.CREDITS, default=0)
            playerGold = playerMoney.get(Currency.GOLD, default=0)
            needCredits = self.currencyCost - playerCredits
            exchangeRate = self.__itemsCache.items.shop.exchangeRate
            needGold = int(math.ceil(float(needCredits) / exchangeRate)) - playerGold
            if needGold <= 0:
                subtitle = self._operationType if self._operationType != SaveMatrixDialogViewModel.EXIT_CONFIRM else SaveMatrixDialogViewModel.EDIT
                title = R.strings.dialogs.detachment.saveMatrix.convertConfirm.dyn(subtitle).dyn(self.__titleType).title()
                sdr = yield await(showConvertCurrencyForSaveMatrixView(ctx={'needCredits': needCredits,
                 'title': title}))
                if sdr.busy:
                    return
                self.uiLogger.log(ACTION.CONVERT_GOLD_TO_CREDITS)
                isOk, data = sdr.result
                if isOk == DialogButtons.SUBMIT:
                    self.__exchangeGold(int(data['gold']))
            elif self._operationType in (SaveMatrixDialogViewModel.EDIT, SaveMatrixDialogViewModel.EXIT_CONFIRM):
                showBuyGoldForDetachmentSkillEdit(needGold)
            elif self._operationType == SaveMatrixDialogViewModel.CLEAR_ALL:
                showBuyGoldForDetachmentSkillDrop(needGold)
        else:
            self.uiLogger.log(ACTION.DIALOG_CONFIRM)
            super(SaveMatrixDialogView, self)._onAcceptClicked()

    def _onCancelClicked(self):
        self.uiLogger.log(ACTION.DIALOG_CANCEL)
        super(SaveMatrixDialogView, self)._onCancelClicked()

    def _onExitClicked(self):
        self.uiLogger.log(ACTION.DIALOG_EXIT)
        super(SaveMatrixDialogView, self)._onExitClicked()

    def __getIsAcceptDisabled(self):
        if self._selectedItem == SaveMatrixDialogViewModel.BLANK:
            return self._blankCount <= 0
        return False if self._selectedItem == SaveMatrixDialogViewModel.CREDITS else True

    def __fillModel(self, *args, **kwargs):
        detachment = self.__detachmentCache.getDetachment(self._detInvID)
        with self.viewModel.transaction() as vm:
            isOperationChargeable = self._arePerksRemoved or self._areUltimatesRemoved
            isChargeableOperationFreeByDiscount = self.currencyCost == 0
            progressionOption = detachment.progression.getDropSkillDiscountByXP(detachment.experience)
            hasFirstDiscount = detachment.dropSkillDiscounted
            vm.setOperationType(self._operationType)
            if isOperationChargeable and isChargeableOperationFreeByDiscount:
                discountMessage = None
                if progressionOption.discount and not progressionOption.firstDropEnable:
                    msgForFree = backport.text(R.strings.dialogs.detachment.saveMatrix.operation.descriptionForFree(), startLevel=progressionOption.levelStart, endLevel=progressionOption.levelEnd)
                    if hasFirstDiscount:
                        _, discount = getFirstDropSkillsPrice(self._detInvID)
                        msgNextInfo = backport.text(R.strings.dialogs.detachment.saveMatrix.operation.descriptionNextFirstDrop(), discount=discount)
                    else:
                        xp = detachment.progression.getLevelStartingXP(progressionOption.levelEnd + 1)
                        progressionNextOption = detachment.progression.getDropSkillDiscountByXP(xp)
                        msgNextInfo = backport.text(R.strings.dialogs.detachment.saveMatrix.operation.descriptionNextDiscount(), startLevel=progressionNextOption.levelStart, endLevel=progressionNextOption.levelEnd, discount=progressionNextOption.discount)
                    discountMessage = text_styles.concatStylesToMultiLine(msgForFree, msgNextInfo)
                elif progressionOption.discount and progressionOption.firstDropEnable and hasFirstDiscount:
                    _, discount = getFirstDropSkillsPrice(self._detInvID)
                    msgForFistDrop = backport.text(R.strings.dialogs.detachment.saveMatrix.operation.descriptionFirstDrop(), discount=discount)
                    msgNextInfo = backport.text(R.strings.dialogs.detachment.saveMatrix.operation.descriptionNextDiscount(), startLevel=progressionOption.levelStart, endLevel=progressionOption.levelEnd, discount=progressionOption.discount)
                    discountMessage = text_styles.concatStylesToMultiLine(msgForFistDrop, msgNextInfo)
                elif not progressionOption.discount and progressionOption.firstDropEnable and hasFirstDiscount:
                    _, discount = getFirstDropSkillsPrice(self._detInvID)
                    discountMessage = backport.text(R.strings.dialogs.detachment.saveMatrix.operation.descriptionFirstDrop(), discount=discount)
                if discountMessage:
                    vm.setDiscountMessage(discountMessage)
            vm.setIsOperationChargeable(isOperationChargeable)
            vm.setIsChargeableOperationFreeByDiscount(isChargeableOperationFreeByDiscount)
            title = R.strings.dialogs.detachment.saveMatrix.dyn(self._operationType).dyn(self.__titleType).title()
            acceptButtonText = R.strings.detachment.common.save()
            cancelButtonText = R.strings.detachment.common.cancel()
            if self._operationType == SaveMatrixDialogViewModel.EDIT:
                acceptButtonText = R.strings.dialogs.detachment.saveMatrix.applyChanges()
            elif self._operationType == SaveMatrixDialogViewModel.CLEAR_ALL:
                acceptButtonText = R.strings.detachment.common.reset()
            elif self._operationType == SaveMatrixDialogViewModel.EXIT_CONFIRM:
                if isOperationChargeable:
                    title = R.strings.dialogs.detachment.saveMatrix.exitConfirm.edit.dyn(self.__titleType).title()
                    acceptButtonText = R.strings.dialogs.detachment.saveMatrix.applyChanges()
                    cancelButtonText = R.strings.dialogs.detachment.saveMatrix.doNotApplyChanges()
                else:
                    cancelButtonText = R.strings.detachment.common.notSave()
            vm.setTitleBody(title)
            vm.setAcceptButtonText(acceptButtonText)
            vm.setCancelButtonText(cancelButtonText)
            detDescr = detachment.getDescriptor()
            perkDiff = [ (perkID, level - detDescr.build.get(perkID, 0)) for perkID, level in self._perks ]
            totalPerks = detachment.getPerks(bonusPerks=dict(perkDiff))
            perksMatrix = detDescr.getPerksMatrix()
            if self._operationType != SaveMatrixDialogViewModel.CLEAR_ALL:
                perksList = vm.getPerksList()
                perksList.clear()
                for ultimateID in self._ultimates:
                    perkVM = PerkShortModel()
                    perkVM.setId(ultimateID)
                    perkVM.setIcon('perk_{}'.format(ultimateID))
                    perksList.addViewModel(perkVM)

                for perkID, perkLevel in self._perks:
                    perkVM = PerkShortModel()
                    perkVM.setId(perkID)
                    perkVM.setIcon('perk_{}'.format(perkID))
                    perkVM.setPoints(perkLevel)
                    perkVM.setIsOvercapped(totalPerks.get(perkID, 0) > perksMatrix.perks[perkID].max_points)
                    perksList.addViewModel(perkVM)

                vm.setPoints(self._points)
            if isOperationChargeable and not isChargeableOperationFreeByDiscount:
                activeGoodies = self.__goodiesCache.getRecertificationForms(REQ_CRITERIA.DEMOUNT_KIT.IN_ACCOUNT | REQ_CRITERIA.DEMOUNT_KIT.IS_ENABLED)
                recertificationForms = activeGoodies.get(RECERTIFICATION_FORM_ID, None)
                self._blankCount = recertificationForms.count if recertificationForms else 0
                if not self._selectedItem:
                    if self._blankCount > 0:
                        self._selectedItem = SaveMatrixDialogViewModel.BLANK
                    elif self.hasEnoughMoney or self.__checkEnoughGoldForExchangeToCredits():
                        self._selectedItem = SaveMatrixDialogViewModel.CREDITS
                selector = vm.selector
                selectorItems = selector.getItems()
                selectorItems.clear()
                firstItem = SelectorDialogItemModel()
                firstItem.setStorageCount(self._blankCount)
                if self._blankCount <= 0:
                    firstItem.setStatus(SelectorDialogItemModel.DISABLED)
                firstItem.setIsItemEnough(self._blankCount > 0)
                firstItem.setType(SaveMatrixDialogViewModel.BLANK)
                firstItem.setIsSelected(self._selectedItem == SaveMatrixDialogViewModel.BLANK)
                firstItem.setTooltipId(TOOLTIPS_CONSTANTS.RECERTIFICATION_FORM)
                selectorItems.addViewModel(firstItem)
                secondItem = SelectorDialogItemModel()
                secondItem.setIsItemEnough(self.hasEnoughMoney)
                secondItem.setIsDiscount(bool(self.discount))
                secondItem.setItemPrice(self.currencyCost)
                secondItem.setType(SaveMatrixDialogViewModel.CREDITS)
                secondItem.setTooltipId(TOOLTIPS_CONSTANTS.CREDITS_INFO_FULL_SCREEN)
                secondItem.setIsSelected(self._selectedItem == SaveMatrixDialogViewModel.CREDITS)
                selectorItems.addViewModel(secondItem)
                selectorItems.invalidate()
                vm.setIsAcceptDisabled(self.__getIsAcceptDisabled())
        return

    @property
    def __titleType(self):
        perksAmount = 0 if self._perks is None else len(self._perks)
        ultimatesAmount = 0 if self._ultimates is None else len(self._ultimates)
        if self._arePerksRemoved or perksAmount:
            if self._areUltimatesRemoved or ultimatesAmount > 0:
                return 'perksAndUltimates'
            return 'perks'
        else:
            return 'ultimates' if self._areUltimatesRemoved or ultimatesAmount > 0 else ''

    @decorators.process('transferMoney')
    def __exchangeGold(self, gold):
        result = yield GoldToCreditsExchanger(gold, withConfirm=False).request()
        if result and result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
            super(SaveMatrixDialogView, self)._onAcceptClicked()

    def __checkEnoughGoldForExchangeToCredits(self):
        _, price, _ = self.dropSkillPrice
        return False if not mayObtainWithMoneyExchange(price, itemsCache=self.__itemsCache) else True
