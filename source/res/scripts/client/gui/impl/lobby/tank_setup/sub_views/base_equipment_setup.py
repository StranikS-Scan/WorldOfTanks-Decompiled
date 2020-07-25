# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/sub_views/base_equipment_setup.py
from functools import partial
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.base_setup_model import BaseSetupModel
from gui.impl.lobby.tank_setup.sub_views.deal_base_setup import DealBaseSetupSubView
from gui.shared.event_dispatcher import showModuleInfo

class BaseEquipmentSetupSubView(DealBaseSetupSubView):
    __slots__ = ()

    def _addListeners(self):
        super(BaseEquipmentSetupSubView, self)._addListeners()
        self._addSlotAction(BaseSetupModel.SELECT_SLOT_ACTION, self._onSelectItem)
        self._addSlotAction(BaseSetupModel.REVERT_SLOT_ACTION, self._onRevertItem)
        self._addSlotAction(BaseSetupModel.RETURN_TO_STORAGE_ACTION, self._onRevertItem)
        self._addSlotAction(BaseSetupModel.SWAP_SLOTS_ACTION, partial(self._onSwapSlots, BaseSetupModel.SWAP_SLOTS_ACTION))
        self._addSlotAction(BaseSetupModel.DRAG_AND_DROP_SLOT_ACTION, partial(self._onSwapSlots, BaseSetupModel.DRAG_AND_DROP_SLOT_ACTION))
        self._addSlotAction(BaseSetupModel.SHOW_INFO_SLOT_ACTION, self._onShowItemInfo)

    def _onSelectItem(self, args):
        itemCD = args.get('intCD')
        currentSlotID = int(args.get('currentSlotId', self._curSlotID))
        self._selectItem(currentSlotID, itemCD)

    def _selectItem(self, slotID, item):
        self._interactor.changeSlotItem(slotID, item)
        self.update()

    def _onSwapSlots(self, actionType, args):
        slotID = int(args.get('installedSlotId'))
        currentSlotID = int(args.get('currentSlotId', self._curSlotID))
        self._swapSlots(currentSlotID, slotID, actionType)
        self.update()

    def _swapSlots(self, currentSlotID, slotID, actionType):
        self._interactor.swapSlots(currentSlotID, slotID, actionType)
        self.update()

    def _onRevertItem(self, args):
        slotID = int(args.get('installedSlotId'))
        self.revertItem(slotID)

    def _onShowItemInfo(self, args):
        itemIntCD = int(args.get('intCD'))
        showModuleInfo(itemIntCD, self._interactor.getItem().descriptor)
