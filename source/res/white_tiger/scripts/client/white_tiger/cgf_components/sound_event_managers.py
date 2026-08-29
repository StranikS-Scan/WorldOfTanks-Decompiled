# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/cgf_components/sound_event_managers.py
from __future__ import absolute_import, division
from future.utils import listitems
import BigWorld
import CGF
import WWISE
import GenericComponents
import Statuses
import InstantStatuses
from constants import ARENA_PERIOD, ATTACK_REASON, ATTACK_REASONS, IS_CLIENT
from shared_utils import findFirst
from white_tiger.cgf_components.sound_helper_components import WTGeneratorEmerging, WTMinibossImpulse, WTStunnedByBoss, WTBossImpulse, WTHarrierRespawnComponent
from white_tiger.gui import white_tiger_account_settings
from white_tiger.skeletons.white_tiger_spawn_listener import ISpawnListener
from vehicle_systems.tankStructure import TankSoundObjectsIndexes
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from helpers.CallbackDelayer import CallbackDelayer
from white_tiger.cgf_components import PlayerVehicleTag, wt_sound_helpers, wt_helpers
from white_tiger_common.wt_constants import WT_GENERATOR_MAX_PROGRESS
from WhiteTigerComponents import WTGeneratorProgressComponent
from white_tiger.gui.white_tiger_account_settings import AccountSettingsKeys
if IS_CLIENT:
    from Vehicle import Vehicle
    from white_tiger.cgf_components.generator_components import WTGeneratorCapturedComponent
else:

    class Vehicle(object):
        pass


    class WTGeneratorCapturedComponent(object):
        pass


def getAllSwitches(wtVehicleName=None):
    allSwitches = {}
    for switch in (WTLanguageSwitchSystem.getLanguageSwitch(), WTLanguageSwitchSystem.getVehicleSwitch(wtVehicleName)):
        allSwitches.update(switch)

    return allSwitches


class WTLanguageSwitchSystem(CGF.System):
    _NAME = wt_sound_helpers.SWITCH_LANG_NAME
    Reactions = CGF.Reactions()

    def onMappingLoaded(self):
        wt_sound_helpers.setLanguageSwitch()

    @classmethod
    def getSwitchGroupName(cls):
        return cls._NAME

    @classmethod
    def getLanguageSwitch(cls):
        return {cls._NAME: wt_sound_helpers.getLanguageValue()}


class WTBattleCountManager(object):
    _BATTLE_COUNT_SETTINGS = {False: AccountSettingsKeys.WT_BATTLES_DONE_HUNTER,
     True: AccountSettingsKeys.WT_BATTLES_DONE_BOSS}
    _BATTLE_COUNT_EXPERT = 10

    @classmethod
    def getBattleCount(cls, isBoss):
        settingsFlag = cls._BATTLE_COUNT_SETTINGS.get(isBoss, None)
        if not settingsFlag:
            return 0
        else:
            battleCount = white_tiger_account_settings.getSettings(settingsFlag)
            return battleCount

    @classmethod
    def increaseBattleCount(cls):
        settingsFlag = cls._BATTLE_COUNT_SETTINGS.get(wt_helpers.isBoss(), None)
        if not settingsFlag:
            return
        else:
            battleCount = white_tiger_account_settings.getSettings(settingsFlag)
            white_tiger_account_settings.setSettings(settingsFlag, battleCount + 1)
            return

    @classmethod
    def isExpert(cls, isBoss):
        return True if cls.getBattleCount(isBoss) > cls._BATTLE_COUNT_EXPERT else False


class WTPlayerExperienceSwitchSystem(CGF.System):
    _NAME = 'SWITCH_ext_WT_vo_player_experience'
    _VALUE_BEGINNER = 'SWITCH_ext_WT_vo_player_experience_beginner'
    _VALUE_EXPERT = 'SWITCH_ext_WT_vo_player_experience_expert'
    Reactions = CGF.Reactions()

    def onMappingLoaded(self):
        WWISE.WW_setSwitch(self._NAME, self._getValue())

    @classmethod
    def getSwitchGroupName(cls):
        return cls._NAME

    @classmethod
    def _getValue(cls):
        return cls._VALUE_EXPERT if WTBattleCountManager.isExpert(wt_helpers.isBoss()) else cls._VALUE_BEGINNER


