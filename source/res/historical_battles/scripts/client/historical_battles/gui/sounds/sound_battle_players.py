# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/sounds/sound_battle_players.py
import BigWorld
import SoundGroups
from items import vehicles
from gui.battle_control.avatar_getter import getSoundNotifications
from constants import ARENA_PERIOD, EQUIPMENT_STAGES
from helpers import dependency, CallbackDelayer
from HBAvatarRespawnComponent import HBAvatarRespawnComponent
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.battle_control.controllers.period_ctrl import IAbstractPeriodView
from gui.battle_control.view_components import IViewComponentsCtrlListener
from historical_battles.gui.battle_control.controllers.equipments import HBDeathZoneItem
from historical_battles.gui.sounds.sound_constants import HBEventGameplayState, HBMusicEvents, HBGameplayVoiceovers, HBUISound, HBBattleEvent
from historical_battles.gui.sounds.sound_static_death_zone import HBStaticDeathZoneSound
from historical_battles_common.hb_constants_extension import ARENA_BONUS_TYPE

def _playSoundNotification(notification, vehicleID=None, checkFn=None, position=None, boundVehicleID=None):
    if not notification:
        return
    else:
        notifications = getSoundNotifications()
        if notifications is not None:
            notifications.play(notification, vehicleID, checkFn, position, boundVehicleID)
        return


class _SoundsPlayer(IAbstractPeriodView, IViewComponentsCtrlListener):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(_SoundsPlayer, self).__init__()
        self.__isInitialized = False
        self.__delayer = None
        self.__staticDeathZoneSound = None
        return

    @property
    def soundDelayer(self):
        return self.__delayer

    def detachedFromCtrl(self, ctrlID):
        self._finalize()

    def setPeriod(self, period):
        if period == ARENA_PERIOD.BATTLE and not self.__isInitialized:
            self._initialize()
            self.__playStartBattleSounds()
        elif period == ARENA_PERIOD.AFTERBATTLE:
            self._finalize()
        elif period == ARENA_PERIOD.PREBATTLE:
            self.__staticDeathZoneSound = HBStaticDeathZoneSound()
            self.__setPrebattleSoundState()

    def _initialize(self):
        self.__isInitialized = True
        self.__delayer = CallbackDelayer.CallbacksSetByID()
        vehicleCtrl = self.sessionProvider.shared.vehicleState
        if vehicleCtrl:
            vehicleCtrl.onRespawnBaseMoving += self.__onRespawnBaseMoving

    def _finalize(self):
        self.__isInitialized = False
        if self.__delayer:
            self.__delayer.clear()
        if self.__staticDeathZoneSound:
            self.__staticDeathZoneSound.destroy()
            self.__staticDeathZoneSound = None
        vehicleCtrl = self.sessionProvider.shared.vehicleState
        if vehicleCtrl:
            vehicleCtrl.onRespawnBaseMoving -= self.__onRespawnBaseMoving
        self.__setAfterbattleSoundState()
        return

    def __playStartBattleSounds(self):
        if BigWorld.player().arena.bonusType == ARENA_BONUS_TYPE.HB_OFFENCE:
            SoundGroups.g_instance.playSound2D(HBMusicEvents.OFFENCE_MUSIC)
        else:
            SoundGroups.g_instance.playSound2D(HBMusicEvents.DEFENCE_MUSIC)

    def __setPrebattleSoundState(self):
        SoundGroups.g_instance.setState(HBEventGameplayState.GROUP, HBEventGameplayState.ON)
        SoundGroups.g_instance.playSound2D(HBBattleEvent.ENTER)

    def __setAfterbattleSoundState(self):
        SoundGroups.g_instance.playSound2D(HBBattleEvent.EXIT)
        SoundGroups.g_instance.setState(HBEventGameplayState.GROUP, HBEventGameplayState.OFF)

    def __onRespawnBaseMoving(self):
        avatarComponent = BigWorld.player().HBAvatarRespawnComponent
        lives = avatarComponent.getAliveVehicleCount()
        if lives != 0:
            _playSoundNotification(HBGameplayVoiceovers.PLAYER_RESPAWN)
        else:
            _playSoundNotification(HBGameplayVoiceovers.LAST_PLAYER_RESPAWN)


