# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/wt_sounds_manager.py
import BigWorld
import CGF
import WWISE
import GenericComponents
import Statuses
import InstantStatuses
import logging
from constants import CURRENT_REALM, IS_CHINA, ARENA_PERIOD, ATTACK_REASON, ATTACK_REASONS, WT_COMPONENT_NAMES
from shared_utils import findFirst
from Vehicle import Vehicle, SpawnComponent
from cgf_script.managers_registrator import onAddedQuery, onRemovedQuery, onProcessQuery, registerComponent
from cgf_components import wt_helpers, sound_helpers, PlayerVehicleTag
from gui.battle_control.controllers.teleport_spawn_ctrl import ISpawnListener
from vehicle_systems.tankStructure import TankSoundObjectsIndexes
from Generator import GeneratorCapturedComponent
import Generator
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from account_helpers import AccountSettings
from account_helpers.AccountSettings import WT_BATTLES_DONE_BOSS, WT_BATTLES_DONE_HUNTER
from helpers.CallbackDelayer import CallbackDelayer
_logger = logging.getLogger(__name__)

@registerComponent
class WtBossImpulse(object):
    pass


@registerComponent
class WtGeneratorEmerging(object):
    pass


@registerComponent
class WtMinibossImpulse(object):
    pass


@registerComponent
class WtStunnedByBoss(object):
    pass


def getAllSwitches(wtVehicleName=None):
    allSwitches = {}
    for switch in (LanguageSwitchManager.getLanguageSwitch(), VehicleSwitchManager.getVehicleSwitch(wtVehicleName)):
        allSwitches.update(switch)

    return allSwitches


class LanguageSwitchManager(CGF.ComponentManager):
    _NAME = 'SWITCH_ext_WT_vo_language'
    _RU_REALMS = ('QA', 'RU')
    _VALUE_RU = 'SWITCH_ext_WT_vo_language_RU'
    _VALUE_NON_RU = 'SWITCH_ext_WT_vo_language_nonRU'
    _VALUE_CN = 'SWITCH_ext_WT_vo_language_CN'

    def activate(self):
        WWISE.WW_setSwitch(self._NAME, self._getValue())

    @classmethod
    def getSwitchGroupName(cls):
        return cls._NAME

    @classmethod
    def getLanguageSwitch(cls):
        return {cls._NAME: cls._getValue()}

    @classmethod
    def _getValue(cls):
        if IS_CHINA:
            return cls._VALUE_CN
        return cls._VALUE_RU if CURRENT_REALM in cls._RU_REALMS else cls._VALUE_NON_RU


class WTBattleCountManager(object):
    _BATTLE_COUNT_SETTINGS = {False: WT_BATTLES_DONE_HUNTER,
     True: WT_BATTLES_DONE_BOSS}
    _BATTLE_COUNT_EXPERT = 10

    @classmethod
    def getBattleCount(cls, isBoss):
        settingsFlag = cls._BATTLE_COUNT_SETTINGS.get(isBoss, None)
        if not settingsFlag:
            return 0
        else:
            battleCount = AccountSettings.getSettings(settingsFlag)
            return battleCount

    @classmethod
    def increaseBattleCount(cls):
        settingsFlag = cls._BATTLE_COUNT_SETTINGS.get(wt_helpers.isBoss(), None)
        if not settingsFlag:
            return
        else:
            battleCount = AccountSettings.getSettings(settingsFlag)
            AccountSettings.setSettings(settingsFlag, battleCount + 1)
            return

    @classmethod
    def isExpert(cls, isBoss):
        return True if cls.getBattleCount(isBoss) > cls._BATTLE_COUNT_EXPERT else False