class WTVehicleSwitchSystem(CGF.System):
    _NAME = 'SWITCH_ext_WT_vo_char'
    _VALUES = {'R97_Object_140': 'SWITCH_ext_WT_vo_char_Ob140',
     'F18_Bat_Chatillon25t': 'SWITCH_ext_WT_vo_char_B25t',
     'A120_M48A5': 'SWITCH_ext_WT_vo_char_M48P',
     'Cz04_T50_51_Waf_Hound_3DSt': 'SWITCH_ext_WT_vo_char_TVP',
     'G98_Waffentrager_E100_TLXXL': 'SWITCH_ext_WT_vo_char_WT'}
    PlayerVehicleActivated = CGF.ActivateReaction(CGF.Ro(Vehicle), CGF.ReactRo(PlayerVehicleTag))
    Reactions = CGF.Reactions(PlayerVehicleActivated)

    def update(self):
        for vehicle, _ in self.reaction(self.PlayerVehicleActivated):
            self.onVehicleAdded(vehicle)

    def onVehicleAdded(self, vehicle):
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
            for key, value in cls._VALUES.items():
                if key in vehicleName:
                    return {cls._NAME: value}

            return {}
        else:
            value = cls._getValue(wt_helpers.getPlayerVehicle())
            return {cls._NAME: value} if value is not None else {}

    @classmethod
    def _getValue(cls, vehicle):
        if vehicle is not None:
            vehicleName = vehicle.typeDescriptor.name
            value = findFirst(lambda i: i[0] in vehicleName, listitems(cls._VALUES))
            if value is not None:
                return value[1]
        return


class WTEndBattleSoundSystem(CGF.System):
    _WINNER_WT = 'wt_both_vo_w_win'
    _WINNER_HUNTER = 'wt_both_vo_hunters_win'
    Reactions = CGF.Reactions()

    def onMappingLoaded(self):
        arena = getattr(BigWorld.player(), 'arena', None)
        if arena is not None:
            arena.onPeriodChange += self.__onArenaPeriodChange
        return

    def onMappingUnloaded(self):
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
                    wt_sound_helpers.playNotification(self._WINNER_WT)
                else:
                    wt_sound_helpers.playNotification(self._WINNER_HUNTER)
            elif wt_helpers.isBoss():
                wt_sound_helpers.playNotification(self._WINNER_HUNTER)
            else:
                wt_sound_helpers.playNotification(self._WINNER_WT)


class WTShieldSoundSystem(CGF.System):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _PLAYER_BOSS_SHIELD_ADDED = {False: 'wt23_w_vo_shield_restored',
     True: 'wt23_w_vo_shield_restored_eos_one'}
    _PLAYER_W_HUNTER_SHOOTING_AT_WT_SHIELD = 'wt23_w_vo_shooting_at_wt_shield'
    _PLAYER_BOSS_NO_SHIELD_IMPACT_3D = 'ev_white_tiger_force_field_off'
    HitsReceivedActivated = CGF.ActivateReaction(CGF.GameObject, CGF.ReactRo(InstantStatuses.ProjectileHitsReceivedComponent))
    Reactions = CGF.Reactions(HitsReceivedActivated)

    def update(self):
        for go, _ in self.reaction(self.HitsReceivedActivated):
            self.onShotDamageReceived(go)

    def __init__(self):
        super(WTShieldSoundSystem, self).__init__()
        self.__hasDebuff = False
        self.__arenaPeriod = ARENA_PERIOD.IDLE

    def onMappingLoaded(self):
        self.__hasDebuff = wt_helpers.getHasDebuff()
        arena = getattr(BigWorld.player(), 'arena', None)
        if arena is not None:
            arena.onPeriodChange += self.__onArenaPeriodChange
        battleStateComponent = wt_helpers.getBattleStateComponent()
        if battleStateComponent:
            battleStateComponent.onShieldStatusChange += self.__onShieldStatusChange
        return

    def onMappingUnloaded(self):
        arena = getattr(BigWorld.player(), 'arena', None)
        if arena is not None:
            arena.onPeriodChange -= self.__onArenaPeriodChange
        return

    def __onArenaPeriodChange(self, *args):
        period, _, _, _ = args
        self.__arenaPeriod = period

    def __onShieldStatusChange(self, isShieldDown):
        if self.__arenaPeriod != ARENA_PERIOD.BATTLE:
            return
        else:
            if not isShieldDown and wt_helpers.isBoss():
                notification = self._PLAYER_BOSS_SHIELD_ADDED.get(wt_helpers.isMinibossInArena(), None)
                if notification:
                    wt_sound_helpers.playNotification(notification)
            return

    def onShotDamageReceived(self, go):
        vehicle = wt_sound_helpers.getVehicle(go, self.spaceID)
        if vehicle is not None and wt_helpers.isBossVehicle(vehicle):
            if not wt_helpers.getHasDebuff():
                if wt_helpers.isBoss() and wt_helpers.getBossVehicleHealthPercent() > 3.0:
                    wt_sound_helpers.playNotification(self._PLAYER_W_HUNTER_SHOOTING_AT_WT_SHIELD)
            else:
                wt_sound_helpers.playVehicleSound(self._PLAYER_BOSS_NO_SHIELD_IMPACT_3D, vehicle)
        return


