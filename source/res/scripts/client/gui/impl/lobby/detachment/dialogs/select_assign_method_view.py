# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/dialogs/select_assign_method_view.py
from functools import partial
from CurrentVehicle import g_currentVehicle
from frameworks.wulf import ViewSettings
from gui import SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.impl.auxiliary.detachment_helper import fillVehicleSlotPriceModel, getSlotPriceData
from gui.impl.dialogs.dialogs import showTrainVehicleConfirmView, buyVehicleSlot
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.buy_dormitory_dialog_model import BuyDormitoryDialogModel
from gui.impl.gen.view_models.views.lobby.detachment.dialogs.select_assign_method_view_model import SelectAssignMethodViewModel
from gui.impl.gen.view_models.views.lobby.detachment.dialogs.vehicle_slot_model import VehicleSlotModel
from gui.impl.gen.view_models.views.lobby.detachment.dialogs.vehicle_slot_states import VehicleSlotStates
from gui.impl.lobby.detachment.tooltips.colored_simple_tooltip import ColoredSimpleTooltip
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogView
from gui.shared.gui_items.Vehicle import Vehicle, getIconResourceName, getNationLessName
from gui.shared.gui_items.detachment import Detachment
from gui.shared.gui_items.processors.detachment import DetachmentUnlockSpecializeVehicleSlotAndAssign, DetachmentSpecializeVehicleSlotAndAssign
from gui.shared.money import Currency
from gui.shared.utils import decorators
from gui.shop import showBuyGoldForDetachmentVehicleSlot
from gui.sounds.filters import switchHangarOverlaySoundFilter
from helpers import dependency
from skeletons.gui.detachment import IDetachmentCache
from skeletons.gui.shared import IItemsCache
from uilogging.detachment.loggers import g_detachmentFlowLogger, DetachmentLogger
from uilogging.detachment.constants import GROUP, ACTION

