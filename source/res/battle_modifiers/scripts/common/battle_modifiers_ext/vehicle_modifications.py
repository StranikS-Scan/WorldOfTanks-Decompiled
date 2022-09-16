# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_modifiers/scripts/common/battle_modifiers_ext/vehicle_modifications.py
import copy
from battle_modifier_constants import USE_MODIFICATION_CACHE, MAX_MODIFICATION_LAYER_COUNT, ModifierDomain, BattleParams
from battle_modifiers_common import battle_modifiers
from collections import deque
from constants import IS_CELLAPP, IS_CLIENT, SHELL_TYPES, SHELL_MECHANICS_TYPE, VEHICLE_MODE
from math import tan, atan, cos, acos
from items.components.component_constants import DEFAULT_GUN_CLIP, DEFAULT_GUN_BURST, DEFAULT_GUN_AUTORELOAD, DEFAULT_GUN_DUALGUN, KMH_TO_MS, MS_TO_KMH
from typing import TYPE_CHECKING, Optional, Type, Dict, Tuple
from Math import Vector2
if TYPE_CHECKING:
    from items.vehicles import VehicleType
    from items.vehicle_items import Chassis, Turret, Gun, Radio, Shell
    from items.components.gun_components import GunShot
    from items.components.shell_components import ShellType
    from battle_modifiers import BattleModifiers
g_cache = None

