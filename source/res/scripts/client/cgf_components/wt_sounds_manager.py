# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/wt_sounds_manager.py
import BigWorld
import CGF
import WWISE
import ArenaComponents
import Health
import Projectiles
from constants import CURRENT_REALM, IS_CHINA, ARENA_PERIOD, ATTACK_REASON, ATTACK_REASONS
from shared_utils import findFirst
from Vehicle import Vehicle, SpawnComponent
from cgf_script.managers_registrator import onAddedQuery, onRemovedQuery, onProcessQuery
from cgf_components import wt_helpers, sound_helpers, PlayerVehicleTag
from gui.battle_control.controllers.spawn_ctrl import ISpawnListener
from vehicle_systems.tankStructure import TankSoundObjectsIndexes
from Generator import GeneratorCapturedComponent
from BombPickUp import BombPickUpComponent
import Generator
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

def getAllSwitches():
    allSwitches = {}
    for switch in (LanguageSwitchManager.getLanguageSwitch(), VehicleSwitchManager.getVehicleSwitch()):
        allSwitches.update(switch)

    return allSwitches


class LanguageSwitchManager(CGF.ComponentManager):
    _NAME = 'SWITCH_ext_WT_vo_language'
    _RU_REALMS = ('DEV', 'QA', 'RU')
    _VALUE_RU = 'SWITCH_ext_WT_vo_language_RU'
    _VALUE_NON_RU = 'SWITCH_ext_WT_vo_language_nonRU'
    _VALUE_CN = 'SWITCH_ext_WT_vo_language_CN'

    def activate(self):
        WWISE.WW_setSwitch(self._NAME, self._getValue())

    @classmethod
    def getLanguageSwitch(cls):
        return {cls._NAME: cls._getValue()}

    @classmethod
    def _getValue(cls):
        if IS_CHINA:
            return cls._VALUE_CN
        return cls._VALUE_RU if CURRENT_REALM in cls._RU_REALMS else cls._VALUE_NON_RU