class SelectAssignMethodView(FullScreenDialogView):
    __slots__ = ('_detachment', '_detachmentInvID', '_vehInvID', '_vehIntCD', '_selectedSlotIndex')
    __itemsCache = dependency.descriptor(IItemsCache)
    __detachmentCache = dependency.descriptor(IDetachmentCache)
    uiLogger = DetachmentLogger(GROUP.SELECT_ASSIGN_METHOD_DIALOG)

    def __init__(self, **kwargs):
        settings = ViewSettings(R.views.lobby.detachment.dialogs.SelectAssignMethodView())
        settings.model = SelectAssignMethodViewModel()
        self._detachmentInvID = kwargs['detachmentInvID']
        vehicle = kwargs['vehicle']
        self._vehInvID = vehicle.invID
        self._vehIntCD = vehicle.intCD
        self._detachment = self.__detachmentCache.getDetachment(self._detachmentInvID)
        self._selectedSlotIndex = -1
        super(SelectAssignMethodView, self).__init__(settings)

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            if tooltipId == VehicleSlotModel.SLOT_TOOLTIP:
                index = event.getArgument('index')
                priceData = getSlotPriceData(index, self._detachmentInvID, self.__itemsCache)
                if priceData['hasDiscount']:
                    specialArgs = (priceData['actualPrice'],
                     priceData['defaultPrice'],
                     priceData['currency'],
                     priceData['isEnoughActual'],
                     priceData['isEnoughDefault'])
                    return self.__getBackportTooltipWindow(TOOLTIPS_CONSTANTS.PRICE_DISCOUNT, specialArgs)
                if not priceData['isEnoughActual']:
                    specialArgs = (priceData['shortage'], priceData['currency'])
                    return self.__getBackportTooltipWindow(TOOLTIPS_CONSTANTS.NOT_ENOUGH_MONEY, specialArgs)
        return super(SelectAssignMethodView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        return ColoredSimpleTooltip(event.getArgument('header', ''), event.getArgument('body', '')) if contentID == R.views.lobby.detachment.tooltips.ColoredSimpleTooltip() else super(SelectAssignMethodView, self).createToolTipContent(event, contentID)

    @property
    def viewModel(self):
        return self.getViewModel()

    def _addListeners(self):
        super(SelectAssignMethodView, self)._addListeners()
        self.viewModel.onSlotClick += self._onSlotClick
        g_clientUpdateManager.addMoneyCallback(self._onMoneyUpdate)
        g_clientUpdateManager.addCallbacks({'shop.detachmentPriceGroups': self._onMoneyUpdate})

    def _removeListeners(self):
        self.viewModel.onSlotClick -= self._onSlotClick
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(SelectAssignMethodView, self)._removeListeners()

    def _setBaseParams(self, model):
        super(SelectAssignMethodView, self)._setBaseParams(model)
        self.__fillViewModel()

    def _initialize(self):
        super(SelectAssignMethodView, self)._initialize()
        switchHangarOverlaySoundFilter(on=True)

    def _finalize(self):
        super(SelectAssignMethodView, self)._finalize()
        switchHangarOverlaySoundFilter(on=False)
        self._detachment = None
        return

    def _onMoneyUpdate(self, *args, **kwargs):
        self.__fillViewModel()
        with self.viewModel.transaction() as model:
            model.setSelectedCardIndex(self._selectedSlotIndex)
            model.getVehicleSlotList()[self._selectedSlotIndex].setIsSelected(True)

    def _onSlotClick(self, event):
        if self._selectedSlotIndex >= 0:
            self.viewModel.getVehicleSlotList()[self._selectedSlotIndex].setIsSelected(False)
        self._selectedSlotIndex = int(event['index'])
        with self.viewModel.transaction() as model:
            model.setSelectedCardIndex(self._selectedSlotIndex)
            model.getVehicleSlotList()[self._selectedSlotIndex].setIsSelected(True)

    def _onAcceptClicked(self):
        slotModel = self.viewModel.getVehicleSlotList()[self._selectedSlotIndex]
        state = slotModel.getState()
        priceModel = slotModel.priceModel
        isEnough = priceModel.getIsEnough()
        price = priceModel.getValue()
        currencyType = priceModel.getType()
        if price > 0 and not isEnough and currencyType == Currency.GOLD:
            self.uiLogger.log(ACTION.BUY_GOLD)
            showBuyGoldForDetachmentVehicleSlot(price)
            return
        if state == VehicleSlotStates.FOR_PURCHASE:
            self.__showBuySlotDialogPrepareTrainDialog(partial(self.__unlockTrainAndAssignCallback, self._selectedSlotIndex))
        else:
            self.__showTrainToVehicleDialog(partial(self.__trainAndAssignCallback, self._selectedSlotIndex))

    def _onCancelClicked(self):
        self.uiLogger.log(ACTION.DIALOG_CANCEL)
        super(SelectAssignMethodView, self)._onCancelClicked()

    def _onExitClicked(self):
        self.uiLogger.log(ACTION.DIALOG_EXIT)
        super(SelectAssignMethodView, self)._onExitClicked()

    @g_detachmentFlowLogger.dFlow(uiLogger.group, GROUP.TRAIN_VEHICLE_CONFIRM_DIALOG)
    def __showTrainToVehicleDialog(self, callback):
        future = showTrainVehicleConfirmView(self.getParentWindow(), detachmentInvID=self._detachmentInvID, slotIndex=self._selectedSlotIndex, selectedVehicleCD=self._vehIntCD)
        future.then(callback)

    @g_detachmentFlowLogger.dFlow(uiLogger.group, GROUP.BUY_VEHICLE_SLOT_DIALOG)
    def __showBuySlotDialogPrepareTrainDialog(self, callback):

        def _processResponse(promise):
            busy, isAccepted = promise.get()
            if busy:
                return
            if isAccepted:
                self.__showTrainToVehicleDialog(callback)

        future = buyVehicleSlot(self.getParentWindow(), ctx={'slotID': self._selectedSlotIndex,
         'detInvID': self._detachmentInvID})
        future.then(_processResponse)

    @decorators.process('updating')
    def __trainAndAssignCallback(self, slotIndex, promise):
        busy, result = promise.get()
        if busy:
            return
        isAccepted, data = result
        if isAccepted:
            processor = DetachmentSpecializeVehicleSlotAndAssign(self._detachmentInvID, slotIndex, self._vehIntCD, data['paymentOptionIdx'], data['isReset'], self._vehInvID)
            result = yield processor.request()
            SystemMessages.pushMessages(result)
            self._onAccept()

    @decorators.process('updating')
    def __unlockTrainAndAssignCallback(self, slotIndex, promise):
        busy, result = promise.get()
        if busy:
            return
        isAccepted, data = result
        if isAccepted:
            processor = DetachmentUnlockSpecializeVehicleSlotAndAssign(self._detachmentInvID, slotIndex, self._vehIntCD, data['paymentOptionIdx'], data['isReset'], self._vehInvID)
            result = yield processor.request()
            SystemMessages.pushMessages(result)
            self._onAccept()

    def __fillViewModel(self):
        with self.viewModel.transaction() as viewModel:
            viewModel.setAcceptButtonText(R.strings.dialogs.selectAssignMethod.button.proceed())
            viewModel.setCancelButtonText(R.strings.dialogs.selectAssignMethod.button.cancel())
            viewModel.setTitleBody(R.strings.dialogs.selectAssignMethod.title())
            viewModel.setCurrentVehicleName(g_currentVehicle.item.shortUserName)
            self.__fillSlots(viewModel)

    def __fillSlots(self, viewModel):
        slotsList = viewModel.getVehicleSlotList()
        slotsList.clear()
        vehicleCDs = self._detachment.getVehicleCDs()
        assignedSlots = len(vehicleCDs)
        emptySlots = self._detachment.maxVehicleSlots - assignedSlots
        for vehicleCD in vehicleCDs:
            slotModel = VehicleSlotModel()
            slotModel.setNation(self._detachment.nationName)
            slotModel.setType(self._detachment.classTypeUnderscore)
            if vehicleCD is not None:
                vehicle = self.__itemsCache.items.getItemByCD(vehicleCD)
                slotModel.setId(vehicle.intCD)
                slotModel.setIcon(getIconResourceName(getNationLessName(vehicle.name)))
                slotModel.setName(vehicle.shortUserName)
                slotModel.setLevel(vehicle.level)
                slotModel.setIsElite(vehicle.isElite)
                slotModel.setState(VehicleSlotStates.ASSIGNED)
            else:
                slotModel.setState(VehicleSlotStates.AVAILABLE)
            slotsList.addViewModel(slotModel)

        for index in xrange(emptySlots):
            slotModel = VehicleSlotModel()
            slotModel.setNation(self._detachment.nationName)
            slotModel.setType(self._detachment.classTypeUnderscore)
            if index == 0:
                slotModel.setState(VehicleSlotStates.FOR_PURCHASE)
                fillVehicleSlotPriceModel(slotModel.priceModel, assignedSlots, self._detachmentInvID, self.__itemsCache)
            else:
                slotModel.setState(VehicleSlotStates.DISABLE)
            slotsList.addViewModel(slotModel)

        slotsList.invalidate()
        return

    def __getBackportTooltipWindow(self, tooltipId, specialArgs):
        tooltipData = backport.createTooltipData(isSpecial=True, specialAlias=tooltipId, specialArgs=specialArgs)
        window = backport.BackportTooltipWindow(tooltipData, self.getParentWindow())
        window.load()
        return window
