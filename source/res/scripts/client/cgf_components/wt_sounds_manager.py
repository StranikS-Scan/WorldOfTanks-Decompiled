# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/wt_sounds_manager.py
import BigWorld
import CGF
import WWISE
import GenericComponents
import Health
import Projectiles
import logging
from constants import ARENA_PERIOD, ATTACK_REASON, ATTACK_REASONS, WT_COMPONENT_NAMES, EQUIPMENT_STAGES
from shared_utils import findFirst
from Vehicle import Vehicle, SpawnComponent
from cgf_script.managers_registrator import onAddedQuery, onRemovedQuery, onProcessQuery
from cgf_components import wt_helpers, sound_helpers, PlayerVehicleTag
from gui.battle_control.controllers.teleport_spawn_ctrl import ISpawnListener
from vehicle_systems.tankStructure import TankSoundObjectsIndexes
from EntityWTGeneratorComponent import GeneratorCapturedComponent, MAX_PROGRESS as GENERATOR_MAX_PROGRESS
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from account_helpers import AccountSettings
from account_helpers.AccountSettings import WT_BATTLES_DONE_BOSS, WT_BATTLES_DONE_HUNTER
from helpers.CallbackDelayer import CallbackDelayer
_logger = logging.getLogger(__name__)

def getAllSwitches():
    allSwitches = {}
    for switch in (LanguageSwitchManager.getLanguageSwitch(), VehicleSwitchManager.getVehicleSwitch()):
        allSwitches.update(switch)

    return allSwitches


class LanguageSwitchManager(CGF.ComponentManager):
    _NAME = 'SWITCH_ext_WT_vo_language'
    _VALUE_RU = 'SWITCH_ext_WT_vo_language_RU'

    def activate(self):
        WWISE.WW_setSwitch(self._NAME, self._getValue())

    @classmethod
    def getLanguageSwitch(cls):
        return {cls._NAME: cls._getValue()}

    @classmethod
    def _getValue(cls):
        return cls._VALUE_RU


class PlayerExperienceSwitchManager(CGF.ComponentManager):
    _NAME = 'SWITCH_ext_WT_vo_player_experience'
    _VALUE_BEGINNER = 'SWITCH_ext_WT_vo_player_experience_beginner'
    _VALUE_EXPERT = 'SWITCH_ext_WT_vo_player_experience_expert'
    _BATTLE_COUNT_SETTINGS = {False: WT_BATTLES_DONE_HUNTER,
     True: WT_BATTLES_DONE_BOSS}
    _BATTLE_COUNT_EXPERT = 10

    def activate(self):
        battleCount = self.getBattleCount(wt_helpers.isBoss())
        WWISE.WW_setSwitch(self._NAME, self._getValue(battleCount))

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

    @classmethod
    def _getValue(cls, battleCount):
        return cls._VALUE_EXPERT if battleCount > cls._BATTLE_COUNT_EXPERT else cls._VALUE_BEGINNER


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
    def getVehicleSwitch(cls):
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
    _PLAYER_WT_WT_WIN = 'wt23_dialogue_vo_wt_win'
    _PLAYER_WT_HUNTERS_WIN = 'wt23_wt_vo_hunters_win'
    _PLAYER_HUNTER_WT_WIN = 'wt_krieger_vo_wt_win'
    _PLAYER_HUNTER_HUNTERS_WIN = 'wt23_hunters_vo_hunters_win_fb'
    _GAMEPLAY_EXIT = 'ev_white_tiger_gameplay_exit'

    def __init__(self):
        super(EndBattleSoundManager, self).__init__()
        self.__exitEventWasPlayed = False

    def activate(self):
        arena = getattr(BigWorld.player(), 'arena', None)
        if arena is not None:
            arena.onPeriodChange += self.__onArenaPeriodChange
            arena.onTeamInfoUnregistered += self.__onTeamInfoUnregistered
        return

    def deactivate(self):
        arena = getattr(BigWorld.player(), 'arena', None)
        if arena is not None:
            arena.onPeriodChange -= self.__onArenaPeriodChange
            arena.onTeamInfoUnregistered -= self.__onTeamInfoUnregistered
        return

    def __onTeamInfoUnregistered(self, *args):
        if not self.__exitEventWasPlayed:
            sound_helpers.play2d(self._GAMEPLAY_EXIT)
            self.__exitEventWasPlayed = True

    def __onArenaPeriodChange(self, *args):
        period, _, _, additionalInfo = args
        if period == ARENA_PERIOD.AFTERBATTLE:
            isWinner = additionalInfo[0] == getattr(BigWorld.player(), 'team', 0)
            if isWinner:
                if wt_helpers.isBoss():
                    sound_helpers.playNotification(self._PLAYER_WT_WT_WIN)
                else:
                    sound_helpers.playNotification(self._PLAYER_HUNTER_HUNTERS_WIN)
            elif wt_helpers.isBoss():
                sound_helpers.playNotification(self._PLAYER_WT_HUNTERS_WIN)
            else:
                sound_helpers.playNotification(self._PLAYER_HUNTER_WT_WIN)
            sound_helpers.play2d(self._GAMEPLAY_EXIT)
            self.__exitEventWasPlayed = True