class PlayerExperienceSwitchManager(CGF.ComponentManager):
    _NAME = 'SWITCH_ext_WT_vo_player_experience'
    _VALUE_BEGINNER = 'SWITCH_ext_WT_vo_player_experience_beginner'
    _VALUE_EXPERT = 'SWITCH_ext_WT_vo_player_experience_expert'

    def activate(self):
        WWISE.WW_setSwitch(self._NAME, self._getValue())

    @classmethod
    def getSwitchGroupName(cls):
        return cls._NAME

    @classmethod
    def _getValue(cls):
        return cls._VALUE_EXPERT if WTBattleCountManager.isExpert(wt_helpers.isBoss()) else cls._VALUE_BEGINNER


class VehicleSwitchManager(CGF.ComponentManager):
    _NAME = 'SWITCH_ext_WT_vo_char'
    _VALUES = {'R97_Object_140': 'SWITCH_ext_WT_vo_char_Ob140',
     'F18_Bat_Chatillon25t': 'SWITCH_ext_WT_vo_char_B25t',
     'A120_M48A5': 'SWITCH_ext_WT_vo_char_M48P',
     'Cz04_T50_51_Waf_Hound_3DSt': 'SWITCH_ext_WT_vo_char_TVP',
     'G98_Waffentrager_E100_TLXXL': 'SWITCH_ext_WT_vo_char_WT'}

    @onAddedQuery(Vehicle, PlayerVehicleTag)
    def onVehicleAdded(self, vehicle, _):
        value = self._getValue(vehicle)
        if value is not None:
            WWISE.WW_setSwitch(self._NAME, value)
        return

    @classmethod
    def getSwitchGroupName(cls):
        return cls._NAME

    @classmethod
    def getVehicleSwitch(cls, vehicleName=None):
        if vehicleName:
            for key in cls._VALUES:
                if key in vehicleName:
                    return {cls._NAME: cls._VALUES[key]}

            return {}
        else:
            value = cls._getValue(wt_helpers.getPlayerVehicle())
            return {cls._NAME: value} if value is not None else {}

    @classmethod
    def _getValue(cls, vehicle):
        if vehicle is not None:
            vehicleName = vehicle.typeDescriptor.name
            value = findFirst(lambda i: i[0] in vehicleName, cls._VALUES.items())
            if value is not None:
                return value[1]
        return


class EndBattleSoundManager(CGF.ComponentManager):
    _WINNER_WT = 'wt_both_vo_w_win'
    _WINNER_HUNTER = 'wt_both_vo_hunters_win'

    def activate(self):
        arena = getattr(BigWorld.player(), 'arena', None)
        if arena is not None:
            arena.onPeriodChange += self.__onArenaPeriodChange
        return

    def deactivate(self):
        arena = getattr(BigWorld.player(), 'arena', None)
        if arena is not None:
            arena.onPeriodChange -= self.__onArenaPeriodChange
        return

    def __onArenaPeriodChange(self, *args):
        period, _, _, additionalInfo = args
        if period == ARENA_PERIOD.AFTERBATTLE:
            isWinner = additionalInfo[0] == getattr(BigWorld.player(), 'team', 0)
            if isWinner:
                if wt_helpers.isBoss():
                    sound_helpers.playNotification(self._WINNER_WT)
                else:
                    sound_helpers.playNotification(self._WINNER_HUNTER)
            elif wt_helpers.isBoss():
                sound_helpers.playNotification(self._WINNER_HUNTER)
            else:
                sound_helpers.playNotification(self._WINNER_WT)


