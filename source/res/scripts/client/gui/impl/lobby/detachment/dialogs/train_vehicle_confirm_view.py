# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/dialogs/train_vehicle_confirm_view.py
import logging
import math
import typing
from CurrentVehicle import g_currentVehicle
from async import async, await
from frameworks.wulf import ViewSettings, View
from gui import SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.impl.auxiliary.instructors_helper import fillVehicleModel
from gui.impl.auxiliary.detachment_helper import fillDetachmentShortInfoModel, getSpecializeOption, getSpecializeOptionMoney
from gui.impl.backport.backport_tooltip import createBackportTooltipContent
from gui.impl.dialogs.dialogs import showConvertCurrencyForVehicleView
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.common.vehicle_model import VehicleModel
from gui.impl.gen.view_models.views.lobby.detachment.dialogs.buy_block_model import BuyBlockModel
from gui.impl.gen.view_models.views.lobby.detachment.dialogs.train_slot_model import TrainSlotModel
from gui.impl.gen.view_models.views.lobby.detachment.dialogs.train_vehicle_confirm_view_model import TrainVehicleConfirmViewModel
from gui.impl.lobby.detachment.tooltips.colored_simple_tooltip import ColoredSimpleTooltip
from gui.impl.lobby.detachment.tooltips.detachment_info_tooltip import DetachmentInfoTooltip
from gui.impl.lobby.detachment.tooltips.instructor_tooltip import getInstructorTooltip
from gui.impl.lobby.detachment.tooltips.level_badge_tooltip_view import LevelBadgeTooltipView
from gui.impl.lobby.detachment.tooltips.commander_perk_tooltip import CommanderPerkTooltip
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogView
from gui.impl.pub.dialog_window import DialogButtons
from gui.shared.gui_items import Vehicle
from gui.shared.gui_items.processors.common import GoldToCreditsExchanger
from gui.shared.money import Currency
from gui.shared.utils import decorators
from gui.shop import showBuyGoldForDetachmentSpecizalize
from helpers import dependency
from items.components.detachment_constants import PaidOperationsContants, SpecializationPaymentOption, PROGRESS_MAX
from items.detachment import DetachmentDescr
from skeletons.gui.detachment import IDetachmentCache
from skeletons.gui.shared import IItemsCache
from uilogging.detachment.constants import GROUP, ACTION
from uilogging.detachment.loggers import DetachmentLogger
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.detachment import Detachment
    from gui.impl.gen.view_models.views.lobby.detachment.common.detachment_info_animated_model import DetachmentInfoAnimatedModel
    from frameworks.wulf import ViewEvent
_logger = logging.getLogger(__name__)

