# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/sound_ctrls/stronghold_battle_sounds.py
import random
import typing
import BigWorld
import SoundGroups
import WWISE
from constants import EQUIPMENT_STAGES
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from gui.battle_control.controllers.sound_ctrls.common import VehicleStateSoundPlayer, SoundPlayersBattleController, SoundPlayer
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from items import artefacts, vehicles
from skeletons.gui.battle_session import IBattleSessionProvider
from vehicle_systems.tankStructure import TankSoundObjectsIndexes

class SoundEvents(object):
    EQUIPMENT_ACTIVATED = {artefacts.AttackArtilleryFortEquipment: 'gui_clan_abl_art_apply'}
    EQUIPMENT_PREPARING = {artefacts.AttackArtilleryFortEquipment: 'gui_clan_abl_art_aim'}
    EQUIPMENT_PREPARING_CANSELED = {artefacts.AttackArtilleryFortEquipment: 'gui_clan_abl_art_cancel'}
    INSPIRE_ENTER = 'gui_clan_abl_insp_enter'
    INSPIRE_EXIT = 'gui_clan_abl_insp_exit'
    INSPIRE_START = 'gui_clan_abl_insp_start'
    INSPIRE_END = 'gui_clan_abl_insp_end'
    ARTILLERY_ENTER = 'gui_clan_abl_art_enter'
    ARTILLERY_EXIT = 'gui_clan_abl_art_exit'
    ARTILLERY_HIT_PC = 'imp_small_splash_HE_NPC_PC'
    ARTILLERY_HIT_NPC = 'imp_small_pierce_HE_NPC_NPC'


class StrongholdBattleSoundController(SoundPlayersBattleController):

    def startControl(self, *args):
        WWISE.activateRemapping('stronghold')
        super(StrongholdBattleSoundController, self).startControl(*args)

    def stopControl(self):
        WWISE.deactivateRemapping('stronghold')
        super(StrongholdBattleSoundController, self).stopControl()

    def _initializeSoundPlayers(self):
        return [_EquipmentSoundPlayer(), _InspireSoundPlayer(), _AOEZoneSoundPlayer()]


class _EquipmentSoundPlayer(SoundPlayer):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def _subscribe(self):
        ctrl = self.__sessionProvider.shared.equipments
        if ctrl is not None:
            ctrl.onEquipmentUpdated += self.__onEquipmentUpdated
        return

    def _unsubscribe(self):
        ctrl = self.__sessionProvider.shared.equipments
        if ctrl is not None:
            ctrl.onEquipmentUpdated -= self.__onEquipmentUpdated
        return

    def __onEquipmentUpdated(self, _, item):
        if item.getPrevStage() == item.getStage():
            return
        prevStageIsReady = item.getPrevStage() in (EQUIPMENT_STAGES.READY, EQUIPMENT_STAGES.PREPARING)
        currentStageIsActive = item.getStage() in (EQUIPMENT_STAGES.ACTIVE,
         EQUIPMENT_STAGES.COOLDOWN,
         EQUIPMENT_STAGES.EXHAUSTED,
         EQUIPMENT_STAGES.UNAVAILABLE)
        descrType = type(item.getDescriptor())
        if item.getPrevStage() == EQUIPMENT_STAGES.READY and item.getStage() == EQUIPMENT_STAGES.PREPARING:
            self.__playSound(descrType, SoundEvents.EQUIPMENT_PREPARING)
        elif item.getPrevStage() == EQUIPMENT_STAGES.PREPARING and item.getStage() == EQUIPMENT_STAGES.READY:
            self.__playSound(descrType, SoundEvents.EQUIPMENT_PREPARING_CANSELED)
        elif prevStageIsReady and currentStageIsActive:
            self.__playSound(descrType, SoundEvents.EQUIPMENT_ACTIVATED)

    @staticmethod
    def __playSound(descrType, soundMap):
        eventName = soundMap.get(descrType)
        if eventName is not None:
            SoundGroups.g_instance.playSound2D(eventName)
        return


