# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/sound_ctrls/comp7_battle_sounds.py
import typing
import logging
from collections import namedtuple
from functools import partial
import BigWorld
import WWISE
from shared_utils import nextTick
import SoundGroups
from Vehicle import StunInfo
from constants import EQUIPMENT_STAGES
from gui.battle_control import avatar_getter
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from points_of_interest_shared import PoiStatus, ENEMY_VEHICLE_ID
from skeletons.gui.battle_session import IBattleSessionProvider
from vehicle_systems.tankStructure import TankSoundObjectsIndexes
from gui.battle_control.controllers.sound_ctrls.common import SoundPlayersBattleController, VehicleStateSoundPlayer, SoundPlayer
_logger = logging.getLogger(__name__)

class Comp7BattleSoundController(SoundPlayersBattleController):

    def startControl(self, *args):
        WWISE.activateRemapping('comp7')
        super(Comp7BattleSoundController, self).startControl()

    def stopControl(self):
        super(Comp7BattleSoundController, self).stopControl()
        nextTick(partial(WWISE.deactivateRemapping, 'comp7'))()

    def _initializeSoundPlayers(self):
        return (_EquipmentStateSoundPlayer(),
         _EquipmentZoneSoundPlayer(),
         _ArtillerySoundPlayer(),
         _RoleSkillSoundPlayer(),
         _PrebattleSoundPlayer(),
         _PoiSNSoundPlayer(),
         _BuffSNSoundPlayer())


_PreDeactivationParams = namedtuple('_PreDeactivationParams', ('soundName', 'timeDelta'))

