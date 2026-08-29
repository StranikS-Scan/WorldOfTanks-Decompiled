# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/WTVehicleHunterComponent.py
import typing
import BigWorld
import CGF
import SoundGroups
from script_component.DynamicScriptComponent import DynamicScriptComponent
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE, FEEDBACK_EVENT_ID
from vehicle_systems.model_assembler import loadAppearancePrefab
if typing.TYPE_CHECKING:
    pass

class WTVehicleHunterComponent(DynamicScriptComponent):
    _WT23_PLASMA_BOOST_UI_SOUND_ID = 'ev_wt_ui_plasma_boost'

    def __init__(self):
        super(WTVehicleHunterComponent, self).__init__()
        self.__plasmaLevelGO = None
        return

    def onDestroy(self):
        self.__removePrefab()
        super(WTVehicleHunterComponent, self).onDestroy()

    def set_plasmaCounter(self, prev):
        if self.plasmaCounter != prev:
            self.__createCapturePrefab(prev)
            self.__updatePlasmaPrefab()
            if self.entity.id == BigWorld.player().playerVehicleID:
                self.__notifiUIAndPlaySounds(prev)

    def set_plasmaDamage(self, pref):
        if self.plasmaDamage != pref:
            ctrl = self.entity.guiSessionProvider.shared.feedback
            if ctrl:
                ctrl.onVehicleFeedbackReceived(FEEDBACK_EVENT_ID.VEHICLE_DISCRETE_DAMAGE_RECEIVED, self.plasmaDamage.victimId, (self.entity.id, self.plasmaDamage.additionalPlasmaDamage))

    def onAppearanceReady(self):
        self.__updatePlasmaPrefab()
        if self.entity.id == BigWorld.player().playerVehicleID:
            self.__notifiUIAndPlaySounds(self.plasmaCounter)

    def _onAvatarReady(self):
        self.__updatePlasmaPrefab()
        if self.entity.id == BigWorld.player().playerVehicleID:
            self.__notifiUIAndPlaySounds(self.plasmaCounter)

    def __notifiUIAndPlaySounds(self, prev):
        ctrl = self.entity.guiSessionProvider.shared.vehicleState
        if ctrl:
            ctrl.notifyStateChanged(VEHICLE_VIEW_STATE.PLASMA, (self.plasmaCounter, self.damageMultiplier, self.plasmaToSaveOnDeath))
            hasPlasmaChanged = self.entity.health > 0 and prev is not None and prev != self.plasmaCounter
            if not hasPlasmaChanged:
                return
            if prev < self.plasmaCounter:
                SoundGroups.g_instance.playSound2D(self._WT23_PLASMA_BOOST_UI_SOUND_ID)
        return

    def __createCapturePrefab(self, prevPlasma):
        if self.plasmaCounter <= prevPlasma:
            return
        appearance = self.entity.appearance
        if appearance and appearance.isConstructed:
            loadAppearancePrefab(self.capturePrefab, appearance)

    def __updatePlasmaPrefab(self):
        self.__removePrefab()
        appearance = self.entity.appearance
        if appearance and appearance.isConstructed and self.plasmaPrefabPerLevel:
            loadAppearancePrefab(self.plasmaPrefabPerLevel[self.plasmaCounter], appearance, self.__plasmaPrefabLoaded)

    def __plasmaPrefabLoaded(self, go):
        if self.entity.health <= 0:
            CGF.removeGameObject(go)
            return
        self.__plasmaLevelGO = go

    def __removePrefab(self):
        if self.__plasmaLevelGO and self.__plasmaLevelGO.isValid():
            CGF.removeGameObject(self.__plasmaLevelGO)
            self.__plasmaLevelGO = None
        return
