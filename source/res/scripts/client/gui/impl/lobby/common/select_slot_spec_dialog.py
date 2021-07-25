# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/common/select_slot_spec_dialog.py
import typing
from BWUtil import AsyncReturn
from async import async, await
from frameworks.wulf import ViewSettings
from gui.impl.auxiliary.vehicle_helper import fillVehicleInfo
from gui.impl.common.base_sub_model_view import BaseSubModelView
from gui.impl.dialogs.dialogs import showSingleDialogWithResultData
from gui.impl.gen.view_models.views.lobby.common.buy_and_exchange_bottom_content_type import BuyAndExchangeBottomContentType
from gui.impl.gen.view_models.views.lobby.common.select_slot_spec_dialog_content_model import SelectSlotSpecDialogContentModel
from gui.impl.gen.view_models.views.lobby.common.select_slot_spec_dialog_model import SelectSlotSpecDialogModel
from gui.impl.gen.view_models.views.lobby.common.select_slot_spec_dialog_slot_model import SelectSlotSpecDialogSlotModel
from gui.impl.gen.view_models.views.lobby.common.select_slot_spec_dialog_spec_model import SelectSlotSpecDialogSpecModel
from gui.impl.lobby.dialogs.auxiliary.buy_and_exchange_state_machine import BuyAndExchangeStateEnum
from gui.impl.lobby.dialogs.buy_and_exchange import BuyAndExchange
from gui.impl.wrappers.user_compound_price_model import PriceModelBuilder
from gui.impl.gen import R
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.items_cache import CACHE_SYNC_REASON
from gui.shared.money import Money
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from gui.Scaleform.Waiting import Waiting
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.Vehicle import Vehicle
    from frameworks.wulf import Window
TContentModel = SelectSlotSpecDialogContentModel

class SelectSlotSpecDialog(BuyAndExchange[SelectSlotSpecDialogModel]):
    __slots__ = ('_vehicle', '_mainContent', '_price', '_slotIdx', '_freeChange')
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, vehicle, slotIdx=None):
        settings = ViewSettings(R.views.lobby.common.SelectSlotSpecDialog(), model=SelectSlotSpecDialogModel())
        self._price = self.__itemsCache.items.shop.customRoleSlotChangeCost(vehicle.level)
        self._vehicle = vehicle
        self._slotIdx = slotIdx
        if self._slotIdx is None:
            self._slotIdx = self._vehicle.optDevices.dynSlotTypeIdx
        self._freeChange = not self._vehicle.optDevices.getSlot(self._slotIdx).isDynamic
        startState = None
        if self._freeChange:
            startState = BuyAndExchangeStateEnum.BUY_NOT_REQUIRED
        super(SelectSlotSpecDialog, self).__init__(settings, self._price, startState)
        self._mainContent = None
        return

    def _onLoading(self, *args, **kwargs):
        model = self.getViewModel()
        model.hold()
        super(SelectSlotSpecDialog, self)._onLoading(*args, **kwargs)
        self._mainContent = SelectSlotSpecDialogMainContent(self._vehicle, model.mainContent, self._slotIdx)
        self._mainContent.onLoading()
        PriceModelBuilder.fillPriceModel(model.changePrice, self._price)
        model.commit()

    def _onLoaded(self, *args, **kwargs):
        super(SelectSlotSpecDialog, self)._onLoaded(*args, **kwargs)
        Waiting.hide('loadModalWindow')

    def _getAdditionalData(self):
        return self._mainContent and self._mainContent.getSelectedSlot()

    def _initialize(self, *args, **kwargs):
        super(SelectSlotSpecDialog, self)._initialize()
        if self._mainContent:
            self._mainContent.initialize()

    def _finalize(self):
        super(SelectSlotSpecDialog, self)._finalize()
        if self._mainContent:
            self._mainContent.finalize()

    def _onInventoryResync(self, reason, diff):
        changedVehicle = diff.get(GUI_ITEM_TYPE.VEHICLE, {})
        if self._vehicle.intCD in changedVehicle or reason == CACHE_SYNC_REASON.SHOP_RESYNC:
            vehicle = self.__itemsCache.items.getItemByCD(self._vehicle.intCD)
            if not vehicle.postProgressionAvailability() or not vehicle.isRoleSlotActive:
                self._onCancel()
            price = self.__itemsCache.items.shop.customRoleSlotChangeCost(self._vehicle.level)
            if not self._freeChange and price != self._price:
                self._price = price
                self._updatePrice(self._price)
                PriceModelBuilder.clearPriceModel(self.getViewModel().changePrice)
                PriceModelBuilder.fillPriceModel(self.getViewModel().changePrice, self._price)
        super(SelectSlotSpecDialog, self)._onInventoryResync(reason, diff)

    def _buyNotRequiredAccept(self):
        self._onAccept()

    def _stateToContent(self):
        return {BuyAndExchangeStateEnum.BUY_CONTENT: BuyAndExchangeBottomContentType.DEAL_PANEL,
         BuyAndExchangeStateEnum.BUY_NOT_REQUIRED: SelectSlotSpecDialogModel.BUY_NOT_REQUIRED_PANEL,
         BuyAndExchangeStateEnum.NEED_EXCHANGE: BuyAndExchangeBottomContentType.EXCHANGE_PANEL,
         BuyAndExchangeStateEnum.CAN_NOT_BUY: BuyAndExchangeBottomContentType.EXCHANGE_PANEL,
         BuyAndExchangeStateEnum.EXCHANGE_CONTENT: BuyAndExchangeBottomContentType.EXCHANGE_PANEL,
         BuyAndExchangeStateEnum.EXCHANGE_IN_PROCESS: BuyAndExchangeBottomContentType.EXCHANGE_PANEL,
         BuyAndExchangeStateEnum.GOLD_NOT_ENOUGH: BuyAndExchangeBottomContentType.EXCHANGE_PANEL,
         BuyAndExchangeStateEnum.EXCHANGE_NOT_REQUIRED: BuyAndExchangeBottomContentType.DEAL_PANEL}

    def _onAcceptClicked(self):
        if self._getCurrentDialogState() == BuyAndExchangeStateEnum.EXCHANGE_NOT_REQUIRED:
            self._buyAccept()
        else:
            super(SelectSlotSpecDialog, self)._onAcceptClicked()

    def _skipNeedExchangeState(self):
        return True


