# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/LSVehicleBoosterFactorsComponent.py
from __future__ import absolute_import
from helpers import dependency
from last_stand.gui.ls_gui_constants import BATTLE_CTRL_ID
from last_stand_common.ls_utils.boosters import applyBoosterFactors, getFactorsDiff
from script_component.DynamicScriptComponent import DynamicScriptComponent
from skeletons.gui.battle_session import IBattleSessionProvider

class LSVehicleBoosterFactorsComponent(DynamicScriptComponent):
    guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    @property
    def lsBattleGuiCtrl(self):
        return self.guiSessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.LS_BATTLE_GUI_CTRL)

    def set_factors(self, prev):
        diff = getFactorsDiff(self.factors or {}, prev or {})
        if diff:
            self.lsBattleGuiCtrl.onFactorsReady(self.entity.id, diff)

    def applyFactors(self, value, factorName):
        return applyBoosterFactors(value, factorName, self.factors or {})

    def _onAvatarReady(self):
        super(LSVehicleBoosterFactorsComponent, self)._onAvatarReady()
        if self.factors:
            self.lsBattleGuiCtrl.onFactorsReady(self.entity.id, set(self.factors.keys()))