class FolloweeSoundManager(CGF.ComponentManager):
    _PLAYER_BOSS_BOMB_TAKEN_BY_HUNTERS = 'wt_w_vo_loot_taken_by_enemy'
    _PLAYER_HUNTER_BOMB_TAKEN_BY_HUNTERS = 'wt_hunters_vo_loot_taken_by_ally'
    _BOMB_TAKEN_PC_3D = ('ev_white_tiger_gain_energy_complete_pc', 'ev_white_tiger_gain_energy_on_board')
    _BOMB_TAKEN_NPC_3D = ('ev_white_tiger_gain_energy_complete_npc', 'ev_white_tiger_gain_energy_on_board')
    _BOMB_LOSE_3D = 'ev_white_tiger_gain_energy_off_board'

    @onAddedQuery(GenericComponents.CarryingLootComponent, CGF.GameObject)
    def onCarryingLootAdded(self, _, go):
        if wt_helpers.isBoss():
            sound_helpers.playNotification(self._PLAYER_BOSS_BOMB_TAKEN_BY_HUNTERS)
        else:
            sound_helpers.playNotification(self._PLAYER_HUNTER_BOMB_TAKEN_BY_HUNTERS)
        vehicle = sound_helpers.getVehicle(go, self.spaceID)
        isPlayer = wt_helpers.isPlayerVehicle(vehicle)
        events = self._BOMB_TAKEN_PC_3D if isPlayer else self._BOMB_TAKEN_NPC_3D
        for event in events:
            sound_helpers.playVehicleSound(event, vehicle)

    @onRemovedQuery(GenericComponents.CarryingLootComponent, CGF.GameObject)
    def onCarryingLootRemoved(self, _, go):
        vehicle = sound_helpers.getVehicle(go, self.spaceID)
        if vehicle is not None:
            sound_helpers.playVehicleSound(self._BOMB_LOSE_3D, vehicle)
        return


class ShieldSoundManager(CGF.ComponentManager):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _PLAYER_BOSS_SHIELD_ADDED = 'wt23_w_vo_shield_restored'
    _PLAYER_W_HUNTER_SHOOTING_AT_WT_SHIELD = 'wt23_w_vo_shooting_at_wt_shield'
    _PLAYER_BOSS_NO_SHIELD_IMPACT_3D = 'ev_white_tiger_force_field_off'
    _PLAYER_BOSS_SHIELD_IMPACT_3D = 'ev_white_tiger_force_field_on'

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
        if name == WT_COMPONENT_NAMES.SHIELD_DEBUFF_ARENA_TIMER:
            if remainingTime <= 0 and self.__hasDebuff:
                if wt_helpers.isBoss():
                    sound_helpers.playNotification(self._PLAYER_BOSS_SHIELD_ADDED)
            self.__hasDebuff = remainingTime > 0

    @onAddedQuery(Projectiles.ProjectileHitsReceivedComponent, CGF.GameObject)
    def onShotDamageReceived(self, _, go):
        vehicle = sound_helpers.getVehicle(go, self.spaceID)
        if vehicle is not None and wt_helpers.isBossVehicle(vehicle):
            if not wt_helpers.getHasDebuff():
                sound_helpers.playVehicleSound(self._PLAYER_BOSS_SHIELD_IMPACT_3D, vehicle)
                if wt_helpers.isBoss() and wt_helpers.getBossVehicleHealthPercent() > 3.0:
                    sound_helpers.playNotification(self._PLAYER_W_HUNTER_SHOOTING_AT_WT_SHIELD)
            else:
                sound_helpers.playVehicleSound(self._PLAYER_BOSS_NO_SHIELD_IMPACT_3D, vehicle)
        return