class WTGeneratorCaptureSoundSystem(CGF.System, CallbackDelayer):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _PLAYER_HUNTER_START_CAPTURE = 'wt_hunters_vo_capture_point'
    _PLAYER_BOSS_START_CAPTURE = 'wt23_w_vo_generator_capture'
    _PLAYER_HUNTER_GENERATOR_BLOCKED = 'wt_hunters_vo_generator_blocked'
    _PLAYER_HUNTER_LAST_GENERATOR_DESTROYED = {False: 'wt23_hunters_vo_last_generator_destroyed',
     True: 'wt23_hunters_vo_last_generator_destroyed_player_is_capturer'}
    _PLAYER_HUNTER_GENERATOR_DESTROYED = {False: 'wt23_hunters_vo_shield_destroyed',
     True: 'wt23_hunters_vo_shield_destroyed_player_is_capturer'}
    _PLAYER_BOSS_GENERATOR_BLOCKED = 'wt_w_vo_generator_blocked'
    _PLAYER_BOSS_GENERATOR_DESTROYED = {False: 'wt23_w_vo_shield_destroyed',
     True: 'wt24_w_vo_shield_destroyed_eos_one'}
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
    GeneratorEmergingActivated = CGF.ActivateReaction(CGF.GameObject, CGF.ReactRo(WTGeneratorEmerging))
    GeneratorProgressActivated = CGF.ActivateReaction(CGF.GameObject, CGF.ReactRo(WTGeneratorProgressComponent))
    GeneratorProgressDeactivated = CGF.DeactivateReaction(CGF.GameObject, CGF.ReactRo(WTGeneratorProgressComponent))
    GeneratorProgressIterate = CGF.IterateReaction(CGF.ActiveOnly, CGF.GameObject, CGF.Ro(WTGeneratorProgressComponent))
    GeneratorProgressAccess = CGF.AccessReaction(CGF.Ro(WTGeneratorProgressComponent))
    EntitySyncAccess = CGF.AccessReaction(CGF.Ro(GenericComponents.EntityGOSync))
    TransformAccess = CGF.AccessReaction(CGF.Ro(CGF.TransformComponent))
    GeneratorCaptureAccess = CGF.AccessReaction(CGF.Ro(WTGeneratorCapturedComponent))
    Reactions = CGF.Reactions(GeneratorEmergingActivated, GeneratorProgressActivated, GeneratorProgressDeactivated, GeneratorProgressIterate, GeneratorProgressAccess, EntitySyncAccess, TransformAccess, GeneratorCaptureAccess)

    def update(self):
        q = CGF.CommandQueue(self.gom)
        generatorCaptureAccess = self.reaction(self.GeneratorCaptureAccess)
        entitySyncAccess = self.reaction(self.EntitySyncAccess)
        for go, _ in self.reaction(self.GeneratorProgressDeactivated):
            self.onGeneratorProgressComponentRemoved(go, q, generatorCaptureAccess, entitySyncAccess)

        generatorProgressAccess = self.reaction(self.GeneratorProgressAccess)
        transformAccess = self.reaction(self.TransformAccess)
        for go, _ in self.reaction(self.GeneratorEmergingActivated):
            self.onGeneratorEmerging(go, generatorProgressAccess, entitySyncAccess, transformAccess)

        for go, _ in self.reaction(self.GeneratorProgressActivated):
            self.onGeneratorProgressComponentAdded(go, entitySyncAccess, transformAccess)

        for go, progressComponent in self.reaction(self.GeneratorProgressIterate):
            self.onProcessGeneratorProgressComponent(go, progressComponent)

    def __init__(self):
        super(WTGeneratorCaptureSoundSystem, self).__init__()
        CallbackDelayer.__init__(self)
        self.__capturedIDs = None
        return

    def onMappingLoaded(self):
        battleStateComponent = wt_helpers.getBattleStateComponent()
        if battleStateComponent:
            battleStateComponent.onGeneratorLocked += self.__onGeneratorLocked
            battleStateComponent.onGeneratorDestroyed += self.__onGeneratorDestroyed

    def onMappingUnloaded(self):
        self.clearCallbacks()
        for soundObject in self._soundObjects.values():
            soundObject.stopAll()

        self._soundObjects.clear()
        self._entityIDs.clear()
        self.__entityIdBlockedGenerator = None
        return

    def onGeneratorEmerging(self, go, generatorProgressAccess, entitySyncAccess, transformAccess):
        parent = self.__getParentGO(go)
        progressComp = generatorProgressAccess.find(parent)
        if progressComp:
            return
        goSyncComponent = entitySyncAccess.find(parent)
        entityID = goSyncComponent.entity.id
        if entityID not in self._soundObjects:
            soundObjectName = self._soundObjectName + str(entityID)
            transform = transformAccess.find(parent)
            position = transform.worldPosition
            self._soundObjects[entityID] = wt_sound_helpers.createSoundObject(soundObjectName, position)
            self._soundObjects[entityID].play(self._GENERATOR_EMERGING_3D)
        else:
            self.__playSound(entityID, self._GENERATOR_EMERGING_3D)

    def onGeneratorProgressComponentAdded(self, go, entitySyncAccess, transformAccess):
        parent = self.__getParentGO(go)
        transform = transformAccess.find(parent)
        position = transform.worldPosition
        goSyncComponent = entitySyncAccess.find(parent)
        entityID = goSyncComponent.entity.id
        notification = self._PLAYER_HUNTER_START_CAPTURE
        if wt_helpers.isBoss():
            notification = self._PLAYER_BOSS_START_CAPTURE
        distToGenerator = wt_sound_helpers.getPlayerVehicleDistToGO(self.spaceID, position)
        triggerDist = float(wt_sound_helpers.getEventInfo(notification, 'infDist'))
        if distToGenerator <= triggerDist and entityID != self.__entityIdBlockedGenerator:
            wt_sound_helpers.playNotification(notification)
        self._entityIDs[go.uuid] = entityID
        if entityID not in self._soundObjects:
            soundObjectName = self._soundObjectName + str(entityID)
            self._soundObjects[entityID] = wt_sound_helpers.createSoundObject(soundObjectName, position)
        self.__playSound(entityID, self._GENERATOR_CAPTURE_START_3D)

    def onProcessGeneratorProgressComponent(self, go, progressComponent):
        progressPercent = 100 * progressComponent.progress / WT_GENERATOR_MAX_PROGRESS
        self.__setRTPC(go, progressPercent)

    def onGeneratorProgressComponentRemoved(self, go, queue, generatorCaptureAccess, entitySyncAccess):
        entityID = self.__getEntityIDFromGO(go, entitySyncAccess)
        capturedComponent = generatorCaptureAccess.find(go)
        if capturedComponent is not None:
            self.__playSound(entityID, self._GENERATOR_CAPTURED_3D)
            self.delayCallback(self._GENERATOR_CAPTURED_3D_SOUND_LENGTH, self.__removeSoundObject, entityID)
            self.__capturedIDs = capturedComponent.vehiclesIDs
            queue.removeComponent(go, WTGeneratorCapturedComponent)
        else:
            self.__playSound(entityID, self._GENERATOR_CAPTURE_FAILED_3D)
        if go.uuid in self._entityIDs:
            self._entityIDs.pop(go.uuid)
        return

    def __onGeneratorLocked(self, _, isLocked, entityID, isInit, areGeneratorsLocked):
        if isInit:
            return
        else:
            if not areGeneratorsLocked:
                if isLocked:
                    self.__playSound(entityID, self._GENERATOR_BLOCKED_3D)
                    self.__entityIdBlockedGenerator = entityID
                    if wt_helpers.isBoss():
                        wt_sound_helpers.playNotification(self._PLAYER_BOSS_GENERATOR_BLOCKED)
                    else:
                        wt_sound_helpers.playNotification(self._PLAYER_HUNTER_GENERATOR_BLOCKED)
                elif self.__entityIdBlockedGenerator:
                    self.__entityIdBlockedGenerator = None
                    if entityID in self._entityIDs.values():
                        self.__playSound(entityID, self._GENERATOR_CAPTURE_START_3D)
            return

    def __playSound(self, entityID, soundID):
        if entityID in self._soundObjects:
            if self.__entityIdBlockedGenerator != entityID:
                self._soundObjects[entityID].play(soundID)

    def __setRTPC(self, go, valueRTPC):
        entityID = self._entityIDs.get(go.uuid)
        if entityID is not None and entityID in self._soundObjects:
            self._soundObjects[entityID].setRTPC(self._GENERATOR_CAPTURE_RTCP, valueRTPC)
        return

    def __removeSoundObject(self, entityID):
        if entityID in self._soundObjects:
            self._soundObjects[entityID].stopAll()
            self._soundObjects.pop(entityID)

    def __getEntityIDFromGO(self, go, entitySyncAccess):
        parent = self.__getParentGO(go)
        goSyncComponent = entitySyncAccess.find(parent)
        try:
            if goSyncComponent and goSyncComponent.entity is not None:
                entityID = goSyncComponent.entity.id
                return entityID
        except TypeError:
            pass

        return

    def __getParentGO(self, go):
        return self.hierarchy.getTopMostParent(go)

    def __onGeneratorDestroyed(self, generatorsLeft):
        period = self.__sessionProvider.arenaVisitor.getArenaPeriod()
        if period != ARENA_PERIOD.BATTLE:
            return
        else:
            isBoss = wt_helpers.isBoss()
            notification = None
            isCapturer = self.__playerIsCapturer()
            if generatorsLeft == 0:
                if isBoss:
                    notification = self._PLAYER_BOSS_LAST_GENERATOR_DESTROYED
                else:
                    notification = self._PLAYER_HUNTER_LAST_GENERATOR_DESTROYED.get(isCapturer, None)
            elif isBoss:
                notification = self._PLAYER_BOSS_GENERATOR_DESTROYED.get(wt_helpers.isMinibossInArena(), None)
            else:
                notification = self._PLAYER_HUNTER_GENERATOR_DESTROYED.get(isCapturer, None)
            if notification:
                wt_sound_helpers.playNotification(notification)
            self.__capturedIDs = None
            return

    def __playerIsCapturer(self):
        return BigWorld.player().vehicle.id in self.__capturedIDs if self.__capturedIDs and BigWorld.player().vehicle else False


