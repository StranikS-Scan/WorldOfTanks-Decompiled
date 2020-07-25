# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/vehicle_compare/base_sub_view.py
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.base_setup_model import BaseSetupModel
from gui.impl.lobby.tank_setup.sub_views.base_setup import BaseSetupSubView

class CompareBaseSetupSubView(BaseSetupSubView):
    __slots__ = ()

    def revertItem(self, slotID):
        self._interactor.changeSlotItem(slotID, None)
        return

    def _addListeners(self):
        super(CompareBaseSetupSubView, self)._addListeners()
        self._addSlotAction(BaseSetupModel.SELECT_SLOT_ACTION, self._onSelectItem)
        self._addSlotAction(BaseSetupModel.REVERT_SLOT_ACTION, self._onRevertItem)
        self._addSlotAction(BaseSetupModel.RETURN_TO_STORAGE_ACTION, self._onRevertItem)
        self._addSlotAction(BaseSetupModel.SWAP_SLOTS_ACTION, self._onSwapSlots)

    def _onSelectItem(self, args):
        itemCD = int(args.get('intCD'))
        currentSlotID = int(args.get('currentSlotId', self._curSlotID))
        self._selectItem(currentSlotID, itemCD)

    def _selectItem(self, slotID, item):
        self._interactor.changeSlotItem(slotID, item)

    def _onSwapSlots(self, args):
        slotID = int(args.get('installedSlotId'))
        currentSlotID = int(args.get('currentSlotId', self._curSlotID))
        self._swapSlots(currentSlotID, slotID)

    def _swapSlots(self, currentSlotID, slotID):
        self._interactor.swapSlots(currentSlotID, slotID)

    def _onRevertItem(self, args):
        slotID = int(args.get('installedSlotId'))
        self.revertItem(slotID)