class TrainVehicleConfirmView(FullScreenDialogView):
    __itemsCache = dependency.descriptor(IItemsCache)
    __detachmentCache = dependency.descriptor(IDetachmentCache)
    _TRAINING_OPTIONS = (BuyBlockModel.FREE, BuyBlockModel.SCHOOL, BuyBlockModel.ACADEMY)
    _PAYMENT_OPTIONS_WITHOUT_CLASS_CHANGE = {BuyBlockModel.FREE: SpecializationPaymentOption.FREE,
     BuyBlockModel.SCHOOL: SpecializationPaymentOption.SILVER,
     BuyBlockModel.ACADEMY: SpecializationPaymentOption.GOLD,
     BuyBlockModel.TRAINING: SpecializationPaymentOption.FREE}
    _TRAINING_OPTION_TO_PAYMENT_OPTION = {TrainVehicleConfirmViewModel.TRAIN: _PAYMENT_OPTIONS_WITHOUT_CLASS_CHANGE,
     TrainVehicleConfirmViewModel.RETRAIN: _PAYMENT_OPTIONS_WITHOUT_CLASS_CHANGE,
     TrainVehicleConfirmViewModel.CHANGE: {BuyBlockModel.FREE: SpecializationPaymentOption.FREE_CLASS,
                                           BuyBlockModel.SCHOOL: SpecializationPaymentOption.SILVER_CLASS,
                                           BuyBlockModel.ACADEMY: SpecializationPaymentOption.GOLD,
                                           BuyBlockModel.TRAINING: SpecializationPaymentOption.FREE_CLASS}}
    _FORMAT_PERCENTS = 100
    uiLogger = DetachmentLogger(GROUP.TRAIN_VEHICLE_CONFIRM_DIALOG)
    __slots__ = ('__selectedVehicleCD', '__layoutID', '__detachmentInvID', '__vehicleSlotIndex', '__detachment', '__operationType', '__selectedCard', '__tooltipByContentID', '_updateIsReset')

    def __init__(self, detachmentInvID, slotIndex, selectedVehicleCD):
        self.__layoutID = R.views.lobby.detachment.dialogs.TrainVehicleConfirmView()
        self.__detachmentInvID = detachmentInvID
        self.__vehicleSlotIndex = slotIndex
        self.__selectedVehicleCD = selectedVehicleCD
        self.__detachment = None
        self.__operationType = None
        self.__selectedCard = BuyBlockModel.ACADEMY
        self._updateIsReset = True
        settings = ViewSettings(layoutID=self.__layoutID, model=TrainVehicleConfirmViewModel())
        super(TrainVehicleConfirmView, self).__init__(settings)
        rTooltip = R.views.lobby.detachment.tooltips
        self.__tooltipByContentID = {rTooltip.InstructorTooltip(): self.__getInstructorTooltip,
         rTooltip.CommanderPerkTooltip(): self.__getCommanderPerkTooltip,
         rTooltip.ColoredSimpleTooltip(): self.__getColoredSimpleTooltip,
         rTooltip.DetachmentInfoTooltip(): self.__getDetachmentInfoTooltip,
         rTooltip.LevelBadgeTooltip(): self.__getLevelBadgeTooltip,
         R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent(): self.__getBackportTooltip}
        return

    @property
    def viewModel(self):
        return super(TrainVehicleConfirmView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        createTooltip = self.__tooltipByContentID.get(contentID)
        return createTooltip(event) if createTooltip else super(TrainVehicleConfirmView, self).createToolTipContent(event, contentID)

    def _onLoading(self):
        super(TrainVehicleConfirmView, self)._onLoading()
        self.__detachment = self.__detachmentCache.getDetachment(self.__detachmentInvID)
        self.__fillViewModel()

    def _addListeners(self):
        super(TrainVehicleConfirmView, self)._addListeners()
        self.viewModel.onSelectionChanged += self.__onSelectionChanged
        self.viewModel.onNotResetChanged += self.__onNotResetChanged
        g_clientUpdateManager.addMoneyCallback(self._onMoneyUpdate)
        g_clientUpdateManager.addCallbacks({'shop.detachmentPriceGroups': self._onMoneyUpdate})

    def _removeListeners(self):
        self.viewModel.onSelectionChanged -= self.__onSelectionChanged
        self.viewModel.onNotResetChanged -= self.__onNotResetChanged
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(TrainVehicleConfirmView, self)._removeListeners()

    def _finalize(self):
        self.soundManager.playInstantSound(backport.sound(R.sounds.detachment_progress_bar_stop_all()))
        self.uiLogger.reset()
        self.__tooltipByContentID.clear()
        super(TrainVehicleConfirmView, self)._finalize()

    def _onMoneyUpdate(self, *args, **kwargs):
        self._updateIsReset = False
        self.__fillViewModel()
        self._updateIsReset = True

    def _getAdditionalData(self):
        return {'paymentOptionIdx': self._getCurrentPaymentOptionIdx(),
         'isReset': int(self.viewModel.getIsReset() or self._getCurrentPaymentOptionIdx() != SpecializationPaymentOption.GOLD)}

    def _getCurrentPaymentOptionIdx(self):
        selectedTrainingOption = self.viewModel.getSelectedBlock()
        return self.__getPaymentOptionForTrainingOption(selectedTrainingOption)

    @async
    def _onAcceptClicked(self):
        paymentOptionIdx = self._getCurrentPaymentOptionIdx()
        specOption = getSpecializeOption(self.__detachmentInvID, paymentOptionIdx, default=False)
        specCurrency, specPrice = getSpecializeOptionMoney(self.__detachment, specOption, paymentOptionIdx)
        plCurrencyAmount = self.__itemsCache.items.stats.money.get(specCurrency)
        hasEnoughMoney = specPrice <= plCurrencyAmount
        if not hasEnoughMoney:
            if specCurrency == Currency.GOLD:
                self.uiLogger.log(ACTION.BUY_GOLD)
                showBuyGoldForDetachmentSpecizalize(specPrice, self.__selectedVehicleCD)
            elif specCurrency == Currency.CREDITS:
                needCredits = specPrice - plCurrencyAmount
                sdr = yield await(showConvertCurrencyForVehicleView(ctx={'needCredits': needCredits,
                 'vehicleCD': self.__selectedVehicleCD,
                 'title': R.strings.detachment.specializeCurrency.title()}))
                if sdr.busy:
                    return
                self.uiLogger.log(ACTION.CONVERT_GOLD_TO_CREDITS)
                isOk, data = sdr.result
                if isOk == DialogButtons.SUBMIT:
                    self.__exchangeGold(int(data['gold']))
        else:
            self.uiLogger.log(ACTION.DIALOG_CONFIRM)
            newVehInvID = self.__itemsCache.items.getItemByCD(self.__selectedVehicleCD).invID
            if self.__detachment and newVehInvID > 0:
                detachmentVehInvID = self.__detachment.vehInvID
                if self.__getOperationType() == TrainVehicleConfirmViewModel.CHANGE:
                    g_currentVehicle.selectVehicle(newVehInvID)
                elif detachmentVehInvID > 0:
                    assignedVehicleCD = self.__itemsCache.items.getVehicle(detachmentVehInvID).intCD
                    assignedSlotID = next((slotID for slotID, vehTypeCompDescr in enumerate(self.__detachment.vehicleSlots) if vehTypeCompDescr == assignedVehicleCD), None)
                    if assignedSlotID is not None and assignedSlotID == self.__vehicleSlotIndex:
                        g_currentVehicle.selectVehicle(newVehInvID)
            super(TrainVehicleConfirmView, self)._onAcceptClicked()
        return

    def _onExitClicked(self):
        self.uiLogger.log(ACTION.DIALOG_EXIT)
        super(TrainVehicleConfirmView, self)._onExitClicked()

    def _onCancelClicked(self):
        self.uiLogger.log(ACTION.DIALOG_CANCEL)
        super(TrainVehicleConfirmView, self)._onCancelClicked()

    def __getOperationType(self):
        detVehClassType = self.__detachment.classType
        vehicleCDs = self.__detachment.getVehicleCDs()
        prevVehicleCD = None if self.__vehicleSlotIndex >= len(vehicleCDs) else vehicleCDs[self.__vehicleSlotIndex]
        trainVehicleItem = self.__itemsCache.items.getItemByCD(self.__selectedVehicleCD)
        if detVehClassType != trainVehicleItem.type:
            return TrainVehicleConfirmViewModel.CHANGE
        else:
            return TrainVehicleConfirmViewModel.RETRAIN if prevVehicleCD is not None else TrainVehicleConfirmViewModel.TRAIN

    def __getPaymentOptionForTrainingOption(self, trainingOption):
        return SpecializationPaymentOption.GOLD if self.__isTraining() else self._TRAINING_OPTION_TO_PAYMENT_OPTION[self.__operationType][trainingOption]

    def __fillBuyBlockModels(self, models):
        models.clearItems()
        if self.__isTraining():
            model = BuyBlockModel()
            model.setType(BuyBlockModel.TRAINING)
            paymentOption = self.__getPaymentOptionForTrainingOption(BuyBlockModel.TRAINING)
            self.__fillBuyBlockModel(model, paymentOption)
            models.addViewModel(model)
        else:
            for to in self._TRAINING_OPTIONS:
                model = BuyBlockModel()
                model.setType(to)
                paymentOption = self.__getPaymentOptionForTrainingOption(to)
                self.__fillBuyBlockModel(model, paymentOption)
                models.addViewModel(model)

        models.invalidate()

    def __fillBuyBlockModel(self, model, paymentOptionID):
        ecoSpecOption = getSpecializeOption(self.__detachmentInvID, paymentOptionID, default=False)
        xpMult = ecoSpecOption.get(PaidOperationsContants.PARAM_EXP_MULTIPLIER, 0)
        model.setPercentExp(-self._FORMAT_PERCENTS * xpMult)
        fine = self.__detachment.getDescriptor().getSpecializeVehicleSlotFineXP(xpMult)
        model.setNegativePercentExp(-fine)
        currency1, price1 = self.__getPrice(paymentOptionID)
        priceModel = model.priceModel
        priceModel.setValue(int(price1))
        priceModel.setType(currency1)
        playerBalance = self.__itemsCache.items.stats.money.get(currency1)
        priceModel.setIsEnough(price1 <= playerBalance)
        currency0, price0 = self.__getOldPrice(paymentOptionID)
        hasDiscount = currency1 == currency0 and price1 < price0
        priceModel.setHasDiscount(hasDiscount)
        if hasDiscount:
            discountPercent = int(round(-100 * (1.0 - float(price1) / price0)))
            priceModel.setDiscountValue(discountPercent)

    def __getPrice(self, paymentOptionID):
        ecoSpecOption = getSpecializeOption(self.__detachmentInvID, paymentOptionID, default=False)
        currency, price = getSpecializeOptionMoney(self.__detachment, ecoSpecOption, paymentOptionID)
        return (currency, price)

    def __getOldPrice(self, paymentOptionID):
        ecoSpecOption = getSpecializeOption(self.__detachmentInvID, paymentOptionID, default=False)
        defEcoSpecOption = getSpecializeOption(self.__detachmentInvID, paymentOptionID, default=True)
        if defEcoSpecOption is None:
            defEcoSpecOption = ecoSpecOption
        currency, price = getSpecializeOptionMoney(self.__detachment, defEcoSpecOption, paymentOptionID, useLevelDiscount=False)
        return (currency, price)

    def __fillXpLoss(self, mdl, selectedBlockName):
        optionIdx = self.__getPaymentOptionForTrainingOption(selectedBlockName)
        specOption = getSpecializeOption(self.__detachmentInvID, optionIdx, default=False)
        xpLossPerc = specOption.get(PaidOperationsContants.PARAM_EXP_MULTIPLIER, 0)
        detDescr0 = self.__detachment.getDescriptor()
        xpProgress0 = detDescr0.getCurrentLevelXPProgress() * PROGRESS_MAX
        if xpLossPerc <= 0:
            mdl.setProgressValue(xpProgress0)
            mdl.setProgressDeltaFrom(xpProgress0)
            mdl.setGainLevels(0)
        else:
            detDescr1 = DetachmentDescr.createByCompDescr(detDescr0.makeCompactDescr())
            fine = detDescr1.getSpecializeVehicleSlotFineXP(xpLossPerc)
            detDescr1.subXP(fine)
            xpProgress1 = detDescr1.getCurrentLevelXPProgress() * PROGRESS_MAX
            mdl.setProgressValue(xpProgress1)
            mdl.setProgressDeltaFrom(xpProgress0)
            rawLvl0 = detDescr0.rawLevel
            rawLvl1 = detDescr1.rawLevel
            mdl.setGainLevels(rawLvl1 - rawLvl0)

    def __fillViewModel(self):
        with self.viewModel.transaction() as vm:
            self.__operationType = self.__getOperationType()
            vehicleCDs = self.__detachment.getVehicleCDs()
            prevVehicleCD = None if self.__vehicleSlotIndex >= len(vehicleCDs) else vehicleCDs[self.__vehicleSlotIndex]
            vm.setOperationType(self.__operationType)
            vm.setAcceptButtonText(R.strings.detachment.common.train())
            vm.setCancelButtonText(R.strings.detachment.common.cancel())
            if self.__operationType == TrainVehicleConfirmViewModel.CHANGE:
                vm.setAcceptButtonText(R.strings.detachment.common.change())
            elif self.__operationType == TrainVehicleConfirmViewModel.RETRAIN:
                vm.setAcceptButtonText(R.strings.detachment.common.retrain())
            else:
                vm.setAcceptButtonText(R.strings.detachment.common.train())
            fillDetachmentShortInfoModel(vm.detachmentInfo, self.__detachment)
            self.__fillBuyBlockModels(vm.blocks)
            if self.__isTraining():
                self.__setSelectedBlock(BuyBlockModel.TRAINING, vm)
            else:
                self.__setSelectedBlock(self.__selectedCard, vm)
            vehicle = self.__itemsCache.items.getItemByCD(self.__selectedVehicleCD) if self.__selectedVehicleCD else None
            if vehicle:
                vm.setIsTrainToPremium(vehicle.isPremium)
                self.__createVehicle(vehicle, model=vm.vehicle)
            prevVehicle = self.__itemsCache.items.getItemByCD(prevVehicleCD) if prevVehicleCD else None
            if prevVehicle is not None:
                self.__createVehicle(prevVehicle, model=vm.prevVehicle)
            vm.slots.clearItems()
            if self.__operationType == TrainVehicleConfirmViewModel.CHANGE:
                for slotIdx in xrange(self.__detachment.maxVehicleSlots):
                    isLocked = slotIdx >= len(vehicleCDs)
                    vCD = vehicleCDs[slotIdx] if not isLocked else None
                    vehicle = self.__itemsCache.items.getItemByCD(vCD) if vCD else None
                    vm.slots.addViewModel(self.__createVehicle(vehicle, isLocked=isLocked))

        return

    def __createVehicle(self, vehicle, isLocked=False, model=None):
        isShortName = self.__operationType is not TrainVehicleConfirmViewModel.TRAIN
        if model is None:
            model = TrainSlotModel()
        if vehicle is None:
            if isinstance(model, TrainSlotModel):
                model.setIsLocked(isLocked)
            return model
        else:
            fillVehicleModel(model, vehicle, isShortName=isShortName)
            return model

    def __setSelectedBlock(self, selectedItem, vm):
        for block in vm.blocks.getItems():
            if block.getType() == selectedItem:
                vm.setSelectedBlock(selectedItem)
                percentExp = block.getPercentExp()
                vm.setPercentExp(percentExp)
                if self._updateIsReset:
                    vm.setIsReset(percentExp < 0)
                self.__fillXpLoss(vm.detachmentInfo, selectedItem)
                self.__updateAcceptButton(selectedItem, vm)
                break

    def __updateAcceptButton(self, selectedBlock, vm):
        paymentOptionNum = self.__getPaymentOptionForTrainingOption(selectedBlock)
        specOption = getSpecializeOption(self.__detachmentInvID, paymentOptionNum, default=False)
        specCurrency, specPrice = getSpecializeOptionMoney(self.__detachment, specOption, paymentOptionNum)
        disableAccept = False
        if specPrice > 0 and specCurrency == Currency.CREDITS:
            playerMoney = self.__itemsCache.items.stats.money
            playerCredits = playerMoney.get(specCurrency)
            if playerCredits < specPrice:
                playerGold = playerMoney.get(Currency.GOLD)
                exchangeRate = self.__itemsCache.items.shop.exchangeRate
                requiredGold = math.ceil(float(specPrice - playerCredits) / exchangeRate)
                if playerGold < requiredGold:
                    disableAccept = True
        vm.setIsAcceptDisabled(disableAccept)

    def __onSelectionChanged(self, args=None):
        if args is None:
            _logger.error('args=None. Please fix JS')
            return
        else:
            selectedItem = args.get('selectedItem')
            with self.viewModel.transaction() as vm:
                self.__selectedCard = selectedItem
                self.__setSelectedBlock(selectedItem, vm)
            return

    @uiLogger.dLogOnce(ACTION.DROP_SKILL_CHECKBOX)
    def __onNotResetChanged(self):
        with self.viewModel.transaction() as vm:
            vm.setIsReset(not vm.getIsReset())

    def __isTraining(self):
        return self.__detachment.level < self.__detachment.progression.firstPaidSpecializationLevel

    @decorators.process('transferMoney')
    def __exchangeGold(self, gold):
        result = yield GoldToCreditsExchanger(gold, withConfirm=False).request()
        SystemMessages.pushMessages(result)
        if result.success:
            self.uiLogger.log(ACTION.DIALOG_CONFIRM)
            super(TrainVehicleConfirmView, self)._onAcceptClicked()

    def __getInstructorTooltip(self, event):
        return getInstructorTooltip(instructorInvID=event.getArgument('instructorInvID'))

    def __getCommanderPerkTooltip(self, event):
        perkType = event.getArgument('perkType')
        return CommanderPerkTooltip(perkType=perkType)

    def __getColoredSimpleTooltip(self, event):
        note = ''
        if self.__isTraining():
            note = backport.text(R.strings.tooltips.trainVehicle.training.body2(), icon='%(info)', minTier=1, maxTier=self.__detachment.progression.firstPaidSpecializationLevel - 1)
        return ColoredSimpleTooltip(event.getArgument('header', ''), event.getArgument('body', ''), note)

    def __getDetachmentInfoTooltip(self, _):
        return DetachmentInfoTooltip(detachmentInvID=self.__detachmentInvID)

    def __getLevelBadgeTooltip(self, _):
        return LevelBadgeTooltipView(self.__detachmentInvID)

    def __getBackportTooltip(self, event):
        tooltipId = event.getArgument('tooltipId')
        if tooltipId == TOOLTIPS_CONSTANTS.PRICE_DISCOUNT:
            block = event.getArgument('block')
            paymentOption = self.__getPaymentOptionForTrainingOption(block)
            currency, newPrice = self.__getOldPrice(paymentOption)
            _, oldPrice = self.__getPrice(paymentOption)
            balance = self.__itemsCache.items.stats.money.get(currency)
            isEnough = balance >= newPrice
            return createBackportTooltipContent(TOOLTIPS_CONSTANTS.PRICE_DISCOUNT, (oldPrice,
             newPrice,
             currency,
             isEnough,
             isEnough))
        if tooltipId == TOOLTIPS_CONSTANTS.NOT_ENOUGH_MONEY:
            currency = event.getArgument('currency')
            value = int(event.getArgument('value', 0))
            shortage = max(value - self.__itemsCache.items.stats.money.get(currency, 0), 0)
            return createBackportTooltipContent(TOOLTIPS_CONSTANTS.NOT_ENOUGH_MONEY, (shortage, currency))
