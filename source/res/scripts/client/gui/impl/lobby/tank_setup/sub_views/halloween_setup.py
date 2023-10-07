# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/sub_views/halloween_setup.py
from gui.impl.lobby.tank_setup.sub_views.base_equipment_setup import BaseEquipmentSetupSubView
from gui.impl.lobby.tank_setup.configurations.halloween import HalloweenTabsController, HalloweenDealPanel

class HalloweenSetupSubView(BaseEquipmentSetupSubView):
    __slots__ = ()

    def revertItem(self, slotID):
        self._interactor.revertSlot(slotID)
        self.update()

    def _createTabsController(self):
        return HalloweenTabsController()

    def _getDealPanel(self):
        return HalloweenDealPanel
