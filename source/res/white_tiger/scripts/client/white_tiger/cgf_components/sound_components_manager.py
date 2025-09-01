# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/cgf_components/sound_components_manager.py
import logging
import BigWorld
import CGF
from constants import IS_CLIENT
from helpers import isPlayerAvatar
from cgf_script.bonus_caps_rules import bonusCapsManager
from cgf_script.managers_registrator import onAddedQuery, onRemovedQuery
from white_tiger.cgf_components import wt_sound_helpers
from white_tiger.cgf_components.sound_components import WTConditionalSound2D, WTConditionalSound3D, WTVehicleSound, WTVehicleSoundComponent, WTSoundNotification
from white_tiger_common.wt_constants import ARENA_BONUS_TYPE_CAPS
if IS_CLIENT:
    from Vehicle import Vehicle
    from white_tiger.cgf_components import wt_helpers
else:

    class Vehicle(object):
        pass


_logger = logging.getLogger(__name__)

@bonusCapsManager(ARENA_BONUS_TYPE_CAPS.WHITE_TIGER, CGF.DomainOption.DomainClient)
class SoundComponentManager(CGF.ComponentManager):
    __TIME_BEETWEN_UNIQUE_EVENT = 0.5

    def __init__(self):
        super(SoundComponentManager, self).__init__()
        self.__pendingVehicles = None
        self.__lastUniqueEventTimeExecution = {}
        return

    def deactivate(self):
        for vehicle in CGF.Query(self.spaceID, Vehicle).values():
            if hasattr(vehicle, 'appearance'):
                vehicle.appearance.removeTempGameObject('sound_object')

        self.__pendingVehicles = None
        self.__lastUniqueEventTimeExecution = {}
        if isPlayerAvatar():
            playerAvatar = BigWorld.player()
            playerAvatar.onVehicleEnterWorld -= self.__onVehicleEnterWorld
        return

    @onAddedQuery(Vehicle)
    def onVehicleAdded(self, vehicle):
        vehicleSoundComponent = vehicle.appearance.findComponentByType(WTVehicleSoundComponent)
        if not vehicleSoundComponent:
            vehicle.appearance.addTempGameObject(WTVehicleSoundComponent(vehicle), 'sound_object')

    @onAddedQuery(WTSoundNotification, CGF.GameObject)
    def onEnterSoundNotification(self, sound, go):
        if sound.onlyForPlayerVehicle:
            vehicle = wt_sound_helpers.getVehicle(go, self.spaceID)
            if vehicle and not vehicle.isPlayerVehicle:
                return
        self.__playNotification(sound.onEnterNotification, sound.conditions, sound.isUnique)

    @onRemovedQuery(WTSoundNotification, CGF.GameObject)
    def onExitSoundNotification(self, sound, go):
        self.__playNotification(sound.onExitNotification, sound.conditions)

    @onAddedQuery(WTConditionalSound2D)
    def onEnterSound2D(self, sound):
        self.__play2d(sound.onEnterSound, sound.conditions)

    @onRemovedQuery(WTConditionalSound2D)
    def onExitSound2D(self, sound):
        self.__play2d(sound.onExitSound, sound.conditions)

    @onAddedQuery(WTConditionalSound3D, CGF.GameObject)
    def onEnterSound3D(self, sound, go):
        self.__play3d(sound.onEnterSound, go, sound.conditions)

    @onRemovedQuery(WTConditionalSound3D, CGF.GameObject)
    def onExitSound3D(self, sound, go):
        self.__play3d(sound.onExitSound, go, sound.conditions)

    @onAddedQuery(WTVehicleSound, CGF.GameObject)
    def onEnterVehicleSound(self, sound, go):
        vehicle = wt_sound_helpers.getVehicle(go, self.spaceID)
        if not vehicle:
            _logger.warning("onEnterVehicleSound: Couldn't find vehicle! go=%s, spaceID=%s", go, self.spaceID)
            return
        else:
            sound.vehicle = vehicle
            soundObjIndex = sound.getSoundObjectIndex()
            enterSound = sound.onEnterSound
            if sound.useNPCEvents and not vehicle.isPlayerVehicle:
                if sound.onEnterSoundNPC:
                    enterSound = sound.onEnterSoundNPC
            soundConditions = sound.conditions
            if not hasattr(vehicle, 'appearance') or vehicle.appearance is None:
                if soundObjIndex is not None:
                    self.__registerPendingVehicle(vehicle.id, self.__playVehiclePart, (enterSound, soundObjIndex, soundConditions))
                else:
                    self.__registerPendingVehicle(vehicle.id, self.__playVehicleRoot, (enterSound, soundConditions))
            elif soundObjIndex is not None:
                self.__playVehiclePart(vehicle, enterSound, soundObjIndex, soundConditions)
            else:
                self.__playVehicleRoot(vehicle, enterSound, soundConditions)
            return

    @onRemovedQuery(WTVehicleSound)
    def onExitVehicleSound(self, sound):
        vehicle = sound.vehicle
        if not vehicle:
            _logger.warning("onExitVehicleSound:Couldn't find vehicle! spaceID=%s", self.spaceID)
            return
        else:
            soundObjIndex = sound.getSoundObjectIndex()
            if not hasattr(vehicle, 'appearance') or vehicle.appearance is None:
                _logger.info("Couldn't find appearance in the vehicle id=%d", vehicle.id)
            else:
                onExitSound = sound.onExitSound
                if not vehicle.isPlayerVehicle and sound.onExitSoundNPC:
                    onExitSound = sound.onExitSoundNPC
                if soundObjIndex is not None:
                    self.__playVehiclePart(vehicle, onExitSound, soundObjIndex, sound.conditions)
                else:
                    self.__playVehicleRoot(vehicle, onExitSound, sound.conditions)
            return

    def __checkConditions(self, conditionsStr, vehicle=None):
        if not conditionsStr:
            return True
        conditions = conditionsStr.split()
        for condition in conditions:
            if not self.__checkAvatarCondition(condition, vehicle):
                return False

        return True

    def __checkAvatarCondition(self, condition, vehicle=None):
        if condition == 'boss_player':
            return wt_helpers.isBoss()
        if condition == 'hunter_player':
            return not wt_helpers.isBoss()
        if condition == 'only_for_player':
            return wt_helpers.isPlayerVehicle(vehicle)
        if 'dist_to' in condition:
            return self.__checkDistToCondition(condition)
        if 'eos_one_in' in condition:
            return wt_helpers.isMinibossInArena() and wt_helpers.isBoss()
        if 'eos_one_out' in condition:
            if not wt_helpers.isMinibossInArena():
                return True
            return False
        if 'engine_audition_is_present' in condition:
            return wt_helpers.isEngineAuditionPresent(vehicle)
        _logger.warning('Found unknown condition: %s', condition)
        return False

    def __checkDistToCondition(self, condition):
        useLower = True
        if '<' in condition:
            condition = condition.split('<')
        elif '>' in condition:
            useLower = False
            condition = condition.split('>')
        else:
            _logger.warning('Found unknown condition: %s', condition)
            return False
        if self.__getListElement(condition, 0) and condition[0] == 'dist_to_boss':
            bossVehicle = wt_helpers.getBossVehicle()
            playerVehicle = wt_helpers.getPlayerVehicle()
            if bossVehicle and playerVehicle:
                dist = playerVehicle.position.distTo(bossVehicle.position)
                conditionDist = self.__getListElement(condition, 1)
                if useLower:
                    return self.__getInt(conditionDist) and dist < int(conditionDist)
                return self.__getInt(conditionDist) and dist > int(conditionDist)
        return False

    def __getListElement(self, list, index):
        try:
            return list[index]
        except IndexError:
            return None

        return None

    def __getInt(self, val):
        try:
            return int(val)
        except (ValueError, TypeError):
            return None

        return None

    def __playNotification(self, notificationName, conditionsStr, isUnique=False):
        isPlay = True
        if isUnique:
            lastTime = self.__lastUniqueEventTimeExecution.get(notificationName, 0)
            self.__lastUniqueEventTimeExecution[notificationName] = BigWorld.time()
            isPlay = BigWorld.time() - lastTime > self.__TIME_BEETWEN_UNIQUE_EVENT
        if notificationName and self.__checkConditions(conditionsStr) and isPlay:
            wt_sound_helpers.playNotification(notificationName)

    def __play2d(self, soundName, conditionsStr):
        if soundName and self.__checkConditions(conditionsStr):
            wt_sound_helpers.play2d(soundName)

    def __play3d(self, soundName, go, conditionsStr):
        if soundName and self.__checkConditions(conditionsStr):
            wt_sound_helpers.play3d(soundName, go, self.spaceID)

    def __playVehicleRoot(self, vehicle, soundName, conditionsStr):
        if soundName and vehicle and self.__checkConditions(conditionsStr, vehicle):
            wt_sound_helpers.playVehicleSound(soundName, vehicle)

    def __playVehiclePart(self, vehicle, soundName, partIndex, conditionsStr):
        if soundName and vehicle and partIndex and self.__checkConditions(conditionsStr, vehicle):
            wt_sound_helpers.playVehiclePart(soundName, vehicle, partIndex)

    def __registerPendingVehicle(self, vehicleID, cb, arguments):
        if self.__pendingVehicles is None:
            self.__pendingVehicles = {}
            BigWorld.player().onVehicleEnterWorld += self.__onVehicleEnterWorld
        self.__pendingVehicles[vehicleID] = (cb, arguments)
        return

    def __onVehicleEnterWorld(self, vehicle):
        vehicleId = vehicle.id
        if vehicleId in self.__pendingVehicles:
            cb, args = self.__pendingVehicles[vehicleId]
            _logger.info('Play postponed sound for vehicleID=%s, callback=%cb, arguments=%s', vehicleId, cb, args)
            cb(vehicle, *args)
            del self.__pendingVehicles[vehicleId]