class ShieldSoundManager(CGF.ComponentManager):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _PLAYER_BOSS_SHIELD_ADDED = {False: 'wt23_w_vo_shield_restored',
     True: 'wt23_w_vo_shield_restored_eos_one'}
    _PLAYER_HUNTER_SHIELD_ADDED = 'wt23_hunters_vo_shield_restored'
    _PLAYER_W_HUNTER_SHOOTING_AT_WT_SHIELD = 'wt23_w_vo_shooting_at_wt_shield'
    _PLAYER_BOSS_NO_SHIELD_IMPACT_3D = 'ev_white_tiger_force_field_off'

    def __init__(self):
        super(ShieldSoundManager, self).__init__()
        self.__hasDebuff = wt_helpers.getHasDebuff()
        self.__arenaPeriod = ARENA_PERIOD.IDLE

    def activate(self):
        arena = getattr(BigWorld.player(), 'arena', None)
        if arena is not None:
            arena.onPeriodChange += self.__onArenaPeriodChange
        feedback = self.__sessionProvider.shared.feedback
        if feedback:
            feedback.onArenaTimer += self.__onArenaTimer
        return

    def deactivate(self):
        arena = getattr(BigWorld.player(), 'arena', None)
        if arena is not None:
            arena.onPeriodChange -= self.__onArenaPeriodChange
        feedback = self.__sessionProvider.shared.feedback
        if feedback:
            feedback.onArenaTimer -= self.__onArenaTimer
        return

    def __onArenaPeriodChange(self, *args):
        period, _, _, _ = args
        self.__arenaPeriod = period

    def __onArenaTimer(self, name, _, remainingTime):
        if self.__arenaPeriod != ARENA_PERIOD.BATTLE:
            return
        else:
            if name == WT_COMPONENT_NAMES.SHIELD_DEBUFF_ARENA_TIMER:
                if remainingTime <= 0 and self.__hasDebuff:
                    if wt_helpers.isBoss():
                        notification = self._PLAYER_BOSS_SHIELD_ADDED.get(wt_helpers.isMinibossInArena(), None)
                        if notification:
                            sound_helpers.playNotification(notification)
                    else:
                        sound_helpers.playNotification(self._PLAYER_HUNTER_SHIELD_ADDED)
                self.__hasDebuff = remainingTime > 0
            return

    @onAddedQuery(InstantStatuses.ProjectileHitsReceivedComponent, CGF.GameObject)
    def onShotDamageReceived(self, _, go):
        vehicle = sound_helpers.getVehicle(go, self.spaceID)
        if vehicle is not None and wt_helpers.isBossVehicle(vehicle):
            if not wt_helpers.getHasDebuff():
                if wt_helpers.isBoss() and wt_helpers.getBossVehicleHealthPercent() > 3.0:
                    sound_helpers.playNotification(self._PLAYER_W_HUNTER_SHOOTING_AT_WT_SHIELD)
            else:
                sound_helpers.playVehicleSound(self._PLAYER_BOSS_NO_SHIELD_IMPACT_3D, vehicle)
        return


