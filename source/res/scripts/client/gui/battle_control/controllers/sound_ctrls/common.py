# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/sound_ctrls/common.py
import typing
import BattleReplay
import BigWorld
import SoundGroups
import TriggersManager
from constants import VEHICLE_HIT_FLAGS as VHF
from Event import EventsSubscriber
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.controllers.interfaces import IBattleController
from helpers import dependency, isPlayerAvatar
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.sounds import IShotsResultSoundController
from shared_utils import nextTick

class SoundPlayersController(object):

    def __init__(self):
        self._soundPlayers = set()

    def init(self):
        for player in self._soundPlayers:
            player.init()

    def destroy(self):
        for player in self._soundPlayers:
            player.destroy()

        self._soundPlayers = None
        return


class SoundPlayersBattleController(IBattleController):

    def __init__(self):
        self.__soundPlayers = self._initializeSoundPlayers()

    def startControl(self, *args):
        self.__startPlayers()

    def stopControl(self):
        self.__destroyPlayers()

    def getControllerID(self):
        return BATTLE_CTRL_ID.SOUND_PLAYERS_CTRL

    def _initializeSoundPlayers(self):
        raise NotImplementedError

    def __startPlayers(self):
        for player in self.__soundPlayers:
            player.init()

    def __destroyPlayers(self):
        for player in self.__soundPlayers:
            player.destroy()

        self.__soundPlayers = None
        return


class SoundPlayer(object):

    def init(self):
        nextTick(self._subscribe)()

    def destroy(self):
        self._unsubscribe()

    def _subscribe(self):
        raise NotImplementedError

    def _unsubscribe(self):
        raise NotImplementedError

    @staticmethod
    def _playSound2D(event, checkAlive=False):
        if BattleReplay.g_replayCtrl.isTimeWarpInProgress:
            return
        else:
            if checkAlive:
                vehicle = BigWorld.player().getVehicleAttached()
                if vehicle is not None and not vehicle.isAlive():
                    return
            SoundGroups.g_instance.playSound2D(event)
            return


class VehicleStateSoundPlayer(SoundPlayer):
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def _subscribe(self):
        ctrl = self._sessionProvider.shared.vehicleState
        ctrl.onVehicleStateUpdated += self._onVehicleStateUpdated
        BigWorld.player().onSwitchingViewPoint += self._onSwitchViewPoint

    def _unsubscribe(self):
        ctrl = self._sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleStateUpdated -= self._onVehicleStateUpdated
        if isPlayerAvatar():
            BigWorld.player().onSwitchingViewPoint -= self._onSwitchViewPoint
        return

    def _onVehicleStateUpdated(self, state, value):
        pass

    def _onSwitchViewPoint(self):
        pass


class BaseEfficiencySoundPlayer(SoundPlayer):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def _subscribe(self):
        ctrl = self.__sessionProvider.shared.personalEfficiencyCtrl
        ctrl.onPersonalEfficiencyReceived += self._onEfficiencyReceived

    def _unsubscribe(self):
        ctrl = self.__sessionProvider.shared.personalEfficiencyCtrl
        if ctrl is not None:
            ctrl.onPersonalEfficiencyReceived -= self._onEfficiencyReceived
        return

    def _onEfficiencyReceived(self, events):
        pass


class EquipmentComponentSoundPlayer(object):
    __slots__ = ('__eventsSubscriber',)
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        self.__eventsSubscriber = None
        return

    def init(self):
        self.__eventsSubscriber = EventsSubscriber()
        self.__eventsSubscriber.subscribeToContextEvent(self.__sessionProvider.shared.vehicleState.onEquipmentComponentUpdated, self._onEquipmentComponentUpdated, self._getEquipmentName())
        self.__eventsSubscriber.subscribeToEvent(self.__sessionProvider.shared.vehicleState.onVehicleControlling, self.__onVehicleControlling)

    def destroy(self):
        self.__eventsSubscriber.unsubscribeFromAllEvents()
        self.__eventsSubscriber = None
        return

    def _onEquipmentComponentUpdated(self, equipmentName, vehicleID, equipmentInfo):
        raise NotImplementedError

    def _getEquipmentName(self):
        raise NotImplementedError

    def _stopSounds(self):
        raise NotImplementedError

    def _getComponentName(self):
        raise NotImplementedError

    def __onVehicleControlling(self, vehicle):
        self._stopSounds()
        component = vehicle.dynamicComponents.get(self._getComponentName())
        if component is not None:
            self._onEquipmentComponentUpdated(component.EQUIPMENT_NAME, vehicle.id, component.getInfo())
        return