class WTVehicleKilledSoundSystem(CGF.System):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _PLAYER_HUNTER_VEHICLE_DESTROYED = ('wt_hunters_vo_vehicle_destroyed', 'wt_krieger_vo_wt_enemy_killed')
    _BOSS_DESTROYED_PC_3D = 'ev_white_tiger_wt_escape_pc'
    _BOSS_DESTROYED_NPC_3D = 'ev_white_tiger_wt_escape_npc'
    _BOSS_DESTROYED = 'vehicle_destroyed'
    Reactions = CGF.Reactions()

    def onMappingLoaded(self):
        arena = getattr(BigWorld.player(), 'arena', None)
        if arena is not None:
            arena.onVehicleKilled += self.__onArenaVehicleKilled
        return

    def onMappingUnloaded(self):
        arena = getattr(BigWorld.player(), 'arena', None)
        if arena is not None:
            arena.onVehicleKilled -= self.__onArenaVehicleKilled
        return

    def __onArenaVehicleKilled(self, *args):
        vId, _, _, reason, _ = args
        bossVehicle = wt_helpers.getBossVehicle()
        if bossVehicle is not None and bossVehicle.id == vId:
            if wt_helpers.isBoss():
                wt_sound_helpers.play3d(self._BOSS_DESTROYED_PC_3D, bossVehicle.entityGameObject, self.spaceID)
                if reason == ATTACK_REASONS.index(ATTACK_REASON.DROWNING):
                    wt_sound_helpers.playNotification(self._BOSS_DESTROYED)
            else:
                wt_sound_helpers.play3d(self._BOSS_DESTROYED_NPC_3D, bossVehicle.entityGameObject, self.spaceID)
        elif BigWorld.player().vehicle and BigWorld.player().vehicle.id == vId:
            for notification in self._PLAYER_HUNTER_VEHICLE_DESTROYED:
                wt_sound_helpers.playNotification(notification)

        return