class GeneratorCaptureSoundManager(CGF.ComponentManager, CallbackDelayer):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _PLAYER_HUNTER_START_CAPTURE = 'wt_hunters_vo_capture_point'
    _PLAYER_BOSS_START_CAPTURE = 'wt23_w_vo_generator_capture'
    _PLAYER_HUNTER_GENERATOR_BLOCKED = 'wt_hunters_vo_generator_blocked'
    _PLAYER_HUNTER_GENERATOR_DESTROYED = {False: 'wt23_hunters_vo_shield_destroyed',
     True: 'wt23_hunters_vo_shield_destroyed_player_is_capturer'}
    _PLAYER_HUNTER_LAST_GENERATOR_DESTROYED = {False: 'wt23_hunters_vo_last_generator_destroyed',
     True: 'wt23_hunters_vo_last_generator_destroyed_player_is_capturer'}
    _PLAYER_BOSS_GENERATOR_BLOCKED = 'wt_w_vo_generator_blocked'
    _PLAYER_BOSS_GENERATOR_DESTROYED = {False: 'wt23_w_vo_shield_destroyed',
     True: 'wt23_w_vo_shield_destroyed_eos_one'}
    _PLAYER_BOSS_LAST_GENERATOR_DESTROYED = 'wt23_w_vo_last_generator_destroyed'
    _GENERATOR_EMERGING_3D = 'ev_white_tiger_tower_generator_emerging'
    _GENERATOR_CAPTURE_START_3D = 'ev_white_tiger_tower_generator_start_capture'
    _GENERATOR_CAPTURE_FAILED_3D = 'ev_white_tiger_tower_generator_downing_capture'
    _GENERATOR_CAPTURED_3D = 'ev_white_tiger_tower_generator_destruction'
    _GENERATOR_BLOCKED_3D = 'ev_white_tiger_tower_generator_blocked'
    _GENERATOR_CAPTURED_3D_SOUND_LENGTH = 14.0
    _GENERATOR_CAPTURE_RTCP = 'RTPC_ext_white_tiger_progress'
    _soundObjectName = 'generatorSoundObject_'
    _soundObjects = {}
    _entityIDs = {}
    __entityIdBlockedGenerator = None

    def __init__(self):
        super(GeneratorCaptureSoundManager, self).__init__()
        CallbackDelayer.__init__(self)
        self.__capturedIDs = None
        return

    def activate(self):
        feedback = self.__sessionProvider.shared.feedback
        if feedback is not None:
            feedback.onGeneratorLocked += self.__onGeneratorLocked
        return

    def deactivate(self):
        feedback = self.__sessionProvider.shared.feedback
        if feedback is not None:
            feedback.onGeneratorLocked -= self.__onGeneratorLocked
        self.clearCallbacks()
        for soundObject in self._soundObjects.values():
            soundObject.stopAll()

        self._soundObjects.clear()
        self._entityIDs.clear()
        return

    @onAddedQuery(CGF.GameObject, WtGeneratorEmerging)
    def onGeneratorEmerging(self, go, _):
        parent = self.__getParentGO(go)
        progressComp = parent.findComponentByType(GenericComponents.GeneratorProgressComponent)
        if progressComp:
            return
        goSyncComponent = parent.findComponentByType(GenericComponents.EntityGOSync)
        entityID = goSyncComponent.entity.id
        if entityID not in self._soundObjects:
            soundObjectName = self._soundObjectName + str(entityID)
            transform = parent.findComponentByType(GenericComponents.TransformComponent)
            position = transform.worldPosition
            self._soundObjects[entityID] = sound_helpers.createSoundObject(soundObjectName, position)
            self._soundObjects[entityID].play(self._GENERATOR_EMERGING_3D)
        else:
            self.__playSound(entityID, self._GENERATOR_EMERGING_3D)

    @onAddedQuery(GenericComponents.GeneratorProgressComponent, CGF.GameObject)
    def onGeneratorProgressComponentAdded(self, progressComponent, go):
        parent = self.__getParentGO(go)
        transform = parent.findComponentByType(GenericComponents.TransformComponent)
        position = transform.worldPosition
        goSyncComponent = parent.findComponentByType(GenericComponents.EntityGOSync)
        entityID = goSyncComponent.entity.id
        notification = self._PLAYER_HUNTER_START_CAPTURE
        if wt_helpers.isBoss():
            notification = self._PLAYER_BOSS_START_CAPTURE
        distToGenerator = sound_helpers.getPlayerVehicleDistToGO(self.spaceID, position)
        triggerDist = float(sound_helpers.getEventInfo(notification, 'infDist'))
        if distToGenerator <= triggerDist and entityID != self.__entityIdBlockedGenerator:
            sound_helpers.playNotification(notification)
        if entityID not in self._entityIDs:
            self._entityIDs[progressComponent] = entityID
        if entityID not in self._soundObjects:
            soundObjectName = self._soundObjectName + str(entityID)
            self._soundObjects[entityID] = sound_helpers.createSoundObject(soundObjectName, position)
        self.__playSound(entityID, self._GENERATOR_CAPTURE_START_3D)

    @onProcessQuery(GenericComponents.GeneratorProgressComponent, CGF.GameObject)
    def onProcessGeneratorProgressComponent(self, progressComponent, go):
        progressPercent = 100 * progressComponent.progress / Generator.MAX_PROGRESS
        self.__setRTPC(progressComponent, progressPercent)

    @onRemovedQuery(GenericComponents.GeneratorProgressComponent, CGF.GameObject)
    def onGeneratorProgressComponentRemoved(self, progressComponent, go):
        entityID = self.__getEntityIDFromGO(go)
        capturedComponent = go.findComponentByType(GeneratorCapturedComponent)
        if capturedComponent is not None:
            self.__playSound(entityID, self._GENERATOR_CAPTURED_3D)
            self.delayCallback(self._GENERATOR_CAPTURED_3D_SOUND_LENGTH, self.__removeSoundObject, entityID)
            self.__capturedIDs = capturedComponent.vehiclesIDs
            go.removeComponentByType(GeneratorCapturedComponent)
        else:
            self.__playSound(entityID, self._GENERATOR_CAPTURE_FAILED_3D)
        if progressComponent in self._entityIDs:
            self._entityIDs.pop(progressComponent)
        return

    def __onGeneratorLocked(self, generatorID, isLocked, entityID):
        if isLocked:
            self.__playSound(entityID, self._GENERATOR_BLOCKED_3D)
            self.__entityIdBlockedGenerator = entityID
            if wt_helpers.isBoss():
                sound_helpers.playNotification(self._PLAYER_BOSS_GENERATOR_BLOCKED)
            else:
                sound_helpers.playNotification(self._PLAYER_HUNTER_GENERATOR_BLOCKED)
        else:
            self.__entityIdBlockedGenerator = None
            if entityID in self._entityIDs.values():
                self.__playSound(entityID, self._GENERATOR_CAPTURE_START_3D)
        return

    def __playSound(self, entityID, soundID):
        if entityID in self._soundObjects:
            if not self.__entityIdBlockedGenerator == entityID:
                self._soundObjects[entityID].play(soundID)

    def __setRTPC(self, progressComponent, valueRTPC):
        if progressComponent in self._entityIDs:
            entityID = self._entityIDs[progressComponent]
            if entityID in self._soundObjects:
                self._soundObjects[entityID].setRTPC(self._GENERATOR_CAPTURE_RTCP, valueRTPC)

    def __removeSoundObject(self, entityID):
        if entityID in self._soundObjects:
            self._soundObjects[entityID].stopAll()
            self._soundObjects.pop(entityID)

    def __getEntityIDFromGO(self, go):
        parent = self.__getParentGO(go)
        goSyncComponent = parent.findComponentByType(GenericComponents.EntityGOSync)
        if goSyncComponent:
            entityID = goSyncComponent.entity.id
            return entityID
        else:
            return None

    def __getParentGO(self, go):
        hierarchy = CGF.HierarchyManager(self.spaceID)
        return hierarchy.getTopMostParent(go)

    @onAddedQuery(GenericComponents.BattleStage, CGF.GameObject)
    def onBattleStageAdded(self, component, go):
        if component.current < component.maximum:
            isBoss = wt_helpers.isBoss()
            notification = None
            if component.current == 0:
                if isBoss:
                    notification = self._PLAYER_BOSS_LAST_GENERATOR_DESTROYED
                else:
                    isCapturer = self.__playerIsCapturer()
                    notification = self._PLAYER_HUNTER_LAST_GENERATOR_DESTROYED.get(isCapturer, None)
            elif isBoss:
                notification = self._PLAYER_BOSS_GENERATOR_DESTROYED.get(wt_helpers.isMinibossInArena(), None)
            else:
                isCapturer = self.__playerIsCapturer()
                notification = self._PLAYER_HUNTER_GENERATOR_DESTROYED.get(isCapturer, None)
            if notification:
                sound_helpers.playNotification(notification)
            self.__capturedIDs = None
        return

    def __playerIsCapturer(self):
        return BigWorld.player().vehicle.id in self.__capturedIDs if self.__capturedIDs and BigWorld.player().vehicle else False


