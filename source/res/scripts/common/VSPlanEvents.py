# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/VSPlanEvents.py
from __future__ import absolute_import
from collections import namedtuple
from typing import Optional

class PcVSPlanSimpleEvent(object):
    CLIENT_ACTIVATION_EVENT = 'OnClientActivation'
    VEHICLE_START_MOVING = 'OnVehicleStartMoving'
    VEHICLE_STOP_MOVING = 'OnVehicleStopMoving'
    VEHICLE_START_FWD_MOVING = 'OnVehicleStartFwdMoving'
    VEHICLE_STOP_FWD_MOVING = 'OnVehicleStopFwdMoving'
    VEHICLE_SHOOT = 'OnVehicleShoot'
    VEHICLE_STUN = 'OnVehicleStun'
    VEHICLE_STUN_OFF = 'OnVehicleStunOff'
    VEHICLE_FIRE_STARTED = 'OnVehicleFireStarted'
    VEHICLE_FIRE_STOPPED = 'OnVehicleFireStopped'
    VEHICLE_EQUIPMENT_SWAP = 'OnVehicleEquipmentSwap'
    VEHICLE_DAMAGE_BY_ENEMY = 'OnVehicleDamageByEnemy'
    VEHICLE_DAMAGE_RECEIVED = 'onVehicleDamageReceived'
    VEHICLE_CHANGE_HEALTH = 'OnVehicleChangeHealth'
    VEHICLE_DEVICE_WAS_CRIT = 'OnVehicleDeviceWasCrit'
    VEHICLE_TANKMAN_WAS_CRIT = 'OnVehicleTankmanWasCrit'
    VEHICLE_TANKMAN_HEALED = 'OnVehicleTankmanHealed'
    VEHICLE_DEVICE_HEALED = 'OnVehicleDeviceHealed'
    VEHICLE_GUN_REALOAD_FINISHED = 'OnVehicleGunReloadFinished'
    VEHICLE_CLIP_REALOAD_FINISH = 'OnVehicleClipReload'
    ENEMY_DETECTED = 'OnEnemyDetected'
    VEHICLE_SIXTH_SENSE_ACTIVATE = 'OnVehicleSixthSenseActivate'
    VEHICLE_CHANGE_SHELLS_BY_CLIENT = 'OnVehicleChangeShellsByClient'
    VEHICLE_ON_TARGET_KILLED = 'OnVehicleOnTargetKilled'
    VEHICLE_ON_TARGET_CRIT = 'OnVehicleOnTargetCrit'
    ARENA_ON_BATTLE_START = 'OnArenaOnBattleStart'
    ON_NO_DAMAGE_SHOT = 'OnNoDamageShot'


OnInnerDeviceWasCrit = namedtuple('OnInnerDeviceWasCrit', 'modulesCount')
OnVehicleEquipmentActivated = namedtuple('OnVehicleEquipmentActivated', 'cooldownEquipmentIndex, cooldownEquipmentName')
OnVehicleTotalDamageDealtIncrease = namedtuple('OnVehicleTotalDamageDealtIncrease', 'totalDamageDealt')
OnVehicleAssistIncrease = namedtuple('OnVehicleAssistIncrease', 'assistPoints')
OnVehicleBlockDamage = namedtuple('OnVehicleBlockDamage', 'blockedDamage')
OnVehicleInRange = namedtuple('OnVehicleInRange', 'targetTeam, targetClass, enabled')
OnVehicleShotDamagedEnemyVehicle = namedtuple('OnVehicleShotDamagedEnemyVehicle', 'targetId')
OnVehicleRadioDistanceChange = namedtuple('OnVehicleRadioDistanceChange', 'radioDistance')
OnWitnessEnemyDamaged = namedtuple('OnWitnessEnemyDamaged', 'targetID')
OnTankmanStatusChanged = namedtuple('tankmanStatusChangedEffect', 'tmanIdx')

class VSPlanEventPerkData(object):
    __slots__ = ('perkID',)

    def __init__(self):
        self.perkID = None
        return

    def __str__(self):
        return 'VSPlanEventPerkData(perkID={})'.format(self.perkID)
