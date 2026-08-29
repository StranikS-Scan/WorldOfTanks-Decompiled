# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/WTVehicleImpulseModA.py
import BigWorld
import CGF
from cgf_components import sound_helpers
from script_component.DynamicScriptComponent import DynamicScriptComponent
from vehicle_systems.model_assembler import loadAppearancePrefab

class WTVehicleImpulseModA(DynamicScriptComponent):
    _PREFAB_SRC = 'content/WtPrefabs/Impulse.prefab'
    _PLAYER_BOSS_STUN_IMPULSE = 'wt_w_vo_ability_emp'

    def __init__(self):
        super(WTVehicleImpulseModA, self).__init__()
        self.__goImpulse = None
        return

    def onDestroy(self):
        self.__unloadEffect()
        super(WTVehicleImpulseModA, self).onDestroy()

    def set_isImpulseActive(self, prev):
        if self.isImpulseActive:
            self.__loadEffect()
        else:
            self.__unloadEffect()

    def set_isSomeoneStuned(self, prev):
        if self.isSomeoneStuned and self.entity.id == BigWorld.player().playerVehicleID:
            sound_helpers.playNotification(self._PLAYER_BOSS_STUN_IMPULSE)

    def __loadEffect(self):
        appearance = self.entity.appearance
        if appearance is None or not appearance.isConstructed:
            return
        else:
            loadAppearancePrefab(self._PREFAB_SRC, appearance, self.__onEffectLoaded)
            return

    def __onEffectLoaded(self, go):
        if not self.isImpulseActive:
            self.__removeGO(go)
            return
        self.__goImpulse = go

    def __unloadEffect(self):
        if self.__goImpulse is not None:
            self.__removeGO(self.__goImpulse)
        self.__goImpulse = None
        return

    def __removeGO(self, go):
        if go and go.isValid():
            CGF.removeGameObject(go)
