# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/HWVehicleAnomaliesComponent.py
from __future__ import absolute_import
from halloween.gui.halloween_gui_constants import BATTLE_CTRL_ID
from helpers import dependency
from script_component.DynamicScriptComponent import DynamicScriptComponent
from skeletons.gui.battle_session import IBattleSessionProvider

class HWVehicleAnomaliesComponent(DynamicScriptComponent):
    guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def _onAvatarReady(self):
        super(HWVehicleAnomaliesComponent, self)._onAvatarReady()
        self._notifyUsedAnomaliesChanged(self.usedAnomalies)

    def onDestroy(self):
        self._notifyUsedAnomaliesChanged([])
        super(HWVehicleAnomaliesComponent, self).onDestroy()

    @property
    def hwBattleGuiCtrl(self):
        return self.guiSessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.HW_BATTLE_GUI_CTRL)

    def set_usedAnomalies(self, _):
        self._notifyUsedAnomaliesChanged(self.usedAnomalies)

    def _notifyUsedAnomaliesChanged(self, usedAnomalies):
        hwBattleGuiCtrl = self.hwBattleGuiCtrl
        if self.entity and self.entity.isPlayerVehicle and hwBattleGuiCtrl:
            hwBattleGuiCtrl.onUpdateUsedAnomalies(usedAnomalies)