class VehicleModifier(object):

    @classmethod
    def modifyVehicle(cls, vehType, modifiers):
        return vehType if not modifiers.haveDomain(ModifierDomain.VEH_TYPE_COMPONENTS) else cls._modifyVehType(vehType, modifiers)

    @classmethod
    def _modifyVehType(cls, vehType, modifiers):
        vehType = copy.copy(vehType)
        if modifiers.haveDomain(ModifierDomain.VEH_TYPE):
            invisibility = vehType.invisibility
            vehType.invisibility = (modifiers(BattleParams.INVISIBILITY_ON_MOVE, invisibility[0]), modifiers(BattleParams.INVISIBILITY_ON_STILL, invisibility[1]))
            damageByStaticsChances = vehType.damageByStaticsChances
            vehType.damageByStaticsChances = {'tankman': modifiers(BattleParams.ENV_TANKMAN_DAMAGE_CHANCE, damageByStaticsChances['tankman']),
             'module': modifiers(BattleParams.ENV_MODULE_DAMAGE_CHANCE, damageByStaticsChances['module'])}
        if modifiers.haveDomain(ModifierDomain.CHASSIS):
            vehType.chassis = tuple((cls.__modifyChassis(chassis, modifiers) for chassis in vehType.chassis))
        if modifiers.haveDomain(ModifierDomain.TURRET_COMPONENTS):
            vehType.turrets = tuple((tuple((cls.__modifyTurret(turret, modifiers) for turret in turretsList)) for turretsList in vehType.turrets))
        if modifiers.haveDomain(ModifierDomain.RADIO):
            vehType.radios = tuple((cls.__modifyRadio(radio, modifiers) for radio in vehType.radios))
        if modifiers.haveDomain(ModifierDomain.PHYSICS):
            vehType.xphysics = cls.__modifyPhysics(vehType.xphysics, modifiers)
        return vehType

    @classmethod
    def __modifyChassis(cls, chassis, modifiers):
        chassis = copy.copy(chassis)
        dispFactors = chassis.shotDispersionFactors
        chassis.shotDispersionFactors = (modifiers(BattleParams.DISP_FACTOR_CHASSIS_MOVEMENT, dispFactors[0]), modifiers(BattleParams.DISP_FACTOR_CHASSIS_ROTATION, dispFactors[1]))
        return chassis

    @classmethod
    def __modifyTurret(cls, turret, modifiers):
        turret = copy.copy(turret)
        if modifiers.haveDomain(ModifierDomain.TURRET):
            turret.rotationSpeed = modifiers(BattleParams.TURRET_ROTATION_SPEED, turret.rotationSpeed)
            turret.circularVisionRadius = modifiers(BattleParams.VISION_RADIUS, turret.circularVisionRadius)
        if modifiers.haveDomain(ModifierDomain.GUN_COMPONENTS):
            turret.guns = tuple((cls.__modifyGun(gun, modifiers) for gun in turret.guns))
        return turret

    @classmethod
    def __modifyGun(cls, gun, modifiers):
        gun = copy.copy(gun)
        if modifiers.haveDomain(ModifierDomain.GUN):
            gun.rotationSpeed = modifiers(BattleParams.GUN_ROTATION_SPEED, gun.rotationSpeed)
            gun.reloadTime = modifiers(BattleParams.RELOAD_TIME, gun.reloadTime)
            if gun.clip != DEFAULT_GUN_CLIP:
                clipCount, clipInterval = gun.clip
                gun.clip = (clipCount, modifiers(BattleParams.CLIP_INTERVAL, clipInterval))
            if gun.burst != DEFAULT_GUN_BURST:
                burstCount, burstInterval = gun.burst
                gun.clip = (burstCount, modifiers(BattleParams.BURST_INTERVAL, burstInterval))
            if gun.autoreload != DEFAULT_GUN_AUTORELOAD:
                modifiedReloadTime = [ modifiers(BattleParams.AUTORELOAD_TIME, reloadTime) for reloadTime in gun.autoreload.reloadTime ]
                gun.autoreload = gun.autoreload._replace(reloadTime=tuple(modifiedReloadTime))
            gun.aimingTime = modifiers(BattleParams.AIMING_TIME, gun.aimingTime)
            if BattleParams.SHOT_DISPERSION_RADIUS in modifiers:
                initRadius = tan(gun.shotDispersionAngle) * 100.0
                gun.shotDispersionAngle = atan(modifiers(BattleParams.SHOT_DISPERSION_RADIUS, initRadius) / 100.0)
            dispFactors = gun.shotDispersionFactors
            gun.shotDispersionFactors = {'turretRotation': modifiers(BattleParams.DISP_FACTOR_TURRET_ROTATION, dispFactors['turretRotation']),
             'afterShot': modifiers(BattleParams.DISP_FACTOR_AFTER_SHOT, dispFactors['afterShot']),
             'whileGunDamaged': modifiers(BattleParams.DISP_FACTOR_WHILE_GUN_DAMAGED, dispFactors['whileGunDamaged'])}
            if gun.dualGun != DEFAULT_GUN_DUALGUN:
                reloadTimes = [ modifiers(BattleParams.RELOAD_TIME, reloadTime) for reloadTime in gun.dualGun.reloadTimes ]
                gun.dualGun = gun.dualGun._replace(reloadTimes=tuple(reloadTimes))
        if modifiers.haveDomain(ModifierDomain.SHOT_COMPONENTS):
            gun.shots = tuple((cls.__modifyShot(shot, modifiers) for shot in gun.shots))
        return gun

    @classmethod
    def __modifyShot(cls, shot, modifiers):
        shot = copy.copy(shot)
        if modifiers.haveDomain(ModifierDomain.SHOT):
            from items import vehicles
            speedFactor = vehicles.g_cache.commonConfig['miscParams']['projectileSpeedFactor']
            initSpeed = shot.speed / speedFactor
            shot.speed = modifiers(BattleParams.SHELL_SPEED, initSpeed) * speedFactor
            gravityFactor = speedFactor ** 2
            initGravity = shot.gravity / gravityFactor
            shot.gravity = modifiers(BattleParams.SHELL_GRAVITY, initGravity) * gravityFactor
            piercingPower = shot.piercingPower
            shot.piercingPower = Vector2(modifiers(BattleParams.PIERCING_POWER_FIRST, piercingPower[0]), modifiers(BattleParams.PIERCING_POWER_LAST, piercingPower[1]))
        if modifiers.haveDomain(ModifierDomain.SHELL_COMPONENTS):
            shot.shell = cls.__modifyShell(shot.shell, modifiers)
        return shot

    @classmethod
    def __modifyShell(cls, shell, modifiers):
        shell = copy.copy(shell)
        if modifiers.haveDomain(ModifierDomain.SHELL):
            if BattleParams.DAMAGE_RANDOMIZATION in modifiers:
                shell.useAltDamageRandomization = True
                shell.damageRandomization = modifiers(BattleParams.DAMAGE_RANDOMIZATION, shell.damageRandomization)
            shell.piercingPowerRandomization = modifiers(BattleParams.PIERCING_POWER_RANDOMIZATION, shell.piercingPowerRandomization)
            damage = shell.damage
            shell.damage = (modifiers(BattleParams.ARMOR_DAMAGE, damage[0]), modifiers(BattleParams.DEVICE_DAMAGE, damage[1]))
        if modifiers.haveDomain(ModifierDomain.SHELL_TYPE):
            shell.type = cls.__modifyShellType(shell.type, modifiers)
        return shell

    @classmethod
    def __modifyShellType(cls, shellType, modifiers):
        shellType = copy.copy(shellType)
        isArmorPiercing = shellType.name.startswith('ARMOR_PIERCING')
        isHollowCharge = shellType.name == SHELL_TYPES.HOLLOW_CHARGE
        isHE = shellType.name == SHELL_TYPES.HIGH_EXPLOSIVE
        if isArmorPiercing:
            shellType.normalizationAngle = modifiers(BattleParams.NORMALIZATION_ANGLE, shellType.normalizationAngle)
        if BattleParams.RICOCHET_ANGLE in modifiers and (isArmorPiercing or isHollowCharge):
            initAngle = acos(shellType.ricochetAngleCos)
            shellType.ricochetAngleCos = cos(modifiers(BattleParams.RICOCHET_ANGLE, initAngle))
        updateDamage = BattleParams.ARMOR_DAMAGE in modifiers or BattleParams.DEVICE_DAMAGE in modifiers
        if updateDamage and isHE and shellType.mechanics == SHELL_MECHANICS_TYPE.MODERN:
            maxDamage = 0
            for mechanics in [shellType.blastWave, shellType.shellFragments, shellType.armorSpalls]:
                if not mechanics.isActive:
                    continue
                damages = mechanics.damages
                modifiedDamages = (modifiers(BattleParams.ARMOR_DAMAGE, damages[0]), modifiers(BattleParams.DEVICE_DAMAGE, damages[1]))
                mechanics.damages = modifiedDamages
                maxDamage = max(maxDamage, modifiedDamages[0], modifiedDamages[1])

            shellType.maxDamage = maxDamage
        return shellType

    @classmethod
    def __modifyRadio(cls, radio, modifiers):
        radio = copy.copy(radio)
        radio.distance = modifiers(BattleParams.RADIO_DISTANCE, radio.distance)
        return radio

    @classmethod
    def __modifyPhysics(cls, physics, modifiers):
        if IS_CELLAPP:
            return cls.__modifyPhysicsServer(physics, modifiers)
        return cls.__modifyPhysicsClient(physics, modifiers) if IS_CLIENT else physics

    @classmethod
    def __modifyPhysicsServer(cls, physics, modifiers):
        physics = copy.deepcopy(physics)
        detailed = physics['detailed']
        detailed['gravityFactor'] = modifiers(BattleParams.GRAVITY_FACTOR, detailed['gravityFactor'])
        for engine in detailed['engines'].itervalues():
            engine['smplEnginePower'] = modifiers(BattleParams.ENGINE_POWER, engine['smplEnginePower'])
            engine['smplFwMaxSpeed'] = modifiers(BattleParams.FW_MAX_SPEED, engine['smplFwMaxSpeed'])
            engine['smplBkMaxSpeed'] = modifiers(BattleParams.BK_MAX_SPEED, engine['smplBkMaxSpeed'])

        for chassis in detailed['chassis'].itervalues():
            speedOnSpot = modifiers(BattleParams.ROTATION_SPEED_ON_STILL, chassis['gimletGoalWOnSpot'])
            chassis['gimletGoalWOnSpot'] = speedOnSpot
            chassis['wPushedRot'] = speedOnSpot
            speedOnMove = modifiers(BattleParams.ROTATION_SPEED_ON_MOVE, chassis['gimletGoalWOnMove'])
            chassis['gimletGoalWOnMove'] = speedOnMove
            chassis['wPushedDiag'] = speedOnMove

        return physics

    @classmethod
    def __modifyPhysicsClient(cls, physics, modifiers):
        physics = copy.deepcopy(physics)
        for engine in physics['engines'].itervalues():
            engine['smplEnginePower'] = modifiers(BattleParams.ENGINE_POWER, engine['smplEnginePower'])
            msSpeed = modifiers(BattleParams.FW_MAX_SPEED, engine['smplFwMaxSpeed'] * KMH_TO_MS)
            engine['smplFwMaxSpeed'] = msSpeed * MS_TO_KMH

        return physics