class _EquipmentStateSoundPlayer(VehicleStateSoundPlayer):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __EQUIPMENT_ACTIVATED = {'comp7_hunter': 'comp_7_ability_buff_common',
     'comp7_aoe_heal': 'comp_7_ability_aoe_heal_apply',
     'comp7_ally_support': 'comp_7_ability_buff_common',
     'comp7_concentration': 'comp_7_ability_buff_common',
     'comp7_aoe_inspire': 'comp_7_ability_insp_start',
     'comp7_fast_recharge': 'comp_7_ability_buff_common',
     'comp7_juggernaut': 'comp_7_ability_buff_common',
     'comp7_risky_attack': 'comp_7_ability_buff_common',
     'comp7_recon': 'comp_7_ability_uav',
     'comp7_berserk': 'comp_7_ability_buff_common',
     'comp7_sure_shot': 'comp_7_ability_buff_common',
     'comp7_sniper': 'comp_7_ability_bullseye',
     'comp7_aggressive_detection': 'comp_7_ability_wheel',
     'comp7_march': 'comp_7_ability_buff_common',
     'comp7_redline': 'comp_7_ability_arty_apply'}
    __EQUIPMENT_DEACTIVATED = {'comp7_aoe_heal': 'comp_7_ability_aoe_heal_stop',
     'comp7_hunter': 'comp_7_ability_buff_end',
     'comp7_ally_support': 'comp_7_ability_buff_end',
     'comp7_concentration': 'comp_7_ability_buff_end',
     'comp7_fast_recharge': 'comp_7_ability_buff_end',
     'comp7_juggernaut': 'comp_7_ability_buff_end',
     'comp7_risky_attack': 'comp_7_ability_buff_end',
     'comp7_berserk': 'comp_7_ability_buff_end',
     'comp7_sure_shot': 'comp_7_ability_buff_end',
     'comp7_sniper': 'comp_7_ability_buff_end',
     'comp7_aggressive_detection': 'comp_7_ability_buff_end',
     'comp7_march': 'comp_7_ability_buff_end'}
    __EQUIPMENT_PREPARING_START = {'comp7_redline': 'comp_7_ability_arty_aim',
     'poi_artillery_aoe': 'comp_7_ability_arty_aim',
     'poi_smoke': 'comp_7_ability_arty_aim',
     'poi_minefield': 'comp_7_ability_arty_aim'}
    __EQUIPMENT_PREPARING_CANCEL = {'comp7_redline': 'comp_7_ability_arty_cancel',
     'poi_artillery_aoe': 'comp_7_ability_arty_cancel',
     'poi_smoke': 'comp_7_ability_arty_cancel',
     'poi_minefield': 'comp_7_ability_arty_cancel'}
    __PRE_DEACTIVATION_SOUNDS = {'comp7_aoe_inspire': _PreDeactivationParams('comp_7_ability_insp_stop', 3.0)}
    __POI_EQUIPMENT_ACTIVATED = {'poi_radar': 'comp_7_ability_poi_radar',
     'poi_radar_ally': 'comp_7_ability_poi_radar_ally',
     'poi_radar_enemy': 'comp_7_ability_poi_radar_enemy',
     'poi_artillery_aoe': 'comp_7_ability_arty_apply',
     'poi_artillery_aoe_ally': 'comp_7_ability_arty_ally',
     'poi_artillery_aoe_enemy': 'comp_7_ability_arty_enemy',
     'poi_smoke': 'comp_7_ability_arty_apply',
     'poi_smoke_ally': 'comp_7_ability_arty_ally',
     'poi_smoke_enemy': 'comp_7_ability_arty_enemy',
     'poi_minefield': 'comp_7_ability_arty_apply',
     'poi_minefield_ally': 'comp_7_ability_arty_ally',
     'poi_minefield_enemy': 'comp_7_ability_arty_enemy'}

    def __init__(self):
        super(_EquipmentStateSoundPlayer, self).__init__()
        self.__callbackDelayer = None
        self.__activeEquipment = set()
        return

    def init(self):
        super(_EquipmentStateSoundPlayer, self).init()
        self.__callbackDelayer = CallbackDelayer()
        self.__activeEquipment.clear()

    def destroy(self):
        super(_EquipmentStateSoundPlayer, self).destroy()
        if self.__callbackDelayer is not None:
            self.__callbackDelayer.destroy()
            self.__callbackDelayer = None
        self.__activeEquipment.clear()
        return

    def _subscribe(self):
        super(_EquipmentStateSoundPlayer, self)._subscribe()
        ctrl = self.__sessionProvider.shared.equipments
        if ctrl is not None:
            ctrl.onEquipmentUpdated += self.__onEquipmentUpdated
        poiCtrl = self.__sessionProvider.dynamic.pointsOfInterest
        if poiCtrl is not None:
            poiCtrl.onPoiEquipmentUsed += self.__onPoiEquipmentUsed
        return

    def _unsubscribe(self):
        super(_EquipmentStateSoundPlayer, self)._unsubscribe()
        ctrl = self.__sessionProvider.shared.equipments
        if ctrl is not None:
            ctrl.onEquipmentUpdated -= self.__onEquipmentUpdated
        poiCtrl = self.__sessionProvider.dynamic.pointsOfInterest
        if poiCtrl is not None:
            poiCtrl.onPoiEquipmentUsed -= self.__onPoiEquipmentUsed
        return

    def _onVehicleStateUpdated(self, state, value):
        if state == VEHICLE_VIEW_STATE.DESTROYED:
            self.__clearActiveEquipment()

    def _onSwitchViewPoint(self):
        self.__clearActiveEquipment()

    def __onEquipmentUpdated(self, _, item):
        if item.getPrevStage() == item.getStage():
            return
        prevStageIsReady = item.getPrevStage() in (EQUIPMENT_STAGES.READY, EQUIPMENT_STAGES.PREPARING)
        prevStageIsActive = item.getPrevStage() in (EQUIPMENT_STAGES.ACTIVE,)
        stageIsCooldown = item.getStage() in (EQUIPMENT_STAGES.COOLDOWN, EQUIPMENT_STAGES.READY, EQUIPMENT_STAGES.UNAVAILABLE)
        stageIsActive = item.getStage() in (EQUIPMENT_STAGES.ACTIVE, EQUIPMENT_STAGES.COOLDOWN, EQUIPMENT_STAGES.EXHAUSTED)
        if item.getPrevStage() == EQUIPMENT_STAGES.READY and item.getStage() == EQUIPMENT_STAGES.PREPARING:
            self.__play2dFromMapping(self.__EQUIPMENT_PREPARING_START, item)
        elif item.getPrevStage() == EQUIPMENT_STAGES.PREPARING and item.getStage() == EQUIPMENT_STAGES.READY:
            self.__play2dFromMapping(self.__EQUIPMENT_PREPARING_CANCEL, item)
        elif prevStageIsReady and stageIsActive:
            self.__play2dFromMapping(self.__EQUIPMENT_ACTIVATED, item)
            self.__play2dFromMappingDelayed(self.__PRE_DEACTIVATION_SOUNDS, item)
            self.__activeEquipment.add(item.getDescriptor().name)
        elif stageIsCooldown and prevStageIsActive:
            self.__play2dFromMapping(self.__EQUIPMENT_DEACTIVATED, item)
            self.__activeEquipment.discard(item.getDescriptor().name)

    def __onPoiEquipmentUsed(self, equipment, vehicleID):
        equipmentName = equipment.name
        ownVehicleID = self.__sessionProvider.shared.vehicleState.getControllingVehicleID()
        if vehicleID == ENEMY_VEHICLE_ID:
            equipmentName = '{}_enemy'.format(equipmentName)
        elif vehicleID != ownVehicleID:
            equipmentName = '{}_ally'.format(equipmentName)
        self.__play2dFromMapping(self.__POI_EQUIPMENT_ACTIVATED, itemName=equipmentName)

    def __play2dFromMapping(self, soundsMapping, item=None, itemName=None):
        soundName = soundsMapping.get(itemName if itemName else item.getDescriptor().name)
        _play2d(soundName)

    def __play2dFromMappingDelayed(self, soundsMapping, item):
        delayedSoundParams = soundsMapping.get(item.getDescriptor().name)
        if delayedSoundParams is not None:
            self.__callbackDelayer.delayCallback(item.getTimeRemaining() - delayedSoundParams.timeDelta, _play2d, delayedSoundParams.soundName)
        return

    def __clearActiveEquipment(self):
        for equipment in self.__activeEquipment:
            soundName = self.__EQUIPMENT_DEACTIVATED.get(equipment)
            if soundName is not None:
                _play2d(soundName)

        self.__activeEquipment.clear()
        self.__callbackDelayer.clearCallbacks()
        return


