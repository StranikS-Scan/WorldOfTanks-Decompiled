# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/VehicleRespawnComponent.py
import BigWorld
import Event
from constants import RespawnState, VEHICLE_SETTING, IS_VS_EDITOR
from helpers import dependency
from script_component.DynamicScriptComponent import DynamicScriptComponent
from skeletons.gui.battle_session import IBattleSessionProvider
from vehicle_systems.stricted_loading import makeCallbackWeak
if not IS_VS_EDITOR:
    from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
    from shared_utils import nextTick
    from helpers.EffectsList import RespawnDestroyEffect

class VehicleRespawnComponent(DynamicScriptComponent):
    onSetSpawnTime = Event.Event()
    guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def onDestroy(self):
        super(VehicleRespawnComponent, self).onDestroy()
        self.entity.onAppearanceReady -= self._onVehicleAppeared

    def chooseSpawnGroup(self, groupName):
        self.cell.chooseSpawnGroup(groupName)

    def set_spawnTime(self, prev):
        self.onSetSpawnTime(self.entity.id, self.spawnTime)

    def set_respawnState(self, prev):
        if self.respawnState == RespawnState.RESPAWNING:
            self._explodeVehicleBeforeRespawn()
        elif self.respawnState == RespawnState.VEHICLE_ALIVE and prev == RespawnState.RESPAWNING:
            self.waitForRespawnReadiness()

    def waitForRespawnReadiness(self):
        avatar = BigWorld.player()
        if avatar is None:
            return
        else:
            vehInfo = avatar.arena.vehicles[self.entity.id]
            isVehicleAlive = vehInfo['isAlive'] and not self.entity.isDestroyed and self.entity.isStarted and self.entity.isAlive()
            isVehicleReady = avatar.playerVehicleID != self.entity.id or avatar.vehicle and avatar.vehicle.id == avatar.playerVehicleID
            if not isVehicleAlive or not isVehicleReady:
                nextTick(makeCallbackWeak(self.waitForRespawnReadiness))()
                return
            self._respawnVehicle()
            return

    def _respawnVehicle(self):
        self.entity.onAppearanceReady += self._onVehicleAppeared
        avatar = BigWorld.player()
        avatar.startResurrecting(self.entity.id)
        avatar.redrawVehicleOnRespawn(self.entity.id, self.entity.publicInfo.compDescr, self.entity.publicInfo.outfit)

    def _onVehicleAppeared(self):
        if self.respawnState != RespawnState.VEHICLE_ALIVE:
            return
        else:
            avatar = BigWorld.player()
            if avatar.playerVehicleID != self.entity.id:
                return
            ownVehicle = getattr(self.entity, 'ownVehicle', None)
            if ownVehicle is None:
                return
            self.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.HEALTH, self.entity.health, self.entity.id)
            ownVehicle.initialUpdate(force=True)
            avatar.updateVehicleSetting(self.entity.id, VEHICLE_SETTING.CURRENT_SHELLS, self.entity.ownVehicle.currentShell)
            avatar.updateVehicleSetting(self.entity.id, VEHICLE_SETTING.NEXT_SHELLS, self.entity.ownVehicle.nextShell)
            self.entity.onAppearanceReady -= self._onVehicleAppeared
            return

    def _explodeVehicleBeforeRespawn(self):
        avatar = BigWorld.player()
        if avatar is None or avatar.playerVehicleID != self.entity.id:
            return
        else:
            RespawnDestroyEffect.play(self.entity.id)
            return