class VehicleModificationCache(battle_modifiers.VehicleModificationCache):
    __slots__ = ('__modifications', '__maxLayerCount', '__layerIdQueue')

    def __init__(self, layerCount=MAX_MODIFICATION_LAYER_COUNT):
        super(VehicleModificationCache, self).__init__(layerCount)
        self.__modifications = {}
        self.__maxLayerCount = layerCount
        self.__layerIdQueue = deque()

    def get(self, vehType, battleModifiers):
        if not USE_MODIFICATION_CACHE:
            return VehicleModifier.modifyVehicle(vehType, battleModifiers)
        return vehType if not battleModifiers.haveDomain(ModifierDomain.VEH_TYPE_COMPONENTS) else self.__addModification(vehType, battleModifiers)

    def clear(self):
        self.__modifications.clear()
        self.__layerIdQueue.clear()

    def __addModification(self, vehType, battleModifiers):
        layerId = battleModifiers.id()
        vehId = self.__getVehId(vehType)
        modifications = self.__modifications
        if layerId not in modifications:
            self.__addLayer(layerId)
        if vehId in modifications[layerId]:
            return modifications[layerId][vehId]
        vehModification = VehicleModifier.modifyVehicle(vehType, battleModifiers)
        modifications[layerId][vehId] = vehModification
        return vehModification

    def __getVehId(self, vehType):
        return vehType.id if vehType.mode == VEHICLE_MODE.DEFAULT else vehType.id + (vehType.mode,)

    def __addLayer(self, layerId):
        if len(self.__layerIdQueue) == self.__maxLayerCount:
            del self.__modifications[self.__layerIdQueue.popleft()]
        self.__layerIdQueue.append(layerId)
        self.__modifications[layerId] = {}


def init():
    global g_cache
    g_cache = VehicleModificationCache()