class WTBossAbilitySoundSystem(CGF.System):
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
    MinibossImpulseDeactivated = CGF.DeactivateReaction(CGF.ReactRo(WTMinibossImpulse))
    StunDeactivated = CGF.DeactivateReaction(CGF.GameObject, CGF.ReactRo(Statuses.StunComponent))
    MinibossImpulseActivated = CGF.ActivateReaction(CGF.ReactRo(WTMinibossImpulse))
    StunnedByBossActivated = CGF.ActivateReaction(CGF.GameObject, CGF.ReactRo(WTStunnedByBoss))
    StunActivated = CGF.ActivateReaction(CGF.GameObject, CGF.ReactRo(Statuses.StunComponent))
    BossImpulseAccess = CGF.AccessReaction(CGF.Ro(WTBossImpulse))
    Reactions = CGF.Reactions(MinibossImpulseDeactivated, StunDeactivated, MinibossImpulseActivated, StunnedByBossActivated, StunActivated, BossImpulseAccess)

    def update(self):
        for _ in self.reaction(self.MinibossImpulseDeactivated):
            self.onMinibossImpulseRemoved()

        for go, _ in self.reaction(self.StunDeactivated):
            self.onStunComponentRemoved(go)

        for _ in self.reaction(self.MinibossImpulseActivated):
            self.onMinibossImpulseAdded()

        bossImpulseAccess = self.reaction(self.BossImpulseAccess)
        for go, _ in self.reaction(self.StunnedByBossActivated):
            self.onStunnedByBossAdded(go, bossImpulseAccess)

        for go, _ in self.reaction(self.StunActivated):
            self.onStunComponentAdded(go, bossImpulseAccess)

    def __init__(self):
        super(WTBossAbilitySoundSystem, self).__init__()
        self.__isPlayerStun = False
        self.__isPlayerStunEMI = False
        self.__stunNotificationPlayed = False
        self.__isMinibossImpulse = False

    def onMappingLoaded(self):
        self.__isPlayerStun = False
        self.__isPlayerStunEMI = False
        self.__isMinibossImpulse = False

    def onMappingUnloaded(self):
        self.__stunNotificationPlayed = False
        if self.__isPlayerStun:
            wt_sound_helpers.play2d(self._PLAYER_HUNTER_STUN_2D_STOP)
            self.__isPlayerStun = False
        if self.__isPlayerStunEMI:
            wt_sound_helpers.play2d(self._PLAYER_HUNTER_STUN_EMI_2D_END)
            self.__isPlayerStunEMI = False

    def onMinibossImpulseAdded(self):
        self.__isMinibossImpulse = True

    def onMinibossImpulseRemoved(self):
        self.__isMinibossImpulse = False

    def onStunnedByBossAdded(self, go, bossImpulseAccess):
        vehicle = wt_sound_helpers.getVehicle(go, self.spaceID)
        self.__onStunnedByBossNotification(vehicle, bossImpulseAccess)

    def onStunComponentAdded(self, go, bossImpulseAccess):
        vehicle = wt_sound_helpers.getVehicle(go, self.spaceID)
        if not wt_helpers.isPlayerVehicle(vehicle):
            return
        wt_sound_helpers.play2d(self._PLAYER_HUNTER_STUN_POWER_DOWN_2D)
        if self.__isBossImpulse(bossImpulseAccess) or self.__isMinibossImpulse:
            wt_sound_helpers.play2d(self._PLAYER_HUNTER_STUN_EMI_2D_START)
            self.__isPlayerStunEMI = True
        else:
            wt_sound_helpers.play2d(self._PLAYER_HUNTER_STUN_2D)
            self.__isPlayerStun = True

    def onStunComponentRemoved(self, go):
        self.__stunNotificationPlayed = False
        vehicle = wt_sound_helpers.getVehicle(go, self.spaceID)
        if not wt_helpers.isPlayerVehicle(vehicle):
            return
        wt_sound_helpers.play2d(self._PLAYER_HUNTER_STUN_POWER_UP_2D)
        if self.__isPlayerStunEMI:
            wt_sound_helpers.play2d(self._PLAYER_HUNTER_STUN_EMI_2D_END)
            self.__isPlayerStunEMI = False
        if self.__isPlayerStun:
            wt_sound_helpers.play2d(self._PLAYER_HUNTER_STUN_2D_STOP)
            self.__isPlayerStun = False

    def __onStunnedByBossNotification(self, vehicle, bossImpulseAccess):
        if self.__isBossImpulse(bossImpulseAccess):
            if wt_helpers.isBoss() and not self.__stunNotificationPlayed:
                wt_sound_helpers.playNotification(self._PLAYER_BOSS_STUN_IMPULSE)
                self.__stunNotificationPlayed = True
            elif wt_helpers.isPlayerVehicle(vehicle):
                wt_sound_helpers.playNotification(self._PLAYER_HUNTER_STUN_SHELL)
        elif wt_helpers.isBoss():
            wt_sound_helpers.playNotification(self._PLAYER_BOSS_STUN)
        elif wt_helpers.isPlayerVehicle(vehicle):
            wt_sound_helpers.playNotification(self._PLAYER_HUNTER_STUN_SHELL)

    def __isBossImpulse(self, bossImpulseAccess):
        bossVehicle = wt_helpers.getBossVehicle()
        if bossVehicle is None:
            return False
        else:
            hasBossImpulse = bossImpulseAccess.find(bossVehicle.entityGameObject) is not None
            return hasBossImpulse


