# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/VSPlanEvents.py
from collections import namedtuple

class PLATOON_VS_PLAN_SIMPLE_EVENT(object):
    CLIENT_ACTIVATION_EVENT = 'client_activation_event'
    CLIENT_DEACTIVATION_EVENT = 'client_deactivation_event'
    VEHICLE_START_MOVING = 'vehicle_start_moving'
    VEHICLE_STOP_MOVING = 'vehicle_stop_moving'
    VEHICLE_SHOOT = 'vehicle_shoot'
    VEHICLE_STUN_OFF = 'vehicle_stun_off'
    VEHICLE_BLOCK_DAMAGE = 'vehicle_block_damage'
    VEHICLE_CHANGE_HEALTH = 'vehicle_change_health'
    VEHICLE_DEVICE_WAS_CRIT = 'vehicle_device_was_crit'


SetPlanInitData = namedtuple('SetPlanInitData', 'ownerVehicleId, scopeId, perkId, perkLevel')
VehicleEquipmentActivatedEvent = namedtuple('VehicleEquipmentActivatedEvent', 'cooldownEquipmentIndex, cooldownEquipmentName')
VehicleTotalDamageDealtIncrease = namedtuple('VehicleTotalDamageDealtIncrease', 'totalDamageDealt')