class _EquipmentZoneSoundPlayer(VehicleStateSoundPlayer):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __EQUIPMENT_ZONE_ENTER = {VEHICLE_VIEW_STATE.AOE_HEAL: 'comp_7_ability_aoe_heal_enter',
     VEHICLE_VIEW_STATE.STUN: 'artillery_stun_effect_start'}
    __EQUIPMENT_ZONE_EXIT = {VEHICLE_VIEW_STATE.AOE_HEAL: 'comp_7_ability_aoe_heal_exit',
     VEHICLE_VIEW_STATE.STUN: 'artillery_stun_effect_end'}

    def __init__(self):
        super(_EquipmentZoneSoundPlayer, self).__init__()
        self.__vehicleStates = set()

    def destroy(self):
        super(_EquipmentZoneSoundPlayer, self).destroy()
        self.__vehicleStates = None
        return

    def _onVehicleStateUpdated(self, state, value):
        if state in self.__EQUIPMENT_ZONE_ENTER and self.__stateIsActive(value) and self.__checkSource(value):
            _play2d(self.__EQUIPMENT_ZONE_ENTER[state])
            self.__vehicleStates.add(state)
        elif state in self.__EQUIPMENT_ZONE_EXIT and not self.__stateIsActive(value) and state in self.__vehicleStates:
            _play2d(self.__EQUIPMENT_ZONE_EXIT[state])
            self.__vehicleStates.discard(state)

    def __stateIsActive(self, value):
        return value.duration > 0.0 if isinstance(value, StunInfo) else not value.get('finishing')

    def __checkSource(self, value):
        return True if isinstance(value, StunInfo) else not value.get('isSourceVehicle')


class _RoleSkillSoundPlayer(SoundPlayer):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __EQUIPMENT_LEVEL_UP = 'comp_7_ability_levelup'

    def _subscribe(self):
        ctrl = self.__sessionProvider.shared.equipments
        if ctrl is not None:
            ctrl.onRoleEquipmentStateChanged += self.__onRoleEquipmentStateChanged
        return

    def _unsubscribe(self):
        ctrl = self.__sessionProvider.shared.equipments
        if ctrl is not None:
            ctrl.onRoleEquipmentStateChanged -= self.__onRoleEquipmentStateChanged
        return

    def __onRoleEquipmentStateChanged(self, state, previousState):
        if state is not None and previousState is not None:
            if state.level > previousState.level:
                _play2d(self.__EQUIPMENT_LEVEL_UP)
        return


_ArtilleryAreaParams = namedtuple('_ArtilleryAreaParams', ('position', 'radius', 'endTime'))