class GeneratorCaptureSoundManager(CGF.ComponentManager):
    _PLAYER_HUNTER_START_CAPTURE = 'wt23_hunters_vo_capture_point'
    _PLAYER_BOSS_START_CAPTURE = 'wt23_w_vo_generator_capture'
    _PLAYER_START_CAPTURE = {True: _PLAYER_BOSS_START_CAPTURE,
     False: _PLAYER_HUNTER_START_CAPTURE}
    _PLAYER_HUNTER_GENERATOR_DESTROYED = 'wt23_hunters_vo_shield_destroyed'
    _PLAYER_HUNTER_LAST_GENERATOR_DESTROYED = 'wt23_hunters_vo_last_generator_destroyed'
    _PLAYER_BOSS_GENERATOR_DESTROYED = 'wt23_w_vo_shield_destroyed'
    _PLAYER_BOSS_LAST_GENERATOR_DESTROYED = 'wt23_w_vo_last_generator_destroyed'
    _GENERATOR_CAPTURE_START_3D = 'ev_white_tiger_tower_generator_start_capture'
    _GENERATOR_CAPTURE_FAILED_3D = 'ev_white_tiger_tower_generator_downing_capture'
    _GENERATOR_CAPTURED_3D = 'ev_white_tiger_tower_generator_destruction'
    _GENERATOR_CAPTURE_RTCP = 'RTPC_ext_white_tiger_progress'
    _soundObjectName = 'generatorSoundObject_'
    _soundObject = None

    def __init__(self):
        super(GeneratorCaptureSoundManager, self).__init__()
        self.__capturedIDs = None
        self.__voTriggerDistance = {True: None,
         False: float(sound_helpers.getEventInfo(self._PLAYER_HUNTER_START_CAPTURE, 'infMaxDist'))}
        return

    @onAddedQuery(GenericComponents.GeneratorProgressComponent, CGF.GameObject)
    def onGeneratorCaptureAdded(self, _, go):
        hierarchy = CGF.HierarchyManager(self.spaceID)
        parent = hierarchy.getTopMostParent(go)
        transform = parent.findComponentByType(GenericComponents.TransformComponent)
        position = transform.worldPosition
        distToGenerator = sound_helpers.getPlayerVehicleDistToGO(self.spaceID, position)
        isBoss = wt_helpers.isBoss()
        if self.__voTriggerDistance[isBoss]:
            if distToGenerator <= self.__voTriggerDistance[isBoss]:
                sound_helpers.playNotification(self._PLAYER_START_CAPTURE[isBoss])
        else:
            sound_helpers.playNotification(self._PLAYER_START_CAPTURE[isBoss])
        objectName = self._soundObjectName + str(parent.id)
        self._soundObject = sound_helpers.createSoundObject(objectName, position)
        if self._soundObject:
            self._soundObject.play(self._GENERATOR_CAPTURE_START_3D)

    @onProcessQuery(GenericComponents.GeneratorProgressComponent)
    def onProcessGeneratorCapture(self, progressComponent):
        progressPercent = 100 * progressComponent.progress / GENERATOR_MAX_PROGRESS
        if self._soundObject:
            self._soundObject.setRTPC(self._GENERATOR_CAPTURE_RTCP, progressPercent)

    @onRemovedQuery(GenericComponents.GeneratorProgressComponent, CGF.GameObject)
    def onGeneratorCaptureRemoved(self, _, go):
        capturedComponent = go.findComponentByType(GeneratorCapturedComponent)
        if capturedComponent is not None:
            if self._soundObject:
                self._soundObject.play(self._GENERATOR_CAPTURED_3D)
            self.__capturedIDs = capturedComponent.vehiclesIDs
            go.removeComponentByType(GeneratorCapturedComponent)
        elif self._soundObject:
            self._soundObject.play(self._GENERATOR_CAPTURE_FAILED_3D)
        return

    @onAddedQuery(GenericComponents.BattleStage, CGF.GameObject)
    def onBattleStageAdded(self, component, go):
        if component.current < component.maximum:
            isBoss = wt_helpers.isBoss()
            self.__capturedIDs = None
            if component.current == 0:
                if isBoss:
                    sound_helpers.playNotification(self._PLAYER_BOSS_LAST_GENERATOR_DESTROYED)
                else:
                    sound_helpers.playNotification(self._PLAYER_HUNTER_LAST_GENERATOR_DESTROYED)
            elif isBoss:
                sound_helpers.playNotification(self._PLAYER_BOSS_GENERATOR_DESTROYED)
            else:
                sound_helpers.playNotification(self._PLAYER_HUNTER_GENERATOR_DESTROYED)
        return


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
    _PLAYER_HUNTER_STUN_EMI_START = 'ev_white_tiger_stun_effect_start'
    _PLAYER_HUNTER_STUN_EMI_END = 'ev_white_tiger_stun_effect_end'
    _PLAYER_HUNTER_STUN_3D = 'ev_white_tiger_stun_effect_imp_start'
    _PLAYER_HUNTER_STUN_3D_STOP = 'ev_white_tiger_stun_effect_imp_end'

    def __init__(self):
        super(BossAbilitySoundManager, self).__init__()
        self.__isPlayerStun3D = False
        self.__isPlayerStunEMI = False
        self.__stunImpulseIsPlaying = False

    @onAddedQuery(Health.StunComponent, CGF.GameObject)
    def onStunComponentAdded(self, _, go):
        vehicle = sound_helpers.getVehicle(go, self.spaceID)
        if self.__isBossImpulse():
            if wt_helpers.isBoss() and not wt_helpers.isBossTeam(vehicle) and not self.__stunImpulseIsPlaying:
                self.__stunImpulseIsPlaying = True
                sound_helpers.playNotification(self._PLAYER_BOSS_STUN_IMPULSE)
            elif wt_helpers.isPlayerVehicle(vehicle):
                sound_helpers.playVehicleSound(self._PLAYER_HUNTER_STUN_EMI_START, vehicle)
                self.__isPlayerStunEMI = True
        elif wt_helpers.isBoss() and not wt_helpers.isBossTeam(vehicle):
            sound_helpers.playNotification(self._PLAYER_BOSS_STUN)
        elif wt_helpers.isPlayerVehicle(vehicle):
            sound_helpers.playNotification(self._PLAYER_HUNTER_STUN_SHELL)
            sound_helpers.playVehicleSound(self._PLAYER_HUNTER_STUN_3D, vehicle)
            self.__isPlayerStun3D = True

    @onRemovedQuery(Health.StunComponent, CGF.GameObject)
    def onStunComponentRemoved(self, _, go):
        vehicle = sound_helpers.getVehicle(go, self.spaceID)
        if self.__stunImpulseIsPlaying and wt_helpers.isBoss() and self.__isBossImpulse():
            self.__stunImpulseIsPlaying = False
        if self.__isPlayerStun3D:
            sound_helpers.playVehicleSound(self._PLAYER_HUNTER_STUN_3D_STOP, vehicle)
            self.__isPlayerStun3D = False
        if self.__isPlayerStunEMI:
            sound_helpers.playVehicleSound(self._PLAYER_HUNTER_STUN_EMI_END, vehicle)
            self.__isPlayerStunEMI = False

    def __isBossImpulse(self):
        bossVehicle = wt_helpers.getBossVehicle()
        if bossVehicle is None:
            return False
        else:
            impulseEquip = bossVehicle.dynamicComponents.get('builtinImpulse_wt')
            return False if impulseEquip is None else impulseEquip.equipmentStatePublic['stage'] == EQUIPMENT_STAGES.COOLDOWN