class WTShootingSoundSystem(CGF.System):
    _SHOOTING_NPC_3D = {'R97_Object_140': 'ev_white_tiger_wpn_hunters_01_npc',
     'F18_Bat_Chatillon25t': 'ev_white_tiger_wpn_hunters_02_npc',
     'A120_M48A5': 'ev_white_tiger_wpn_hunters_02_npc',
     'Cz04_T50_51_Waf_Hound_3DSt': 'ev_white_tiger_wpn_hunters_01_npc',
     'G98_Waffentrager_E100_TL': 'ev_white_tiger_wpn_waffentrager_npc'}
    ShotActivated = CGF.ActivateReaction(CGF.GameObject, CGF.ReactRo(InstantStatuses.ShotsDoneComponent))
    Reactions = CGF.Reactions(ShotActivated)

    def update(self):
        for go, _ in self.reaction(self.ShotActivated):
            self.onShotComponentAdded(go)

    def onShotComponentAdded(self, go):
        vehicle = wt_sound_helpers.getVehicle(go, self.spaceID)
        if vehicle is not None and not wt_helpers.isPlayerVehicle(vehicle):
            vehicleName = vehicle.typeDescriptor.name
            value = findFirst(lambda i: i[0] in vehicleName, listitems(self._SHOOTING_NPC_3D))
            if value is not None:
                wt_sound_helpers.playVehiclePart(value[1], vehicle, TankSoundObjectsIndexes.GUN)
        return


