# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/LSVehicleSoulsContainerComponent.py
import BigWorld
import Event
from helpers import dependency
from script_component.DynamicScriptComponent import DynamicScriptComponent
from skeletons.gui.battle_session import IBattleSessionProvider

class LSVehicleSoulsContainerComponent(DynamicScriptComponent):
    guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(LSVehicleSoulsContainerComponent, self).__init__()
        self.onChangeSoulsCount = Event.Event()

    def _onAvatarReady(self):
        super(LSVehicleSoulsContainerComponent, self)._onAvatarReady()
        from last_stand.gui.ls_gui_constants import BATTLE_CTRL_ID
        lsBattleGuiCtrl = self.guiSessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.LS_BATTLE_GUI_CTRL)
        if lsBattleGuiCtrl and self.entity.id == BigWorld.player().playerVehicleID:
            lsBattleGuiCtrl.onSoulsContainerReady(self)

    def set_lastCollected(self, _):
        _, reason = self.lastCollected
        self.onChangeSoulsCount(self.souls, reason)

    def onDestroy(self):
        self.onChangeSoulsCount.clear()
        super(LSVehicleSoulsContainerComponent, self).onDestroy()
