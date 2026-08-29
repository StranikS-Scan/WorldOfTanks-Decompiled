# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/battle_context_hints/common.py
from typing import Optional, TYPE_CHECKING
from shared_utils import CONST_CONTAINER
if TYPE_CHECKING:
    from gui.battle_control.controllers.consumables.ammo_ctrl import AmmoController

def getBestPiercingShellCD(ammoCtrl):
    if ammoCtrl is None:
        return
    else:
        currentShellCD = ammoCtrl.getCurrentShellCD()
        if currentShellCD is None:
            return
        gunSettings = ammoCtrl.getGunSettings()
        currentPiercingPower = gunSettings.getPiercingPower(currentShellCD)
        bestShellCD = None
        bestPiercingPower = currentPiercingPower
        for intCD, (count, _) in ammoCtrl.getShellsLayout():
            if count <= 0 or intCD == currentShellCD:
                continue
            piercingPower = gunSettings.getPiercingPower(intCD)
            if piercingPower > bestPiercingPower:
                bestPiercingPower = piercingPower
                bestShellCD = intCD

        return bestShellCD


class HintId(CONST_CONTAINER):
    PLAYER_VEHICLE_OBSERVED = 'PlayerVehicleObserved'
    KILLED_WHILE_OBSERVED = 'KilledWhileObserved'
    IN_SAFETY_WHILE_NOT_OBSERVED = 'InSafetyWhileNotObserved'
    ENGINE_DAMAGE_REPAIR_KIT = 'EngineDamageRepairKit'
    AMMUNITION_DAMAGE_REPAIR_KIT = 'AmmunitionDamageRepairKit'
    FUELTANK_DAMAGE_REPAIR_KIT = 'FueltankDamageRepairKit'
    GUN_ROTATOR_DAMAGE_REPAIR_KIT = 'GunRotatorDamageRepairKit'
    GUN_DAMAGE_REPAIR_KIT = 'GunDamageRepairKit'
    AMMUNITION_CRIT = 'AmmunitionCrit'
    FUELTANK_CRIT = 'FueltankCrit'
    GUN_ROTATOR_DESTROY_REPAIR_KIT = 'GunRotatorDestroyRepairKit'
    ENGINE_DESTROY_REPAIR_KIT = 'EngineDestroyRepairKit'
    GUN_DESTROY_REPAIR_KIT = 'GunDestroyRepairKit'
    TRACK_DESTROY_REPAIR_KIT = 'TrackDestroyRepairKit'
    MODULE_DAMAGE = 'ModuleDamage'
    COMMANDER_DAMAGE_MED_KIT = 'CommanderDamageMedKit'
    DRIVER_DAMAGE_MED_KIT = 'DriverDamageMedKit'
    GUNNER_DAMAGE_MED_KIT = 'GunnerDamageMedKit'
    LOADER_DAMAGE_MED_KIT = 'LoaderDamageMedKit'
    RADIOMAN_DAMAGE_MED_KIT = 'RadiomanDamageMedKit'
    AMMO_TYPE_AVAILABLE = 'AmmoTypeAvailable'
    AMMO_TYPE_SWITCH = 'AmmoTypeSwitch'


class ContextHintsSoundEvents(CONST_CONTAINER):
    PLAYER_VEHICLE_OBSERVED = 'vo_contextHints_04_00'
    KILLED_WHILE_OBSERVED = 'vo_contextHints_04_01'
    IN_SAFETY_WHILE_NOT_OBSERVED = 'vo_contextHints_InSafetyWhileNotObserved'
    MODULE_REPAIR_KIT = 'vo_contextHints_04_03'
    AMMUNITION_CRIT = 'vo_contextHints_04_08'
    FUELTANK_CRIT = 'vo_contextHints_04_09'
    MODULE_DAMAGE = 'vo_contextHints_04_14'
    TANKMAN_DAMAGE = 'vo_contextHints_04_15'
    AMMO_TYPE_AVAILABLE = 'vo_contextHints_AmmoTypeAvailable'
    AMMO_TYPE_SWITCH = 'vo_contextHints_AmmoTypeSwitch_01'
    AMMO_TYPE_SWITCH_APPLIED = 'vo_contextHints_AmmoTypeSwitch_02'
