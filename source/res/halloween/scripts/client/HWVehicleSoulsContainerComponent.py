# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/HWVehicleSoulsContainerComponent.py
from __future__ import absolute_import
import BigWorld
import Event
from helpers import dependency
from script_component.DynamicScriptComponent import DynamicScriptComponent
from skeletons.gui.battle_session import IBattleSessionProvider

class HWVehicleSoulsContainerComponent(DynamicScriptComponent):
    guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(HWVehicleSoulsContainerComponent, self).__init__()
        self.onChangeSoulsCount = Event.Event()

    def _onAvatarReady(self):
        super(HWVehicleSoulsContainerComponent, self)._onAvatarReady()
        from halloween.gui.halloween_gui_constants import BATTLE_CTRL_ID
        hwBattleGuiCtrl = self.guiSessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.HW_BATTLE_GUI_CTRL)
        if hwBattleGuiCtrl and self.entity.id == BigWorld.player().playerVehicleID:
            hwBattleGuiCtrl.onSoulsContainerReady(self)

    def set_capacity(self, _):
        self.onChangeSoulsCount(self.souls, 0)

    def set_lastCollected(self, _):
        _, reason = self.lastCollected
        self.onChangeSoulsCount(self.souls, reason)

    def onDestroy(self):
        self.onChangeSoulsCount.clear()
        super(HWVehicleSoulsContainerComponent, self).onDestroy()