class WTHarrierRespawnSoundSystem(CGF.System):
    _SPAWN_HUNTER_3D = 'ev_white_tiger_spawn_hunters'
    HarrierRespawnActivated = CGF.ActivateReaction(CGF.GameObject, CGF.ReactRo(WTHarrierRespawnComponent))
    Reactions = CGF.Reactions(HarrierRespawnActivated)

    def update(self):
        for go, _ in self.reaction(self.HarrierRespawnActivated):
            self.onHarrierRespawnComponentAdded(go)

    def onHarrierRespawnComponentAdded(self, go):
        vehicle = wt_sound_helpers.getVehicle(go, self.spaceID)
        if vehicle is not None and not wt_helpers.isBossVehicle(vehicle):
            wt_sound_helpers.playVehicleSound(self._SPAWN_HUNTER_3D, vehicle)
        return


class WTRespawnSoundPlayer(ISpawnListener):
    _RESPAWN_VIEW_SHOW = 'ev_white_tiger_waiting_overlay_ambient'
    _RESPAWN_VIEW_HIDE = 'ev_white_tiger_waiting_overlay_ambient_stop'

    def showSpawnPoints(self):
        wt_sound_helpers.play2d(self._RESPAWN_VIEW_SHOW)

    def closeSpawnPoints(self):
        wt_sound_helpers.play2d(self._RESPAWN_VIEW_HIDE)


