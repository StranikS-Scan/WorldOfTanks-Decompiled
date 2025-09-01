# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/lobby/tank_setup/sub_view.py
from functools import partial
from gui.impl.lobby.tank_setup.sub_views.consumable_setup import ConsumableSetupSubView
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.base_setup_model import BaseSetupModel
from last_stand.gui.impl.lobby.tank_setup.configuration import LastStandTabsController
from last_stand.gui.shared.event_dispatcher import showModuleInfo

class LastStandSetupSubView(ConsumableSetupSubView):
    __slots__ = ()

    def _createTabsController(self):
        return LastStandTabsController()

    def _addListeners(self):
        super(LastStandSetupSubView, self)._addListeners()
        self._addSlotAction(BaseSetupModel.SELECT_SLOT_ACTION, self._onSelectItem)
        self._addSlotAction(BaseSetupModel.REVERT_SLOT_ACTION, self._onRevertItem)
        self._addSlotAction(BaseSetupModel.RETURN_TO_STORAGE_ACTION, self._onRevertItem)
        self._addSlotAction(BaseSetupModel.SWAP_SLOTS_ACTION, partial(self._onSwapSlots, BaseSetupModel.SWAP_SLOTS_ACTION))
        self._addSlotAction(BaseSetupModel.DRAG_AND_DROP_SLOT_ACTION, partial(self._onSwapSlots, BaseSetupModel.DRAG_AND_DROP_SLOT_ACTION))
        self._addSlotAction(BaseSetupModel.SHOW_INFO_SLOT_ACTION, self._onShowItemInfo)

    def _onShowItemInfo(self, args):
        itemIntCD = int(args.get('intCD'))
        showModuleInfo(itemIntCD, self._interactor.getItem().descriptor)
