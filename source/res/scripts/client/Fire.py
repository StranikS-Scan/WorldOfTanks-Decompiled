# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/Fire.py
import random
import weakref
import BigWorld
from constants import FIRE_NOTIFICATION_CODES
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
import Health
import TriggersManager
from TriggersManager import TRIGGER_TYPE
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE

class Fire(BigWorld.DynamicScriptComponent):
    __guiSessionProvider = dependency.descriptor(IBattleSessionProvider)
    __FIRE_SOUNDS = {'fireStarted': 'fire_started',
     'fireStopped': 'fire_stopped'}
    __EXTENDED_NOTIFICATION_WINDOW = 1

    def __init__(self):
        super(Fire, self).__init__()
        self.__effectListPlayerRef = None
        vehicle = self.entity
        self.__isPlayerVehicle = vehicle.isPlayerVehicle
        if not self.__tryShowFlameEffect():
            vehicle.onAppearanceReady += self.__tryShowFlameEffect
        return

    def __tryShowFlameEffect(self):
        vehicle = self.entity
        appearance = vehicle.appearance
        if appearance is None or not appearance.isConstructed:
            return False
        else:
            if vehicle.health > 0:
                fire = appearance.findComponentByType(Health.FireComponent)
                if fire is None:
                    appearance.createComponent(Health.FireComponent)
                isUnderwater = appearance.isUnderwater
                if not isUnderwater and self.__effectListPlayerRef is None:
                    self.__playEffect()
            return True

    def set_fireInfo(self, _=None):
        self.triggerFireUIandSound()

    def triggerFireUIandSound(self):
        fireInfo = self.fireInfo
        if fireInfo is None:
            return
        else:
            vehicle = self.entity
            avatar = BigWorld.player()
            isCurrentOrObservedVeh = self.__isCurrentOrObservedVeh(avatar, vehicle)
            if avatar.userSeesWorld() and isCurrentOrObservedVeh and BigWorld.serverTime() - fireInfo['startTime'] < self.__EXTENDED_NOTIFICATION_WINDOW:
                soundCheck = lambda veh=vehicle, player=avatar: player.vehicle == veh and veh.isOnFire()
                avatar.playSoundIfNotMuted(self.__FIRE_SOUNDS['fireStarted'], checkFn=soundCheck)
                deviceExtraIndex = fireInfo['deviceExtraIndex']
                extra = vehicle.typeDescriptor.extras[deviceExtraIndex] if deviceExtraIndex != 0 else None
                self.__guiSessionProvider.shared.messages.showVehicleDamageInfo(avatar, FIRE_NOTIFICATION_CODES[fireInfo['notificationIndex']], vehicle.id, fireInfo['attackerID'], extra, fireInfo['equipmentID'])
                TriggersManager.g_manager.activateTrigger(TRIGGER_TYPE.PLAYER_VEHICLE_IN_FIRE)
            if isCurrentOrObservedVeh:
                self.__guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.FIRE, True)
            rtsCommander = self.__guiSessionProvider.dynamic.rtsCommander
            if rtsCommander and avatar.isCommander():
                rtsCommander.invalidateControlledVehicleState(vehicle.id, VEHICLE_VIEW_STATE.FIRE, True)
            return

    def onDestroy(self):
        self._cleanup()

    def _cleanup(self):
        vehicle = self.entity
        vehicle.appearance.removeComponentByType(Health.FireComponent)
        vehicle.onAppearanceReady -= self.__tryShowFlameEffect
        if vehicle.health > 0:
            self.__fadeEffects()
        else:
            self.__stopEffects()
        avatar = BigWorld.player()
        fireInfo = self.fireInfo
        if fireInfo is not None and self.__isCurrentOrObservedVeh(avatar, vehicle):
            if vehicle.health > 0:
                soundCheck = lambda veh=vehicle, player=avatar: player.vehicle == veh and not veh.isOnFire()
                avatar.playSoundIfNotMuted(self.__FIRE_SOUNDS['fireStopped'], checkFn=soundCheck)
                deviceExtraIndex = fireInfo['deviceExtraIndex']
                extra = vehicle.typeDescriptor.extras[deviceExtraIndex] if deviceExtraIndex != 0 else None
                self.__guiSessionProvider.shared.messages.showVehicleDamageInfo(avatar, 'FIRE_STOPPED', vehicle.id, fireInfo['attackerID'], extra, fireInfo['equipmentID'])
            TriggersManager.g_manager.deactivateTrigger(TRIGGER_TYPE.PLAYER_VEHICLE_IN_FIRE)
            self.__guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.FIRE, False)
        rtsCommander = self.__guiSessionProvider.dynamic.rtsCommander
        if rtsCommander and avatar.isCommander():
            rtsCommander.invalidateControlledVehicleState(vehicle.id, VEHICLE_VIEW_STATE.FIRE, False)
        return

    def __getEffectsListPlayer(self):
        return self.__effectListPlayerRef() if self.__effectListPlayerRef is not None else None

    def __playEffect(self):
        vehicle = self.entity
        stages, effects, _ = random.choice(vehicle.typeDescriptor.type.effects['flaming'])
        data = {'entity_id': vehicle.id}
        waitForKeyOff = True
        effectListPlayer = vehicle.appearance.boundEffects.addNew(None, effects, stages, waitForKeyOff, **data)
        self.__effectListPlayerRef = weakref.ref(effectListPlayer)
        return

    def __stopEffects(self):
        effectsListPlayer = self.__getEffectsListPlayer()
        if effectsListPlayer is not None:
            effectsListPlayer.stop(forceCallback=True)
            self.__effectListPlayerRef = None
        return

    def __fadeEffects(self):
        effectsListPlayer = self.__getEffectsListPlayer()
        if effectsListPlayer is not None:
            effectsListPlayer.keyOff()
            self.__effectListPlayerRef = None
        return

    def __isCurrentOrObservedVeh(self, avatar, vehicle):
        observedVehID = self.__guiSessionProvider.shared.vehicleState.getControllingVehicleID()
        return vehicle.id == avatar.playerVehicleID or vehicle.id == observedVehID

    def onUnderWaterSwitch(self, isVehicleUnderwater):
        if isVehicleUnderwater:
            self.__stopEffects()
        else:
            self.__playEffect()

    def onCameraChanged(self, isPlayerVehicle):
        if self.__isPlayerVehicle == isPlayerVehicle:
            return
        self.__isPlayerVehicle = isPlayerVehicle
        vehicle = self.entity
        appearance = vehicle.appearance
        if appearance.isUnderwater:
            return
        self.__stopEffects()
        self.__playEffect()