class WTGameplayEnterSoundPlayer(CGF.System):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _GAMEPLAY_ENTER = 'ev_white_tiger_gameplay_enter'
    _GAMEPLAY_EXIT = 'ev_white_tiger_gameplay_exit'
    Reactions = CGF.Reactions()

    def __init__(self):
        super(WTGameplayEnterSoundPlayer, self).__init__()
        self.__enterSoundPlayed = False

    def onMappingLoaded(self):
        arenaPeriod = self.__sessionProvider.shared.arenaPeriod.getPeriod()
        if arenaPeriod == ARENA_PERIOD.BATTLE:
            self.__playEnterSound()
        arena = getattr(BigWorld.player(), 'arena', None)
        if arena is not None:
            arena.onPeriodChange += self.__onArenaPeriodChange
        return

    def onMappingUnloaded(self):
        self.__playExitSound()
        arena = getattr(BigWorld.player(), 'arena', None)
        if arena is not None:
            arena.onPeriodChange -= self.__onArenaPeriodChange
        return

    def __onArenaPeriodChange(self, *args):
        period, _, _, _ = args
        if period == ARENA_PERIOD.PREBATTLE:
            WTBattleCountManager.increaseBattleCount()
        if period == ARENA_PERIOD.BATTLE:
            self.__playEnterSound()
        if period == ARENA_PERIOD.AFTERBATTLE:
            self.__playExitSound()

    def __playEnterSound(self):
        wt_sound_helpers.play2d(self._GAMEPLAY_ENTER)
        self.__enterSoundPlayed = True

    def __playExitSound(self):
        if self.__enterSoundPlayed:
            wt_sound_helpers.play2d(self._GAMEPLAY_EXIT)
            self.__enterSoundPlayed = False


class WTOvertimeSoundPlayer(CGF.System):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _WT_OVERTIME_BOSS_SOUND_NOTIFICATION = 'wt23_w_vo_overtime'
    _WT_OVERTIME_HUNTER_SOUND_NOTIFICATION = 'wt23_hunters_vo_overtime'
    Reactions = CGF.Reactions()

    def onMappingLoaded(self):
        overTimeComp = getattr(self.__sessionProvider.arenaVisitor.getComponentSystem(), 'overtimeComponent', None)
        if overTimeComp is not None:
            overTimeComp.onOvertimeStart += self.__onOvertimeStart
        return

    def onMappingUnloaded(self):
        overTimeComp = getattr(self.__sessionProvider.arenaVisitor.getComponentSystem(), 'overtimeComponent', None)
        if overTimeComp is not None:
            overTimeComp.onOvertimeStart -= self.__onOvertimeStart
        return

    def __onOvertimeStart(self, _):
        if wt_helpers.isBoss():
            wt_sound_helpers.playNotification(self._WT_OVERTIME_BOSS_SOUND_NOTIFICATION)
        else:
            wt_sound_helpers.playNotification(self._WT_OVERTIME_HUNTER_SOUND_NOTIFICATION)