class VehicleKilledSoundManager(CGF.ComponentManager):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _PLAYER_HUNTER_VEHICLE_DESTROYED = ('wt_hunters_vo_vehicle_destroyed', 'wt_krieger_vo_wt_enemy_killed')
    _BOSS_DESTROYED_PC_3D = 'ev_white_tiger_wt_escape_pc'
    _BOSS_DESTROYED_NPC_3D = 'ev_white_tiger_wt_escape_npc'
    _BOSS_DESTROYED = 'vehicle_destroyed'

    def activate(self):
        arena = getattr(BigWorld.player(), 'arena', None)
        if arena is not None:
            arena.onVehicleKilled += self.__onArenaVehicleKilled
        return

    def deactivate(self):
        arena = getattr(BigWorld.player(), 'arena', None)
        if arena is not None:
            arena.onVehicleKilled -= self.__onArenaVehicleKilled
        return

    def __onArenaVehicleKilled(self, *args):
        vId, _, _, reason, _ = args
        bossVehicle = wt_helpers.getBossVehicle()
        if bossVehicle is not None and bossVehicle.id == vId:
            if wt_helpers.isBoss():
                sound_helpers.play3d(self._BOSS_DESTROYED_PC_3D, bossVehicle.entityGameObject, self.spaceID)
                if reason == ATTACK_REASONS.index(ATTACK_REASON.DROWNING):
                    sound_helpers.playNotification(self._BOSS_DESTROYED)
            else:
                sound_helpers.play3d(self._BOSS_DESTROYED_NPC_3D, bossVehicle.entityGameObject, self.spaceID)
        elif BigWorld.player().vehicle and BigWorld.player().vehicle.id == vId:
            for notification in self._PLAYER_HUNTER_VEHICLE_DESTROYED:
                sound_helpers.playNotification(notification)

        return


