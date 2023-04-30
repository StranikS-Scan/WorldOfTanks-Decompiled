# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/VSPlanEvents.py
from collections import namedtuple

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
    VEHICLE_BLOCK_DAMAGE = 'OnVehicleBlockDamage'
    VEHICLE_CHANGE_HEALTH = 'OnVehicleChangeHealth'
    VEHICLE_DEVICE_WAS_CRIT = 'OnVehicleDeviceWasCrit'
    VEHICLE_TANKMAN_WAS_CRIT = 'OnVehicleTankmanWasCrit'
    VEHICLE_TANKMAN_HEALED = 'OnVehicleTankmanHealed'
    VEHICLE_DEVICE_HEALED = 'OnVehicleDeviceHealed'
    VEHICLE_GUN_REALOAD_FINISHED = 'OnVehicleGunReloadFinished'
    ENEMY_DETECTED = 'OnEnemyDetected'
    VEHICLE_SIXTH_SENSE_ACTIVATE = 'OnVehicleSixthSenseActivate'
    VEHICLE_CHANGE_SHELLS_BY_CLIENT = 'OnVehicleChangeShellsByClient'
    VEHICLE_ON_TARGET_KILLED = 'OnVehicleOnTargetKilled'
    VEHICLE_ON_TARGET_CRIT = 'OnVehicleOnTargetCrit'
    ARENA_ON_BATTLE_START = 'OnArenaOnBattleStart'


OnInnerDeviceWasCrit = namedtuple('OnInnerDeviceWasCrit', 'modulesCount')
OnVehicleEquipmentActivated = namedtuple('OnVehicleEquipmentActivated', 'cooldownEquipmentIndex, cooldownEquipmentName')
OnVehicleTotalDamageDealtIncrease = namedtuple('OnVehicleTotalDamageDealtIncrease', 'totalDamageDealt')
OnVehicleAssistIncrease = namedtuple('OnVehicleAssistIncrease', 'assistPoints')
OnVehicleInRange = namedtuple('OnVehicleInRange', 'targetTeam, targetClass, enabled')
OnVehicleShotDamagedEnemyVehicle = namedtuple('OnVehicleShotDamagedEnemyVehicle', 'targetId')
OnVehicleRadioDistanceChange = namedtuple('OnVehicleRadioDistanceChange', 'radioDistance')
OnWitnessEnemyDamaged = namedtuple('OnWitnessEnemyDamaged', 'targetID')
OnTankmanStatusChanged = namedtuple('tankmanStatusChangedEffect', 'tmanIdx')