class _InspireSoundPlayer(VehicleStateSoundPlayer, CallbackDelayer):
    STOP_SOURCE_SOUND_DELAY = 3

    def __init__(self):
        super(_InspireSoundPlayer, self).__init__()
        self.__isInspiring = False
        self.__isInspired = False
        self.__isSource = False

    def destroy(self):
        self.__isInspiring = False
        self.__isInspired = False
        self.__isSource = False
        VehicleStateSoundPlayer.destroy(self)
        CallbackDelayer.destroy(self)

    def _onVehicleStateUpdated(self, state, value):
        if not state == VEHICLE_VIEW_STATE.INSPIRE:
            return
        else:
            isSource = value['isSourceVehicle']
            self.__isSource = isSource if isSource is not None else self.__isSource
            isInactivation = value['isInactivation']
            attachedVehicle = BigWorld.player().getVehicleAttached()
            totalDuration = 0
            if attachedVehicle is not None and attachedVehicle.inspired is not None:
                totalDuration = attachedVehicle.inspired.inactivationEndTime - BigWorld.serverTime()
            if value['duration'] is not None and totalDuration > 0:
                if self.__isSource:
                    if not self.__isInspiring:
                        self.__isInspiring = True
                        self._playSound2D(SoundEvents.INSPIRE_START, checkAlive=True)
                        if totalDuration >= self.STOP_SOURCE_SOUND_DELAY:
                            self.delayCallback(totalDuration - self.STOP_SOURCE_SOUND_DELAY, self.__stopEvent)
                elif not self.__isInspired and not isInactivation:
                    self.__isInspired = True
                    self._playSound2D(SoundEvents.INSPIRE_ENTER, checkAlive=True)
                elif self.__isInspired and isInactivation:
                    self.__isInspired = False
                    self.__stopEvent()
            elif self.__isSource:
                if self.__isInspiring:
                    self.__isInspiring = False
                    self.clearCallbacks()
            elif self.__isInspired:
                self.__isInspired = False
                self.__stopEvent()
            return

    def __stopEvent(self):
        self._playSound2D(SoundEvents.INSPIRE_END if self.__isSource else SoundEvents.INSPIRE_EXIT, checkAlive=True)


class _AOEZoneSoundPlayer(VehicleStateSoundPlayer, CallbackDelayer):
    MIN_DELAY = 0.75
    MAX_DELAY = 1.5

    def __init__(self):
        super(_AOEZoneSoundPlayer, self).__init__()
        self.__isDelayPeriod = False
        self.__tillFinishAttackTime = 0

    def destroy(self):
        self.__isDelayPeriod = False
        self.__tillFinishAttackTime = 0
        VehicleStateSoundPlayer.destroy(self)
        CallbackDelayer.destroy(self)

    def _onVehicleStateUpdated(self, state, value):
        if not state == VEHICLE_VIEW_STATE.AOE_ZONE:
            return
        else:
            zoneData = self.__findLongest(value)
            if zoneData is None:
                self.clearCallbacks()
                self.__stopDelayPeriod()
                self.__tillFinishAttackTime = 0
                return
            strikeAttackStartTime = zoneData['startTime'] - BigWorld.serverTime()
            strikeAttackEndTime = zoneData['endTime'] - BigWorld.serverTime()
            if strikeAttackStartTime > 0:
                if not self.__isDelayPeriod:
                    self.__isDelayPeriod = True
                    self.__play2DSound(SoundEvents.ARTILLERY_ENTER)
                self.delayCallback(strikeAttackStartTime, self.__stopDelayPeriod)
            if strikeAttackEndTime > 0:
                if self.__tillFinishAttackTime > 0:
                    self.__tillFinishAttackTime = strikeAttackEndTime
                elif strikeAttackStartTime > 0:
                    self.__tillFinishAttackTime = strikeAttackEndTime
                    self.delayCallback(strikeAttackStartTime, self.__playDamageReceivedSound)
                else:
                    self.__tillFinishAttackTime = strikeAttackEndTime
                    self.__playDamageReceivedSound()
            return

    def __playDamageReceivedSound(self):
        self.__play3DVehicleSound()
        sec = random.uniform(self.MIN_DELAY, self.MAX_DELAY)
        self.__tillFinishAttackTime -= sec
        if self.__tillFinishAttackTime > 0:
            self.delayCallback(sec, self.__playDamageReceivedSound)
        else:
            self.__tillFinishAttackTime = 0

    def __stopDelayPeriod(self):
        if self.__isDelayPeriod:
            self.__isDelayPeriod = False
            self.__play2DSound(SoundEvents.ARTILLERY_EXIT)

    @staticmethod
    def __findLongest(zones):
        longestZone = None
        for zone in zones:
            equipment = vehicles.g_cache.equipments().get(zone['equipmentID'])
            if isinstance(equipment, artefacts.AttackArtilleryFortEquipment):
                if longestZone is None:
                    longestZone = zone
                elif longestZone['endTime'] < zone['endTime']:
                    longestZone = zone

        return longestZone

    @staticmethod
    def __play3DVehicleSound():
        vehicle = BigWorld.player().getVehicleAttached()
        if vehicle is not None and vehicle.isAlive() and vehicle.isStarted:
            sound = SoundEvents.ARTILLERY_HIT_PC if vehicle.isPlayerVehicle else SoundEvents.ARTILLERY_HIT_NPC
            soundObject = vehicle.appearance.engineAudition.getSoundObject(TankSoundObjectsIndexes.ENGINE)
            soundObject.play(sound)
        return

    @staticmethod
    def __play2DSound(event):
        SoundGroups.g_instance.playSound2D(event)