class BossAbilitySoundManager(CGF.ComponentManager):
    _PLAYER_BOSS_STUN_IMPULSE = 'wt_w_vo_ability_emp'
    _PLAYER_BOSS_STUN = 'wt_w_vo_ability_stun_shell'
    _PLAYER_HUNTER_STUN_IMPULSE = 'wt_hunters_vo_ability_emp'
    _PLAYER_HUNTER_STUN_SHELL = 'wt_hunters_vo_stun_shell'
    _PLAYER_HUNTER_STUN_EMI_2D_START = 'ev_white_tiger_stun_effect_start'
    _PLAYER_HUNTER_STUN_EMI_2D_END = 'ev_white_tiger_stun_effect_end'
    _PLAYER_HUNTER_STUN_POWER_DOWN_2D = 'ev_white_tiger_stun_effect_power_down'
    _PLAYER_HUNTER_STUN_2D = 'ev_white_tiger_stun_effect_imp_start'
    _PLAYER_HUNTER_STUN_2D_STOP = 'ev_white_tiger_stun_effect_imp_end'
    _PLAYER_HUNTER_STUN_POWER_UP_2D = 'ev_white_tiger_stun_effect_power_up'

    def __init__(self):
        super(BossAbilitySoundManager, self).__init__()
        self.__isPlayerStun = False
        self.__isPlayerStunEMI = False
        self.__stunNotificationPlayed = False
        self.__isMinibossImpulse = False

    def activate(self):
        self.__isPlayerStun = False
        self.__isPlayerStunEMI = False
        self.__isMinibossImpulse = False

    def deactivate(self):
        self.__stunNotificationPlayed = False
        if self.__isPlayerStun:
            sound_helpers.play2d(self._PLAYER_HUNTER_STUN_2D_STOP)
            self.__isPlayerStun = False
        if self.__isPlayerStunEMI:
            sound_helpers.play2d(self._PLAYER_HUNTER_STUN_EMI_2D_END)
            self.__isPlayerStunEMI = False

    @onAddedQuery(WtMinibossImpulse, CGF.GameObject)
    def onMinibossImpulseAdded(self, *_):
        self.__isMinibossImpulse = True

    @onRemovedQuery(WtMinibossImpulse, CGF.GameObject)
    def onMinibossImpulseRemoved(self, *_):
        self.__isMinibossImpulse = False

    @onAddedQuery(WtStunnedByBoss, CGF.GameObject)
    def onStunnedByBossAdded(self, _, go):
        vehicle = sound_helpers.getVehicle(go, self.spaceID)
        self.__onStunnedByBossNotification(vehicle)

    @onAddedQuery(Statuses.StunComponent, CGF.GameObject)
    def onStunComponentAdded(self, _, go):
        vehicle = sound_helpers.getVehicle(go, self.spaceID)
        if not wt_helpers.isPlayerVehicle(vehicle):
            return
        sound_helpers.play2d(self._PLAYER_HUNTER_STUN_POWER_DOWN_2D)
        if self.__isBossImpulse() or self.__isMinibossImpulse:
            sound_helpers.play2d(self._PLAYER_HUNTER_STUN_EMI_2D_START)
            self.__isPlayerStunEMI = True
        else:
            sound_helpers.play2d(self._PLAYER_HUNTER_STUN_2D)
            self.__isPlayerStun = True

    @onRemovedQuery(Statuses.StunComponent, CGF.GameObject)
    def onStunComponentRemoved(self, _, go):
        self.__stunNotificationPlayed = False
        vehicle = sound_helpers.getVehicle(go, self.spaceID)
        if not wt_helpers.isPlayerVehicle(vehicle):
            return
        sound_helpers.play2d(self._PLAYER_HUNTER_STUN_POWER_UP_2D)
        if self.__isPlayerStunEMI:
            sound_helpers.play2d(self._PLAYER_HUNTER_STUN_EMI_2D_END)
            self.__isPlayerStunEMI = False
        if self.__isPlayerStun:
            sound_helpers.play2d(self._PLAYER_HUNTER_STUN_2D_STOP)
            self.__isPlayerStun = False

    def __onStunnedByBossNotification(self, vehicle):
        if self.__isBossImpulse():
            if wt_helpers.isBoss() and not self.__stunNotificationPlayed:
                sound_helpers.playNotification(self._PLAYER_BOSS_STUN_IMPULSE)
                self.__stunNotificationPlayed = True
            elif wt_helpers.isPlayerVehicle(vehicle):
                sound_helpers.playNotification(self._PLAYER_HUNTER_STUN_SHELL)
        elif wt_helpers.isBoss():
            sound_helpers.playNotification(self._PLAYER_BOSS_STUN)
        elif wt_helpers.isPlayerVehicle(vehicle):
            sound_helpers.playNotification(self._PLAYER_HUNTER_STUN_SHELL)

    def __isBossImpulse(self):
        bossVehicle = wt_helpers.getBossVehicle()
        if bossVehicle is None:
            return False
        else:
            hasBossImpulse = bossVehicle.entityGameObject.findComponentByType(WtBossImpulse) is not None
            return hasBossImpulse