class ShotsResultSoundController(IShotsResultSoundController):
    ENEMY_AND_GUN_DAMAGED_BY_PROJECTILE = 'enemy_hp_damaged_by_projectile_and_gun_damaged_by_player'
    ENEMY_AND_CHASSIS_DAMAGED_BY_PROJECTILE = 'enemy_hp_damaged_by_projectile_and_chassis_damaged_by_player'
    ENEMY_DAMAGED_BY_PROJECTILE = 'enemy_hp_damaged_by_projectile_by_player'
    ENEMY_DAMAGED_BY_NOT_PIERCING = None
    ENEMY_DAMAGED_BY_DIRECT_EXPLOSION = 'enemy_hp_damaged_by_explosion_at_direct_hit_by_player'
    ENEMY_DAMAGED_BY_NEAR_EXPLOSION = 'enemy_hp_damaged_by_near_explosion_by_player'
    ENEMY_NOT_DAMAGED_ATTEMPT_AND_GUN_DAMAGED = 'enemy_no_hp_damage_at_attempt_and_gun_damaged_by_player'
    ENEMY_NOT_DAMAGED_ATTEMPT_AND_CHASSIS_DAMAGED = 'enemy_no_hp_damage_at_attempt_and_chassis_damaged_by_player'
    ENEMY_NOT_DAMAGED_ATTEMPT = 'enemy_no_hp_damage_at_attempt_by_player'
    ENEMY_NOT_DAMAGED_NO_ATTEMPT_AND_GUN_DAMAGED = 'enemy_no_hp_damage_at_no_attempt_and_gun_damaged_by_player'
    ENEMY_NOT_DAMAGED_NO_ATTEMPT_AND_CHASSIS_DAMAGED = 'enemy_no_hp_damage_at_no_attempt_and_chassis_damaged_by_player'
    ENEMY_NOT_DAMAGED_NO_ATTEMPT = 'enemy_no_hp_damage_at_no_attempt_by_player'
    ENEMY_NOT_DAMAGED_BY_NEAR_EXPLOSION = 'enemy_no_hp_damage_by_near_explosion_by_player'
    ENEMY_NOT_DAMAGED_AND_NOT_PIERCED = 'enemy_no_piercing_by_player'
    ENEMY_RICOCHET = 'enemy_ricochet_by_player'
    _DEFAULT_EVENT_PREFIX = ''
    _FREQUENT_EVENT_PREFIX = 'frequent_'
    _SHOT_RESULT_SOUND_PRIORITIES = {ENEMY_AND_GUN_DAMAGED_BY_PROJECTILE: 13,
     ENEMY_AND_CHASSIS_DAMAGED_BY_PROJECTILE: 12,
     ENEMY_DAMAGED_BY_PROJECTILE: 11,
     ENEMY_DAMAGED_BY_NOT_PIERCING: 10,
     ENEMY_DAMAGED_BY_DIRECT_EXPLOSION: 9,
     ENEMY_DAMAGED_BY_NEAR_EXPLOSION: 8,
     ENEMY_NOT_DAMAGED_ATTEMPT_AND_GUN_DAMAGED: 7,
     ENEMY_NOT_DAMAGED_NO_ATTEMPT_AND_GUN_DAMAGED: 6,
     ENEMY_NOT_DAMAGED_ATTEMPT_AND_CHASSIS_DAMAGED: 5,
     ENEMY_NOT_DAMAGED_NO_ATTEMPT_AND_CHASSIS_DAMAGED: 4,
     ENEMY_NOT_DAMAGED_AND_NOT_PIERCED: 3,
     ENEMY_NOT_DAMAGED_ATTEMPT: 3,
     ENEMY_NOT_DAMAGED_NO_ATTEMPT: 2,
     ENEMY_NOT_DAMAGED_BY_NEAR_EXPLOSION: 1,
     ENEMY_RICOCHET: 0}
    _ARMOR_SCREEN_FLAGS = VHF.ARMOR_WITH_ZERO_DF_NOT_PIERCED_BY_PROJECTILE | VHF.DEVICE_NOT_PIERCED_BY_PROJECTILE
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        self.__eventPrefix = self._DEFAULT_EVENT_PREFIX

    def startControl(self, *_):
        vStateCtrl = self.__sessionProvider.shared.vehicleState
        if vStateCtrl is not None:
            vStateCtrl.onVehicleControlling += self.__invalidateCurrentVehicle
            vehicle = vStateCtrl.getControllingVehicle()
            self.__invalidateCurrentVehicle(vehicle)
        return

    def stopControl(self):
        vStateCtrl = self.__sessionProvider.shared.vehicleState
        if vStateCtrl is not None:
            vStateCtrl.onVehicleControlling -= self.__invalidateCurrentVehicle
        return

    def getControllerID(self):
        return BATTLE_CTRL_ID.SHOTS_RESULT_SOUND

    def getBestSoundEventName(self, bestSound):
        return self.__eventPrefix + bestSound[0]

    def getBestShotResultSound(self, currBest, newSoundName, otherData):
        newSoundPriority = self._SHOT_RESULT_SOUND_PRIORITIES[newSoundName]
        if currBest is None:
            return (newSoundName, otherData, newSoundPriority)
        else:
            return (newSoundName, otherData, newSoundPriority) if newSoundPriority > currBest[2] else currBest

    def getVehicleHitResultSound(self, enemyVehID, hitFlags, enemiesHitCount):
        sound = None
        if hitFlags & VHF.ATTACK_IS_EXTERNAL_EXPLOSION:
            if hitFlags & VHF.MATERIAL_WITH_POSITIVE_DF_PIERCED_BY_EXPLOSION:
                sound = self.ENEMY_DAMAGED_BY_NEAR_EXPLOSION
            elif hitFlags & VHF.IS_ANY_PIERCING_MASK:
                sound = self.ENEMY_NOT_DAMAGED_BY_NEAR_EXPLOSION
        elif hitFlags & VHF.MATERIAL_WITH_POSITIVE_DF_PIERCED_BY_PROJECTILE:
            if hitFlags & (VHF.GUN_DAMAGED_BY_PROJECTILE | VHF.GUN_DAMAGED_BY_EXPLOSION):
                sound = self.ENEMY_AND_GUN_DAMAGED_BY_PROJECTILE
            elif hitFlags & (VHF.CHASSIS_DAMAGED_BY_PROJECTILE | VHF.CHASSIS_DAMAGED_BY_EXPLOSION):
                sound = self.ENEMY_AND_CHASSIS_DAMAGED_BY_PROJECTILE
            else:
                sound = self.ENEMY_DAMAGED_BY_PROJECTILE
        elif hitFlags & VHF.MATERIAL_WITH_POSITIVE_DF_NOT_PIERCED_WITH_DAMAGE_BY_PROJECTILE:
            sound = self.ENEMY_DAMAGED_BY_NOT_PIERCING
        elif hitFlags & VHF.MATERIAL_WITH_POSITIVE_DF_PIERCED_BY_EXPLOSION:
            sound = self.ENEMY_DAMAGED_BY_DIRECT_EXPLOSION
        elif hitFlags & VHF.RICOCHET and not hitFlags & VHF.DEVICE_PIERCED_BY_PROJECTILE:
            sound = self.ENEMY_RICOCHET
            if enemiesHitCount == 1:
                TriggersManager.g_manager.fireTrigger(TriggersManager.TRIGGER_TYPE.PLAYER_SHOT_RICOCHET, targetId=enemyVehID)
        elif hitFlags & VHF.MATERIAL_WITH_POSITIVE_DF_NOT_PIERCED_BY_PROJECTILE:
            if hitFlags & (VHF.GUN_DAMAGED_BY_PROJECTILE | VHF.GUN_DAMAGED_BY_EXPLOSION):
                sound = self.ENEMY_NOT_DAMAGED_ATTEMPT_AND_GUN_DAMAGED
            elif hitFlags & (VHF.CHASSIS_DAMAGED_BY_PROJECTILE | VHF.CHASSIS_DAMAGED_BY_EXPLOSION):
                sound = self.ENEMY_NOT_DAMAGED_ATTEMPT_AND_CHASSIS_DAMAGED
            else:
                sound = self.ENEMY_NOT_DAMAGED_ATTEMPT
                if enemiesHitCount == 1:
                    TriggersManager.g_manager.fireTrigger(TriggersManager.TRIGGER_TYPE.PLAYER_SHOT_NOT_PIERCED, targetId=enemyVehID)
        elif hitFlags & (VHF.GUN_DAMAGED_BY_PROJECTILE | VHF.GUN_DAMAGED_BY_EXPLOSION):
            sound = self.ENEMY_NOT_DAMAGED_NO_ATTEMPT_AND_GUN_DAMAGED
        elif hitFlags & (VHF.CHASSIS_DAMAGED_BY_PROJECTILE | VHF.CHASSIS_DAMAGED_BY_EXPLOSION):
            sound = self.ENEMY_NOT_DAMAGED_NO_ATTEMPT_AND_CHASSIS_DAMAGED
        else:
            if hitFlags & VHF.IS_ANY_PIERCING_MASK and not hitFlags & self._ARMOR_SCREEN_FLAGS:
                sound = self.ENEMY_NOT_DAMAGED_NO_ATTEMPT
            else:
                sound = self.ENEMY_NOT_DAMAGED_AND_NOT_PIERCED
            if enemiesHitCount == 1:
                TriggersManager.g_manager.fireTrigger(TriggersManager.TRIGGER_TYPE.PLAYER_SHOT_NOT_PIERCED, targetId=enemyVehID)
        return sound

    def __invalidateCurrentVehicle(self, vehicle):
        self.__eventPrefix = self._DEFAULT_EVENT_PREFIX
        if vehicle is not None and vehicle.typeDescriptor.isAutoShootGunVehicle:
            self.__eventPrefix = self._FREQUENT_EVENT_PREFIX
        return
