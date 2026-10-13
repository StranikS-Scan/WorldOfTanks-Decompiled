# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/HWBuffDrainMarkerComponent.py
from __future__ import absolute_import
from helpers import dependency
from script_component.DynamicScriptComponent import DynamicScriptComponent
from halloween.gui.halloween_gui_constants import BATTLE_CTRL_ID
from skeletons.gui.battle_session import IBattleSessionProvider

class HWBuffDrainMarkerComponent(DynamicScriptComponent):
    _guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def onDestroy(self):
        self.__updateMarkerIcon(False)
        super(HWBuffDrainMarkerComponent, self).onDestroy()

    def set_isActive(self, prev):
        self.__updateMarkerIcon(self.isActive)

    def _onAvatarReady(self):
        super(HWBuffDrainMarkerComponent, self)._onAvatarReady()
        self.__updateMarkerIcon(self.isActive)

    def __updateMarkerIcon(self, visible):
        if not self.entity.isPlayerVehicle:
            hwBattleGuiCtrl = self._guiSessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.HW_BATTLE_GUI_CTRL)
            if hwBattleGuiCtrl:
                hwBattleGuiCtrl.onBossAuraVictimMarkerIcon(self.entity, visible)