class ShootingSoundManager(CGF.ComponentManager):
    _SHOOTING_NPC_3D = {'R97_Object_140': 'ev_white_tiger_wpn_hunters_01_npc',
     'F18_Bat_Chatillon25t': 'ev_white_tiger_wpn_hunters_02_npc',
     'A120_M48A5': 'ev_white_tiger_wpn_hunters_02_npc',
     'Cz04_T50_51_Waf_Hound_3DSt': 'ev_white_tiger_wpn_hunters_01_npc',
     'G98_Waffentrager_E100_TL': 'ev_white_tiger_wpn_waffentrager_npc'}

    @onAddedQuery(InstantStatuses.ShotsDoneComponent, CGF.GameObject)
    def onShotComponentAdded(self, _, go):
        vehicle = sound_helpers.getVehicle(go, self.spaceID)
        if vehicle is not None and not wt_helpers.isPlayerVehicle(vehicle):
            vehicleName = vehicle.typeDescriptor.name
            value = findFirst(lambda i: i[0] in vehicleName, self._SHOOTING_NPC_3D.items())
            if value is not None:
                sound_helpers.playVehiclePart(value[1], vehicle, TankSoundObjectsIndexes.GUN)
        return


class SpawnSoundManager(CGF.ComponentManager):
    _SPAWN_HUNTER_3D = 'ev_white_tiger_spawn_hunters'

    @onAddedQuery(SpawnComponent, CGF.GameObject)
    def onSpawnComponentAdded(self, _, go):
        vehicle = sound_helpers.getVehicle(go, self.spaceID)
        if vehicle is not None and not wt_helpers.isBossVehicle(vehicle):
            sound_helpers.playVehicleSound(self._SPAWN_HUNTER_3D, vehicle)
            vehicle.appearance.removeComponentByType(SpawnComponent)
        return


