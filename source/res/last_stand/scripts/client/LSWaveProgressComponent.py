# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/LSWaveProgressComponent.py
import typing
from helpers import dependency
from last_stand.gui.ls_gui_constants import BATTLE_CTRL_ID
from script_component.DynamicScriptComponent import DynamicScriptComponent
from skeletons.gui.battle_session import IBattleSessionProvider

class LSWaveProgressComponent(DynamicScriptComponent):
    guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    @property
    def lsBattleGuiCtrl(self):
        return self.guiSessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.LS_BATTLE_GUI_CTRL)

    def _onAvatarReady(self):
        super(LSWaveProgressComponent, self)._onAvatarReady()
        if self.lsBattleGuiCtrl is not None:
            self.lsBattleGuiCtrl.updateEnemiesInfo(dict(self.enemiesInfo))
            self.lsBattleGuiCtrl.updateHealthBreakpoints(self.healthBreakpoints)
            self.lsBattleGuiCtrl.updateEnemiesStatus(self.enemiesStatus)
        return

    def set_enemiesInfo(self, prev):
        if self.lsBattleGuiCtrl is not None:
            self.lsBattleGuiCtrl.updateEnemiesInfo(dict(self.enemiesInfo))
        return

    def set_healthBreakpoints(self, prev):
        if self.lsBattleGuiCtrl is not None:
            self.lsBattleGuiCtrl.updateHealthBreakpoints(self.healthBreakpoints)
        return

    def set_enemiesStatus(self, prev):
        if self.lsBattleGuiCtrl is not None:
            self.lsBattleGuiCtrl.updateEnemiesStatus(self.enemiesStatus)
        return