class SelectSlotSpecDialogMainContent(BaseSubModelView[TContentModel]):
    __slots__ = ('_vehicle', '_slotIdx', '_startIdx')

    def __init__(self, vehicle, viewModel, slotIdx=None):
        super(SelectSlotSpecDialogMainContent, self).__init__(viewModel)
        self._vehicle = vehicle
        self._slotIdx = slotIdx
        self._startIdx = -1

    def onLoading(self, *args, **kwargs):
        super(SelectSlotSpecDialogMainContent, self).onLoading(*args, **kwargs)
        optDevices = self._vehicle.optDevices
        model = self._viewModel
        self.setAvailableSpecs(model, optDevices)
        self.setSlots(model, optDevices)
        fillVehicleInfo(model.vehicleInfo, self._vehicle)

    def setSlots(self, model, optDevices):
        model.setTargetSlotIdx(self._slotIdx)
        for idx in range(len(optDevices.slots)):
            slotModel = SelectSlotSpecDialogSlotModel()
            slotData = optDevices.getSlot(idx)
            self._fillSpecsModel(slotModel, slotData.item.categories)
            model.getSlots().addViewModel(slotModel)

        self.__setSelectedSpecIdx(model, optDevices.getSlot(self._slotIdx))

    def setAvailableSpecs(self, model, optDevices):
        for slot in optDevices.dynSlotTypeOptions:
            slotModel = SelectSlotSpecDialogSpecModel()
            slotModel.setId(slot.slotID)
            self._fillSpecsModel(slotModel, slot.categories)
            model.getAvailableSpecs().addViewModel(slotModel)

    def getSelectedSlot(self):
        if self._viewModel is not None:
            idx = self._viewModel.getSelectedSpecIdx()
            if idx >= 0:
                return self._viewModel.getAvailableSpecs().getValue(idx).getId()
        return 0

    @staticmethod
    def _fillSpecsModel(model, categories):
        if categories:
            model.setSpecialization(next(iter(categories)))

    def __setSelectedSpecIdx(self, model, slotData):
        for index, slotModel in enumerate(model.getAvailableSpecs()):
            if slotModel.getId() == slotData.item.slotID:
                self._startIdx = index
                break

        model.setSelectedSpecIdx(self._startIdx)


@async
def showDialog(vehicle, parent=None):
    result = yield await(showSingleDialogWithResultData(layoutID=R.views.lobby.common.SelectSlotSpecDialog(), parent=parent, wrappedViewClass=SelectSlotSpecDialog, vehicle=vehicle))
    raise AsyncReturn(result)