class RespawnSoundPlayer(ISpawnListener):
    _RESPAWN_VIEW_SHOW = 'ev_white_tiger_waiting_overlay_ambient'
    _RESPAWN_VIEW_HIDE = 'ev_white_tiger_waiting_overlay_ambient_stop'
    _STATE_NAME = 'STATE_white_tiger_gameplay_waiting'
    _STATE_SHOWN_VALUE = 'STATE_white_tiger_gameplay_waiting_on'
    _STATE_HIDDEN_VALUE = 'STATE_white_tiger_gameplay_waiting_off'

    def showSpawnPoints(self):
        sound_helpers.play2d(self._RESPAWN_VIEW_SHOW)
        sound_helpers.setState(self._STATE_NAME, self._STATE_SHOWN_VALUE)

    def closeSpawnPoints(self):
        sound_helpers.play2d(self._RESPAWN_VIEW_HIDE)
        sound_helpers.setState(self._STATE_NAME, self._STATE_HIDDEN_VALUE)


class GameplayEnterSoundPlayer(CGF.ComponentManager, CallbackDelayer):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _GAMEPLAY_ENTER = 'ev_white_tiger_gameplay_enter'
    _GAMEPLAY_EXIT = 'ev_white_tiger_gameplay_exit'
    _WT23_VO_PREBATTLE_DIALOGUE = 'wt23_vo_dialogue_prebattle'
    _PREBATTLE_DIALOGUE_START_TIME = 23.0

    def __init__(self):
        super(GameplayEnterSoundPlayer, self).__init__()
        CallbackDelayer.__init__(self)
        self.__enterSoundPlayed = False

    def activate(self):
        arenaPeriod = self.__sessionProvider.shared.arenaPeriod.getPeriod()
        if arenaPeriod == ARENA_PERIOD.BATTLE:
            self.__playEnterSound()
        arena = getattr(BigWorld.player(), 'arena', None)
        if arena is not None:
            arena.onPeriodChange += self.__onArenaPeriodChange
        return

    def deactivate(self):
        self.__playExitSound()
        self.clearCallbacks()
        arena = getattr(BigWorld.player(), 'arena', None)
        if arena is not None:
            arena.onPeriodChange -= self.__onArenaPeriodChange
        return

    def __onArenaPeriodChange(self, *args):
        period, periodEndTime, _, _ = args
        if period == ARENA_PERIOD.PREBATTLE:
            WTBattleCountManager.increaseBattleCount()
            timeToPeriodEnd = max(periodEndTime - BigWorld.serverTime(), 0.0)
            if timeToPeriodEnd > self._PREBATTLE_DIALOGUE_START_TIME:
                notificationDelay = max(timeToPeriodEnd - self._PREBATTLE_DIALOGUE_START_TIME, 0.0)
                self.delayCallback(notificationDelay, self.__playPrebattleDialogue)
        if period == ARENA_PERIOD.BATTLE:
            self.__playEnterSound()
        if period == ARENA_PERIOD.AFTERBATTLE:
            self.__playExitSound()

    def __playEnterSound(self):
        sound_helpers.play2d(self._GAMEPLAY_ENTER)
        self.__enterSoundPlayed = True

    def __playExitSound(self):
        if self.__enterSoundPlayed:
            sound_helpers.play2d(self._GAMEPLAY_EXIT)
            self.__enterSoundPlayed = False

    def __playPrebattleDialogue(self):
        sound_helpers.playNotification(self._WT23_VO_PREBATTLE_DIALOGUE)