class EquipmentSoundPlayer(_SoundsPlayer):

    def __init__(self):
        super(EquipmentSoundPlayer, self).__init__()
        self.__isNitroSoundPlaying = False

    def _initialize(self):
        self.__deathZoneSoundPlayed = False
        super(EquipmentSoundPlayer, self)._initialize()
        ctrl = self.sessionProvider.shared.equipments
        if ctrl is not None:
            ctrl.onEquipmentUpdated += self.__onEquipmentUpdated
            ctrl.onCombatEquipmentUsed += self.__onCombatEquipmentUsed
            ctrl.onEquipmentMarkerShown += self.__onEquipmentMarkerShown
        HBAvatarRespawnComponent.onDeath += self.__onVehicleDestroyed
        return

    def _finalize(self):
        ctrl = self.sessionProvider.shared.equipments
        if ctrl is not None:
            ctrl.onEquipmentUpdated -= self.__onEquipmentUpdated
            ctrl.onCombatEquipmentUsed -= self.__onCombatEquipmentUsed
            ctrl.onEquipmentMarkerShown -= self.__onEquipmentMarkerShown
        HBAvatarRespawnComponent.onDeath -= self.__onVehicleDestroyed
        if self.__isNitroSoundPlaying:
            SoundGroups.g_instance.playSound2D(HBUISound.NITRO_DEACTIVATION)
            self.__isNitroSoundPlaying = False
        super(EquipmentSoundPlayer, self)._finalize()
        return

    def __onEquipmentUpdated(self, _, item):
        if item.getPrevStage() == item.getStage():
            return
        equipment = vehicles.g_cache.equipments().get(item.getEquipmentID())
        if equipment:
            prevStage = item.getPrevStage()
            curStage = item.getStage()
            prevStageIsReady = prevStage in (EQUIPMENT_STAGES.READY, EQUIPMENT_STAGES.PREPARING)
            currentStageIsActive = curStage in (EQUIPMENT_STAGES.ACTIVE, EQUIPMENT_STAGES.COOLDOWN, EQUIPMENT_STAGES.EXHAUSTED)
            if prevStageIsReady and currentStageIsActive:
                if equipment and equipment.activationSound:
                    if equipment.name == 'afterburning_hb':
                        self.__isNitroSoundPlaying = True
                    SoundGroups.g_instance.playSound2D(equipment.activationSound)
            else:
                prevStageIsActive = prevStage == EQUIPMENT_STAGES.ACTIVE
                currentStageIsCooldown = curStage in (EQUIPMENT_STAGES.COOLDOWN, EQUIPMENT_STAGES.READY, EQUIPMENT_STAGES.UNAVAILABLE)
                if prevStageIsActive and currentStageIsCooldown:
                    if equipment and equipment.deactivationSound:
                        if equipment.name == 'afterburning_hb':
                            self.__isNitroSoundPlaying = False
                        SoundGroups.g_instance.playSound2D(equipment.deactivationSound)

    def __onCombatEquipmentUsed(self, shooterID, eqID):
        equipment = vehicles.g_cache.equipments().get(eqID)
        if equipment is None:
            return
        else:
            if hasattr(equipment, 'wwsoundShot') and equipment.wwsoundShot:
                shotSoundPreDelay = 0.0
                if hasattr(equipment, 'shotSoundPreDelay'):
                    if equipment.shotSoundPreDelay is not None:
                        shotSoundPreDelay = equipment.shotSoundPreDelay
                delay = 0.0
                if hasattr(equipment, 'delay'):
                    delay = equipment.delay
                elif hasattr(equipment, 'minDelay'):
                    delay = equipment.minDelay
                if delay > shotSoundPreDelay:
                    delay = delay - shotSoundPreDelay
                if self.soundDelayer.hasDelayedCallbackID(eqID):
                    self.soundDelayer.stopCallback(eqID)
                self.soundDelayer.delayCallback(eqID, delay, SoundGroups.g_instance.playSound2D, equipment.wwsoundShot)
            return

    def __onEquipmentMarkerShown(self, item, pos, direction, time, team):
        if not isinstance(item, HBDeathZoneItem):
            return
        if self.__deathZoneSoundPlayed:
            return
        self.__deathZoneSoundPlayed = True
        _playSoundNotification(HBGameplayVoiceovers.DEATH_ZONE_ATTACK)

    def __onVehicleDestroyed(self, *_):
        if self.__isNitroSoundPlaying:
            SoundGroups.g_instance.playSound2D(HBUISound.NITRO_DEACTIVATION)
            self.__isNitroSoundPlaying = False