class ShootingSoundManager(CGF.ComponentManager):
    _SHOOTING_NPC_3D = {'R97_Object_140': 'ev_white_tiger_wpn_hunters_01_npc',
     'F18_Bat_Chatillon25t': 'ev_white_tiger_wpn_hunters_02_npc',
     'A120_M48A5': 'ev_white_tiger_wpn_hunters_02_npc',
     'Cz04_T50_51_Waf_Hound_3DSt': 'ev_white_tiger_wpn_hunters_01_npc',
     'G98_Waffentrager_E100_TL': 'ev_white_tiger_wpn_waffentrager_npc'}
    _LARGE_WEAPON_HUNTERS = {'france:F18_Bat_Chatillon25t_hound_TLXXL', 'usa:A120_M48A5_hound_TLXXL'}
    _EVENT_LARGE_WPN_HUNTER_SOUND = 'ev_white_tiger_wpn_hunters_02_pc'

    @onAddedQuery(Projectiles.ShotsDoneComponent, CGF.GameObject)
    def onShotComponentAdded(self, _, go):
        vehicle = sound_helpers.getVehicle(go, self.spaceID)
        if vehicle is None:
            return
        else:
            if not wt_helpers.isPlayerVehicle(vehicle):
                vehicleName = vehicle.typeDescriptor.name
                value = findFirst(lambda i: i[0] in vehicleName, self._SHOOTING_NPC_3D.items())
                if value is not None:
                    sound_helpers.playVehiclePart(value[1], vehicle, TankSoundObjectsIndexes.GUN)
            else:
                vehicleName = vehicle.typeDescriptor.name
                if vehicleName in self._LARGE_WEAPON_HUNTERS:
                    sound_helpers.playVehiclePart(self._EVENT_LARGE_WPN_HUNTER_SOUND, vehicle, TankSoundObjectsIndexes.GUN)
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
    _GAMEPLAY_ENTER = 'ev_white_tiger_gameplay_enter'
    _WT23_VO_PREBATTLE_DIALOGUE = 'wt23_vo_dialogue_prebattle'
    _PREBATTLE_DIALOGUE_START_TIME = 23.0

    def __init__(self):
        super(GameplayEnterSoundPlayer, self).__init__()
        CallbackDelayer.__init__(self)
        self.__prevPeriod = None
        return

    def activate(self):
        arena = getattr(BigWorld.player(), 'arena', None)
        if arena is not None:
            arena.onPeriodChange += self.__onArenaPeriodChange
        return

    def deactivate(self):
        self.clearCallbacks()
        arena = getattr(BigWorld.player(), 'arena', None)
        if arena is not None:
            arena.onPeriodChange -= self.__onArenaPeriodChange
        return

    def __onArenaPeriodChange(self, *args):
        period, periodEndTime, _, _ = args
        if period == ARENA_PERIOD.PREBATTLE:
            PlayerExperienceSwitchManager.increaseBattleCount()
            if wt_helpers.isBoss():
                timeToPeriodEnd = max(periodEndTime - BigWorld.serverTime(), 0.0)
                if timeToPeriodEnd > self._PREBATTLE_DIALOGUE_START_TIME:
                    notificationDelay = max(timeToPeriodEnd - self._PREBATTLE_DIALOGUE_START_TIME, 0.0)
                    self.delayCallback(notificationDelay, self.__playPrebattleDialogue)
        if period != self.__prevPeriod and period == ARENA_PERIOD.BATTLE:
            sound_helpers.play2d(self._GAMEPLAY_ENTER)
        self.__prevPeriod = period

    def __playPrebattleDialogue(self):
        sound_helpers.playNotification(self._WT23_VO_PREBATTLE_DIALOGUE)