class VehicleSwitchManager(CGF.ComponentManager):
    _NAME = 'SWITCH_ext_WT_vo_char'
    _VALUES = {'R97_Object_140': 'SWITCH_ext_WT_vo_char_Ob140',
     'F18_Bat_Chatillon25t': 'SWITCH_ext_WT_vo_char_B25t',
     'A120_M48A5': 'SWITCH_ext_WT_vo_char_M48P',
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
    _PLAYER_BOSS_WIN = ('wt_w_vo_win',)
    _PLAYER_HUNTER_WIN = ('wt_hunters_vo_win', 'wt_krieger_vo_wt_lose')
    _PLAYER_HUNTER_DEFEAT = ('wt_krieger_vo_wt_win',)
    _GAMEPLAY_EXIT = 'ev_white_tiger_gameplay_exit'

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
                notifications = self._PLAYER_BOSS_WIN if wt_helpers.isBoss() else self._PLAYER_HUNTER_WIN
            else:
                notifications = () if wt_helpers.isBoss() else self._PLAYER_HUNTER_DEFEAT
            for notification in notifications:
                sound_helpers.playNotification(notification)

            sound_helpers.play2d(self._GAMEPLAY_EXIT)


class FolloweeSoundManager(CGF.ComponentManager):
    _PLAYER_BOSS_BOMB_TAKEN_BY_HUNTERS = 'wt_w_vo_loot_taken_by_enemy'
    _PLAYER_HUNTER_BOMB_TAKEN_BY_HUNTERS = 'wt_hunters_vo_loot_taken_by_ally'
    _BOMB_TAKEN_PC_3D = ('ev_white_tiger_gain_energy_complete_pc', 'ev_white_tiger_gain_energy_on_board')
    _BOMB_TAKEN_NPC_3D = ('ev_white_tiger_gain_energy_complete_npc', 'ev_white_tiger_gain_energy_on_board')
    _BOMB_LOSE_3D = 'ev_white_tiger_gain_energy_off_board'

    @onAddedQuery(ArenaComponents.CarryingLootComponent, CGF.GameObject)
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

    @onRemovedQuery(ArenaComponents.CarryingLootComponent, CGF.GameObject)
    def onCarryingLootRemoved(self, _, go):
        vehicle = sound_helpers.getVehicle(go, self.spaceID)
        if vehicle is not None:
            sound_helpers.playVehicleSound(self._BOMB_LOSE_3D, vehicle)
        return


class CaptureLootSoundManager(CGF.ComponentManager):
    _PLAYER_START_CAPTURE = 'ev_white_tiger_gain_energy_start'
    _PLAYER_STOP_CAPTURE = 'ev_white_tiger_gain_energy_stop'

    @onAddedQuery(BombPickUpComponent, PlayerVehicleTag)
    def onCaptureAdded(self, *_):
        sound_helpers.play2d(self._PLAYER_START_CAPTURE)

    @onRemovedQuery(BombPickUpComponent, PlayerVehicleTag)
    def onCaptureRemoved(self, *_):
        sound_helpers.play2d(self._PLAYER_STOP_CAPTURE)


class ShieldSoundManager(CGF.ComponentManager):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _PLAYER_BOSS_SHIELD_ADDED = 'wt_w_vo_shield_full'
    _PLAYER_HUNTER_SHIELD_ADDED = 'wt_krieger_vo_shield_full'
    _PLAYER_BOSS_SHIELD_REMOVED = 'wt_w_vo_shield_destroyed'
    _PLAYER_HUNTER_SHIELD_REMOVED = 'wt_krieger_vo_shield_destroyed'
    _PLAYER_BOSS_NO_SHIELD_IMPACT_3D = 'ev_white_tiger_force_field_off'
    _PLAYER_BOSS_SHIELD_IMPACT_3D = 'ev_white_tiger_force_field_on'

    def __init__(self):
        super(ShieldSoundManager, self).__init__()
        self.__hasDebuff = wt_helpers.getHasDebuff()

    def activate(self):
        feedback = self.__sessionProvider.shared.feedback
        if feedback:
            feedback.onArenaTimer += self.__onArenaTimer

    def deactivate(self):
        feedback = self.__sessionProvider.shared.feedback
        if feedback:
            feedback.onArenaTimer -= self.__onArenaTimer

    def __onArenaTimer(self, name, _, remainingTime):
        if name == wt_helpers.WT_SHIELD_DEBUFF_DURATION:
            if remainingTime > 0 and not self.__hasDebuff:
                if wt_helpers.isBoss():
                    sound_helpers.playNotification(self._PLAYER_BOSS_SHIELD_REMOVED)
                else:
                    sound_helpers.playNotification(self._PLAYER_HUNTER_SHIELD_REMOVED)
            elif remainingTime <= 0 and self.__hasDebuff:
                if wt_helpers.isBoss():
                    sound_helpers.playNotification(self._PLAYER_BOSS_SHIELD_ADDED)
                else:
                    sound_helpers.playNotification(self._PLAYER_HUNTER_SHIELD_ADDED)
            self.__hasDebuff = remainingTime > 0

    @onAddedQuery(Projectiles.ProjectileHitsReceivedComponent, CGF.GameObject)
    def onShotDamageReceived(self, _, go):
        vehicle = sound_helpers.getVehicle(go, self.spaceID)
        if vehicle is not None and wt_helpers.isBossVehicle(vehicle):
            if not wt_helpers.getHasDebuff():
                sound_helpers.playVehicleSound(self._PLAYER_BOSS_SHIELD_IMPACT_3D, vehicle)
            else:
                sound_helpers.playVehicleSound(self._PLAYER_BOSS_NO_SHIELD_IMPACT_3D, vehicle)
        return


class GeneratorCaptureSoundManager(CGF.ComponentManager):
    _PLAYER_HUNTER_START_CAPTURE = 'wt_hunters_vo_capture_point'
    _PLAYER_HUNTER_GENERATOR_DESTROYED = 'wt_hunters_vo_generator_destroyed'
    _PLAYER_HUNTER_LAST_GENERATOR_DESTROYED = 'wt_hunters_vo_destruction_last_generator'
    _PLAYER_BOSS_GENERATOR_DESTROYED = 'wt_w_vo_destruction_generator'
    _PLAYER_BOSS_LAST_GENERATOR_DESTROYED = 'wt_w_vo_destruction_last_generator'
    _GENERATOR_CAPTURE_START_3D = 'ev_white_tiger_tower_generator_start_capture'
    _GENERATOR_CAPTURE_FAILED_3D = 'ev_white_tiger_tower_generator_downing_capture'
    _GENERATOR_CAPTURED_3D = 'ev_white_tiger_tower_generator_destruction'
    _GENERATOR_CAPTURE_RTCP = 'RTPC_ext_white_tiger_progress'

    @onAddedQuery(ArenaComponents.GeneratorProgressComponent, CGF.GameObject)
    def onGeneratorCaptureAdded(self, _, go):
        if not wt_helpers.isBoss():
            sound_helpers.playNotification(self._PLAYER_HUNTER_START_CAPTURE)
        sound_helpers.play3d(self._GENERATOR_CAPTURE_START_3D, go, self.spaceID)

    @onProcessQuery(ArenaComponents.GeneratorProgressComponent)
    def onProcessGeneratorCapture(self, progressComponent):
        progressPercent = 100 * progressComponent.progress / Generator.MAX_PROGRESS
        sound_helpers.setRTCP(self._GENERATOR_CAPTURE_RTCP, progressPercent)

    @onRemovedQuery(ArenaComponents.GeneratorProgressComponent, CGF.GameObject)
    def onGeneratorCaptureRemoved(self, _, go):
        isCaptured = go.findComponentByType(GeneratorCapturedComponent) is not None
        if isCaptured:
            sound_helpers.play3d(self._GENERATOR_CAPTURED_3D, go, self.spaceID)
            go.removeComponentByType(GeneratorCapturedComponent)
        else:
            sound_helpers.play3d(self._GENERATOR_CAPTURE_FAILED_3D, go, self.spaceID)
        return

    @onAddedQuery(ArenaComponents.BattleStage, CGF.GameObject)
    def onBattleStageAdded(self, component, go):
        if component.current < component.maximum:
            if component.current == 0:
                if wt_helpers.isBoss():
                    sound_helpers.playNotification(self._PLAYER_BOSS_LAST_GENERATOR_DESTROYED)
                else:
                    sound_helpers.playNotification(self._PLAYER_HUNTER_LAST_GENERATOR_DESTROYED)
            elif wt_helpers.isBoss():
                sound_helpers.playNotification(self._PLAYER_BOSS_GENERATOR_DESTROYED)
            else:
                sound_helpers.playNotification(self._PLAYER_HUNTER_GENERATOR_DESTROYED)


class VehicleKilledSoundManager(CGF.ComponentManager):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _PLAYER_HUNTER_VEHICLE_DESTROYED = ('wt_hunters_vo_vehicle_destroyed', 'wt_krieger_vo_wt_enemy_killed')
    _PLAYER_HUNTER_DEAD = ('wt_hunters_vo_vehicle_dead', 'wt_krieger_vo_wt_enemy_killed')
    _BOSS_DESTROYED_PC_3D = 'ev_white_tiger_wt_escape_pc'
    _BOSS_DESTROYED_NPC_3D = 'ev_white_tiger_wt_escape_npc'
    _BOSS_DESTROYED = 'vehicle_destroyed'

    def __init__(self):
        super(VehicleKilledSoundManager, self).__init__()
        self.__livesNumber = None
        playerLives = wt_helpers.getPlayerLives()
        if not wt_helpers.isBoss() and playerLives > 0:
            self.__livesNumber = playerLives
        return

    def activate(self):
        arena = getattr(BigWorld.player(), 'arena', None)
        if arena is not None:
            arena.onVehicleKilled += self.__onArenaVehicleKilled
        spawnCtrl = self.__sessionProvider.dynamic.spawn
        if spawnCtrl is not None:
            spawnCtrl.onTeamLivesSetted += self.__onTeamLivesSetted
        return

    def deactivate(self):
        arena = getattr(BigWorld.player(), 'arena', None)
        if arena is not None:
            arena.onVehicleKilled -= self.__onArenaVehicleKilled
        spawnCtrl = self.__sessionProvider.dynamic.spawn
        if spawnCtrl is not None:
            spawnCtrl.onTeamLivesSetted -= self.__onTeamLivesSetted
        return

    def __onArenaVehicleKilled(self, vId, killerID, equipmentID, reason):
        bossVehicle = wt_helpers.getBossVehicle()
        if bossVehicle is not None and bossVehicle.id == vId:
            if wt_helpers.isBoss():
                sound_helpers.play3d(self._BOSS_DESTROYED_PC_3D, bossVehicle.entityGameObject, self.spaceID)
                if reason == ATTACK_REASONS.index(ATTACK_REASON.DROWNING):
                    sound_helpers.playNotification(self._BOSS_DESTROYED)
            else:
                sound_helpers.play3d(self._BOSS_DESTROYED_NPC_3D, bossVehicle.entityGameObject, self.spaceID)
        return

    def __onTeamLivesSetted(self):
        if wt_helpers.isBoss():
            return
        else:
            playerLives = wt_helpers.getPlayerLives()
            if self.__livesNumber is None:
                self.__livesNumber = playerLives
                return
            if playerLives == self.__livesNumber:
                return
            self.__livesNumber = playerLives
            notifications = self._PLAYER_HUNTER_DEAD if playerLives == 0 else self._PLAYER_HUNTER_VEHICLE_DESTROYED
            for notification in notifications:
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

    @onAddedQuery(Health.StunComponent, CGF.GameObject)
    def onStunComponentAdded(self, _, go):
        vehicle = sound_helpers.getVehicle(go, self.spaceID)
        if self.__isBossImpulse():
            if wt_helpers.isBoss():
                sound_helpers.playNotification(self._PLAYER_BOSS_STUN_IMPULSE)
            elif wt_helpers.isPlayerVehicle(vehicle):
                sound_helpers.playNotification(self._PLAYER_HUNTER_STUN_IMPULSE)
                sound_helpers.playVehicleSound(self._PLAYER_HUNTER_STUN_EMI_START, vehicle)
                self.__isPlayerStunEMI = True
        elif wt_helpers.isBoss():
            sound_helpers.playNotification(self._PLAYER_BOSS_STUN)
        elif wt_helpers.isPlayerVehicle(vehicle):
            sound_helpers.playNotification(self._PLAYER_HUNTER_STUN_SHELL)
            sound_helpers.playVehicleSound(self._PLAYER_HUNTER_STUN_3D, vehicle)
            self.__isPlayerStun3D = True

    @onRemovedQuery(Health.StunComponent, CGF.GameObject)
    def onStunComponentRemoved(self, _, go):
        vehicle = sound_helpers.getVehicle(go, self.spaceID)
        if self.__isPlayerStun3D:
            sound_helpers.playVehicleSound(self._PLAYER_HUNTER_STUN_3D_STOP, vehicle)
            self.__isPlayerStun3D = False
        if self.__isPlayerStunEMI:
            sound_helpers.playVehicleSound(self._PLAYER_HUNTER_STUN_EMI_END, vehicle)
            self.__isPlayerStunEMI = False

    def __isBossImpulse(self):
        bossVehicle = wt_helpers.getBossVehicle()
        return False if bossVehicle is None else 'impulse_animation' in bossVehicle.dynamicComponents


class ShootingSoundManager(CGF.ComponentManager):
    _SHOOTING_NPC_3D = {'R97_Object_140': 'ev_white_tiger_wpn_hunters_01_npc',
     'F18_Bat_Chatillon25t': 'ev_white_tiger_wpn_hunters_02_npc',
     'A120_M48A5': 'ev_white_tiger_wpn_hunters_02_npc',
     'G98_Waffentrager_E100_TL': 'ev_white_tiger_wpn_waffentrager_npc'}

    @onAddedQuery(Projectiles.ShotsDoneComponent, CGF.GameObject)
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


class GameplayEnterSoundPlayer(CGF.ComponentManager):
    _GAMEPLAY_ENTER = 'ev_white_tiger_gameplay_enter'

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
        period, _, _, _ = args
        if period == ARENA_PERIOD.BATTLE:
            sound_helpers.play2d(self._GAMEPLAY_ENTER)
