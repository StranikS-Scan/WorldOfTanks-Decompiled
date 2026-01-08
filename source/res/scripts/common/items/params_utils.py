# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/params_utils.py
from collections import namedtuple
import typing
from constants import IS_CLIENT, IS_WEB, IS_CGF_DUMP, IS_LOAD_GLOSSARY, IS_EDITOR
from items.components.shared_components import TemperatureGunParams, OverheatGunParams
if typing.TYPE_CHECKING:
    from items.vehicles import VehicleDescriptor
_AttributeModifier = namedtuple('_AttributeModifier', ('name', 'value', 'opType'))
if IS_CLIENT or IS_WEB or IS_LOAD_GLOSSARY or IS_CGF_DUMP or IS_EDITOR:

    def convertModifiersList(modifiersList):
        return [ _AttributeModifier(attrName, value, opType) for opType, _, attrName, value, __ in modifiersList ]


    def getTemperatureModifier(descr, modifierName):
        mechanicParams = descr.mechanicsParams.get(TemperatureGunParams.MECHANICS_NAME)
        if mechanicParams is None:
            return
        else:
            state = mechanicParams.thermalStates.states[-1]
            modifiers = convertModifiersList(state.modifiers)
            return next((m for m in modifiers if m.name == modifierName), None)


    def getHeatedAimingTime(aimingTime, descr):
        modifier = getTemperatureModifier(descr, 'gun/aimingTime')
        return aimingTime * modifier.value if modifier is not None else aimingTime


    def getHeatedShotDispersion(shotDispersion, descr):
        modifier = getTemperatureModifier(descr, 'multShotDispersionFactor')
        return shotDispersion * modifier.value if modifier is not None else shotDispersion


    def getTemperatureRateOfFire(descr, isVehicle=True):
        mechanicsParams = descr.mechanicsParams
        tempMechanicParams = mechanicsParams.get(TemperatureGunParams.MECHANICS_NAME)
        overheatMechanicParams = mechanicsParams.get(OverheatGunParams.MECHANICS_NAME)
        if tempMechanicParams is None or overheatMechanicParams is None:
            return
        else:
            heatingPerShot = tempMechanicParams.heatingPerShot
            thermalScoreLimit = tempMechanicParams.maxTemperature
            coolingPerSecFactor = overheatMechanicParams.coolingPerSecFactor
            coolingTime = thermalScoreLimit / (tempMechanicParams.coolingPerSec * coolingPerSecFactor)
            gunDescr = descr.gun if isVehicle else descr
            clipRate = round(60.0 / gunDescr.clip[1])
            burstTime = thermalScoreLimit * 60 / (heatingPerShot * clipRate)
            shootingCyclesPerMinute = 60 / (burstTime + tempMechanicParams.coolingDelay + coolingTime)
            shellsPerCycle = thermalScoreLimit / heatingPerShot
            return shootingCyclesPerMinute * shellsPerCycle
