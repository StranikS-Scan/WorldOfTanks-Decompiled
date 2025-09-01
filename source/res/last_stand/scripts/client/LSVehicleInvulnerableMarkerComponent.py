# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/LSVehicleInvulnerableMarkerComponent.py
import BigWorld
from helpers import dependency
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID
from script_component.DynamicScriptComponent import DynamicScriptComponent
from skeletons.gui.battle_session import IBattleSessionProvider
from last_stand.gui.ls_gui_constants import BATTLE_CTRL_ID

class LSVehicleInvulnerableMarkerComponent(DynamicScriptComponent):
    guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def _onAvatarReady(self):
        super(LSVehicleInvulnerableMarkerComponent, self)._onAvatarReady()
        lsBattleGuiCtrl = self.guiSessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.LS_BATTLE_GUI_CTRL)
        if lsBattleGuiCtrl:
            lsBattleGuiCtrl.setVehicleInvulnerable(self.entity.id, True)

    def onDestroy(self):
        lsBattleGuiCtrl = self.guiSessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.LS_BATTLE_GUI_CTRL)
        if lsBattleGuiCtrl:
            lsBattleGuiCtrl.setVehicleInvulnerable(self.entity.id, False)
        super(LSVehicleInvulnerableMarkerComponent, self).onDestroy()

    def showNoHitMarker(self, attackerID):
        avatar = BigWorld.player()
        if not avatar:
            return
        attachedVehicle = avatar.getVehicleAttached()
        if not attachedVehicle or attachedVehicle.id != attackerID:
            return
        feedback = self.guiSessionProvider.shared.feedback
        feedback.setVehicleState(self.entity.id, FEEDBACK_EVENT_ID.LS_NO_HIT)