class _ArtillerySoundPlayer(SoundPlayer):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __COMP7_ARTILLERY_NAMES = ('comp7_redline', 'poi_artillery_aoe', 'poi_smoke', 'poi_minefield')
    __ARTILLERY_START = 'comp_7_ability_arty_enter'
    __ARTILLERY_STOP = 'comp_7_ability_arty_exit'
    __ARTILLERY_DAMAGE_PC = 'imp_artillery_expl_huge_NPC_PC'

    def __init__(self):
        super(_ArtillerySoundPlayer, self).__init__()
        self.__callbackDelayer = None
        self.__attacked = False
        self.__artilleryAreas = []
        return

    def init(self):
        super(_ArtillerySoundPlayer, self).init()
        self.__callbackDelayer = CallbackDelayer()

    def destroy(self):
        super(_ArtillerySoundPlayer, self).destroy()
        if self.__callbackDelayer is not None:
            self.__callbackDelayer.destroy()
            self.__callbackDelayer = None
        self.__artilleryAreas = None
        return

    def _subscribe(self):
        ctrl = self.__sessionProvider.shared.equipments
        if ctrl is not None:
            ctrl.onEquipmentAreaCreated += self.__onEquipmentAreaCreated
        return

    def _unsubscribe(self):
        ctrl = self.__sessionProvider.shared.equipments
        if ctrl is not None:
            ctrl.onEquipmentAreaCreated -= self.__onEquipmentAreaCreated
        return

    def __onEquipmentAreaCreated(self, equipment, position, endTime, level=None):
        if equipment.name in self.__COMP7_ARTILLERY_NAMES:
            radius = equipment.getRadiusBasedOnSkillLevel(level) if level is not None else equipment.areaRadius
            self.__artilleryAreas.append(_ArtilleryAreaParams(position, radius, endTime))
            self.__updateAttack()
        return

    def __updateAttack(self):
        self.__artilleryAreas = [ area for area in self.__artilleryAreas if BigWorld.serverTime() < area.endTime ]
        vehicle = _getPlayerVehicle()
        if vehicle is not None:
            affectAreas = [ area for area in self.__artilleryAreas if vehicle.position.flatDistTo(area.position) < area.radius ]
            attacked = bool(affectAreas)
        else:
            attacked = False
        if attacked and not self.__attacked:
            _play2d(self.__ARTILLERY_START)
        elif not attacked and self.__attacked:
            _play2d(self.__ARTILLERY_STOP)
            _playVehiclePC(self.__ARTILLERY_DAMAGE_PC, TankSoundObjectsIndexes.ENGINE)
        self.__attacked = attacked
        if self.__artilleryAreas:
            self.__callbackDelayer.delayCallback(0.2, self.__updateAttack)
        return


class _PrebattleSoundPlayer(SoundPlayer):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __CONFIRM_VEHICLE_SELECTION = 'comp_7_tank_confirm'

    def _subscribe(self):
        prebattleCtrl = self.__sessionProvider.dynamic.comp7PrebattleSetup
        if prebattleCtrl is not None:
            prebattleCtrl.onSelectionConfirmed += self.__onSelectionConfirmed
        return

    def _unsubscribe(self):
        prebattleCtrl = self.__sessionProvider.dynamic.comp7PrebattleSetup
        if prebattleCtrl is not None:
            prebattleCtrl.onSelectionConfirmed -= self.__onSelectionConfirmed
        return

    def __onSelectionConfirmed(self):
        _play2d(self.__CONFIRM_VEHICLE_SELECTION)


class _PoiSNSoundPlayer(VehicleStateSoundPlayer):
    __POI_CAPTURE_TIMER_SHOWN = 'comp_7_poi_timer_capture'
    __POI_COOLDOWN_TIMER_SHOWN = 'comp_7_poi_timer_cooldown'

    def _onVehicleStateUpdated(self, state, value):
        if state == VEHICLE_VIEW_STATE.POINT_OF_INTEREST_STATE and value is not None:
            if value.status.statusID is PoiStatus.CAPTURING:
                _play2d(self.__POI_CAPTURE_TIMER_SHOWN)
            elif value.status.statusID is PoiStatus.COOLDOWN:
                _play2d(self.__POI_COOLDOWN_TIMER_SHOWN)
        return


class _BuffSNSoundPlayer(VehicleStateSoundPlayer):
    __RESET_ABILITY = 'comp_7_ability_timer_reset'
    __EQUIPMENT_STATE_ACTIVATED = {VEHICLE_VIEW_STATE.AOE_INSPIRE: 'comp_7_ability_insp_start'}

    def __init__(self):
        super(_BuffSNSoundPlayer, self).__init__()
        self.__vehicleStates = {}

    def _onVehicleStateUpdated(self, state, value):
        if VEHICLE_VIEW_STATE.AOE_INSPIRE <= state <= VEHICLE_VIEW_STATE.AGGRESSIVE_DETECTION and value is not None:
            if value.get('finishing'):
                self.__vehicleStates.pop(state, None)
            else:
                currentValue = self.__vehicleStates.get(state)
                if currentValue is not None and value.get('endTime') > currentValue:
                    _play2d(self.__RESET_ABILITY)
                else:
                    _play2d(self.__EQUIPMENT_STATE_ACTIVATED.get(state))
                self.__vehicleStates[state] = value.get('endTime')
        return


def _getPlayerVehicle():
    vehicle = avatar_getter.getPlayerVehicle()
    return vehicle if vehicle is not None and vehicle.isAlive() else None


def _play2d(soundName):
    if soundName is None:
        return
    else:
        SoundGroups.g_instance.playSound2D(soundName)
        return


def _playVehiclePC(soundName, soundObjectIndex):
    vehicle = _getPlayerVehicle()
    if vehicle is not None:
        soundObject = vehicle.appearance.engineAudition.getSoundObject(soundObjectIndex)
        if soundObject is not None:
            soundObject.play(soundName)
        else:
            _logger.debug('Could not find audition sound object for %s', soundName)
    else:
        _logger.debug('Vehicle for %s is destroyed or not loaded', soundName)
    return
