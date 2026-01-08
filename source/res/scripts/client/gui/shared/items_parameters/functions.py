# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/items_parameters/functions.py
from collections import defaultdict
from operator import itemgetter
import typing
from future.utils import iteritems, itervalues
import BigWorld
from gui.shared.formatters import text_styles
from gui.shared.gui_items import KPI
from gui.shared.gui_items.Tankman import crewMemberRealSkillLevel
from gui.shared.items_parameters import isTemperatureGun
from gui.shared.items_parameters.params_constants import MODULES
from helpers import dependency
from items import utils, tankmen, getTypeOfCompactDescr
from items.vehicles import vehicleAttributeFactors
from items.params_utils import getHeatedShotDispersion
from skeletons.gui.lobby_context import ILobbyContext
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.Vehicle import Vehicle
    from items.vehicles import VehicleDescriptor, CompositeVehicleDescriptor

class _KpiDict(object):

    def __init__(self, factors=None, factorTypes=None):
        self.__dict = defaultdict(float) if factors is None else factors
        self.__typeDict = {} if factorTypes is None else factorTypes
        return

    def __mul__(self, other):
        resultTypes, resultFactors = {}, defaultdict(float)
        otherFactors, otherTypes = other.getFactors(), other.getFactorTypes()
        for kpiName in self.__dict.viewkeys() | otherFactors.viewkeys():
            resultTypes[kpiName] = kpiType = self.__typeDict.get(kpiName) or otherTypes[kpiName]
            firstVal, secondVal = self.__dict.get(kpiName, 0.0), otherFactors.get(kpiName, 0.0)
            resultFactors[kpiName] = firstVal + secondVal + (firstVal * secondVal if kpiType == KPI.Type.MUL else 0.0)

        return _KpiDict(resultFactors, resultTypes)

    def addKPI(self, name, value, kpiType):
        delta = 1.0 if kpiType == KPI.Type.MUL else 0.0
        self.__dict[name] += value - delta
        self.__typeDict[name] = kpiType

    def getFactor(self, kpiName):
        if kpiName not in self.__dict:
            return 0.0
        kpiType = self.__typeDict[kpiName]
        return self.__dict[kpiName] * 100 if kpiType == KPI.Type.MUL else self.__dict[kpiName]

    def getFactors(self):
        return self.__dict

    def getFactorTypes(self):
        return self.__typeDict

    def getKpi(self, kpiName):
        kpiType = self.__typeDict[kpiName]
        return KPI(kpiName, (1.0 if kpiType == KPI.Type.MUL else 0.0) + self.__dict[kpiName], kpiType)

    def getKpiIterator(self):
        for kpiName, kpiValue in iteritems(self.__dict):
            kpiType = self.__typeDict[kpiName]
            yield KPI(kpiName, (1.0 if kpiType == KPI.Type.MUL else 0.0) + kpiValue, kpiType)

    def getCoeff(self, kpiName):
        return self.getFactor(kpiName) / 100 + 1


def aggregateKpi(kpiList):
    result = _KpiDict()
    for kpi in kpiList:
        result.addKPI(kpi.name, kpi.value, kpi.type)

    return result


def getKpiFactors(vehicle):
    baseKPI = _KpiDict()
    activeModifications = set(vehicle.descriptor.modifications)
    for stepItem in vehicle.postProgression.iterUnorderedSteps():
        if not (stepItem.isReceived() and stepItem.action.getActiveID() in activeModifications):
            continue
        for kpi in stepItem.action.getKpi(vehicle):
            baseKPI.addKPI(kpi.name, kpi.value, kpi.type)

    otherKPI = _KpiDict()
    for idx, optDevice in enumerate(vehicle.optDevices.installed):
        if optDevice is None:
            continue
        isSpec = bool(vehicle.optDevices.getSlot(idx).item.categories & optDevice.descriptor.categories)
        for kpi in optDevice.getKpi(vehicle):
            value = kpi.specValue if isSpec and kpi.specValue is not None else kpi.value
            otherKPI.addKPI(kpi.name, value, kpi.type)

    for item in vehicle.consumables.installed:
        if item is None:
            continue
        for kpi in item.getKpi(vehicle):
            otherKPI.addKPI(kpi.name, kpi.value, kpi.type)

    for item in vehicle.battleBoosters.installed:
        if item is None or item.isCrewBooster() or not item.isAffectsOnVehicle(vehicle):
            continue
        for kpi in item.getKpi(vehicle):
            otherKPI.addKPI(kpi.name, kpi.value, kpi.type)

    baseKPI = baseKPI * otherKPI
    for kpi in kpiFromCrewSkills(vehicle):
        baseKPI.addKPI(kpi.name, kpi.value, kpi.type)

    return baseKPI


def kpiFromCrewSkills(vehicle):
    skills = {}
    for _, tankman in vehicle.crew:
        if tankman is None:
            continue
        for skill in tankman.skills:
            if skill.isSkillActive:
                level = crewMemberRealSkillLevel(vehicle, skill.name)
                if level != tankmen.NO_SKILL:
                    skills[skill.name] = level

        for bonusSkills in itervalues(tankman.bonusSkills):
            for bonusSkill in bonusSkills:
                if bonusSkill and bonusSkill.name != 'any' and bonusSkill.level != tankmen.NO_SKILL and bonusSkill.isSkillActive:
                    level = crewMemberRealSkillLevel(vehicle, bonusSkill.name)
                    if level != tankmen.NO_SKILL:
                        skills[bonusSkill.name] = level

    for eq in vehicle.battleBoosters.installed.getItems():
        if eq.isCrewBooster() and eq.isAffectsOnVehicle(vehicle):
            if eq.descriptor.skillName not in skills:
                skills[eq.descriptor.skillName] = tankmen.MAX_SKILL_LEVEL

    kpi = []
    skillsConfig = tankmen.getSkillsConfig()
    for skillName, level in iteritems(skills):
        skillKpi = skillsConfig.getSkill(skillName).kpi
        for _kpi in skillKpi:
            baseValue = 1.0 if _kpi.type == KPI.Type.MUL else 0.0
            value = baseValue - (baseValue - _kpi.value) / tankmen.MAX_SKILL_LEVEL * level
            kpi.append(KPI(_kpi.name, value, kpiType=_kpi.type, specValue=_kpi.specValue, vehicleTypes=_kpi.vehicleTypes))

    return kpi


def getVehicleFactors(vehicle, situationalBonuses=None, isModifySkillProcessors=False):
    factors = vehicleAttributeFactors()
    vehicleDescr = vehicle.descriptor
    eqs = [ eq.descriptor for eq in vehicle.consumables.installed.getItems() ]
    for booster in vehicle.battleBoosters.installed.getItems():
        if booster.isAffectsOnVehicle(vehicle):
            eqs.append(booster.descriptor)

    crewCompactDescrs = extractCrewDescrs(vehicle)
    additionalCrewLevelIncrease = calculateAdditionalCrewLevelIncrease(vehicle, situationalBonuses)
    utils.updateAttrFactorsWithSplit(vehicleDescr, crewCompactDescrs, eqs, factors, additionalCrewLevelIncrease, isModifySkillProcessors)
    return factors


def calculateAdditionalCrewLevelIncrease(vehicle, situationalBonuses):
    situationalBonuses = situationalBonuses or []
    if not situationalBonuses:
        return 0.0
    else:
        resultCrewLevelIncrease = 0.0
        for _, tankman in vehicle.crew:
            if tankman is None:
                continue
            for skill in tankman.skills:
                if skill.isSkillActive and skill.name in situationalBonuses:
                    skillLevelIncrease = getattr(tankmen.getSkillsConfig().getSkill(skill.name), 'crewLevelIncrease', 0.0)
                    resultCrewLevelIncrease += skillLevelIncrease / tankmen.MAX_SKILL_LEVEL * skill.level

            for bonusSkills in itervalues(tankman.bonusSkills):
                for bonusSkill in bonusSkills:
                    if bonusSkill and bonusSkill.isSkillActive:
                        skillLevelIncrease = getattr(tankmen.getSkillsConfig().getSkill(bonusSkill.name), 'crewLevelIncrease', 0.0)
                        resultCrewLevelIncrease += skillLevelIncrease / tankmen.MAX_SKILL_LEVEL * bonusSkill.level

        return resultCrewLevelIncrease


def extractCrewDescrs(vehicle, replaceNone=True):
    crewCompactDescrs = []
    emptySlots = []
    otherVehicleSlots = []
    vehicleDescr = vehicle.descriptor
    for idx, tankman in sorted(vehicle.crew, key=itemgetter(0)):
        tankmanCompDescr = None
        if tankman is not None:
            if hasattr(tankman, 'strCD'):
                tankmanCompDescr = tankman.strCD
                if tankman.efficiencyRoleLevel < tankman.roleLevel:
                    otherVehicleSlots.append(idx)
            else:
                tankmanCompDescr = tankman
            if tankmanCompDescr is not None:
                _, _, roleID = tankmen.parseNationSpecAndRole(tankmanCompDescr)
                if tankmen.SKILL_NAMES[roleID] != vehicleDescr.type.crewRoles[idx][0]:
                    from gui.shared.gui_items.items_actions import factory
                    factory.doAction(factory.UNLOAD_TANKMAN, vehicle.invID, idx, int(BigWorld.serverTime()), 1)
                    tankmanCompDescr = None
        if tankmanCompDescr is None:
            if not replaceNone:
                emptySlots.append(idx)
            else:
                role = vehicleDescr.type.crewRoles[idx][0]
                tankmanCompDescr = createFakeTankmanDescr(role, vehicleDescr.type)
        crewCompactDescrs.append(tankmanCompDescr)

    return crewCompactDescrs if replaceNone else (crewCompactDescrs, emptySlots, otherVehicleSlots)


def createFakeTankmanDescr(role, vehicleType, roleLevel=100):
    nationID, vehicleTypeID = vehicleType.id
    passport = tankmen.generatePassport(nationID)
    return tankmen.generateCompactDescr(passport, vehicleTypeID, role, roleLevel)


def formatCompatibles(name, collection):
    return ', '.join([ (text_styles.neutral(c) if c == name else text_styles.main(c)) for c in collection ])


def getInstalledModuleVehicle(vehicleDescr, itemDescr):
    curVehicle = None
    if vehicleDescr:
        compDescrType = getTypeOfCompactDescr(itemDescr.compactDescr)
        module = MODULES[compDescrType](vehicleDescr)
        if module.id[1] == itemDescr.id[1]:
            curVehicle = vehicleDescr.type.userString
    return curVehicle


def isStunParamVisible(shellDict):
    lobbyContext = dependency.instance(ILobbyContext)
    return shellDict.hasStun and lobbyContext.getServerSettings().spgRedesignFeatures.isStunEnabled()


def getBasicShell(vehDescr):
    return vehDescr.gun.shots[0].shell


def getClientShotDispersion(vehicleDescr, shotDispersionFactor):
    gun = vehicleDescr.gun
    values = []
    multShotDispersionFactor = vehicleDescr.miscAttrs['multShotDispersionFactor'] * shotDispersionFactor
    shotDispersionAngle = gun.shotDispersionAngle
    if 'dualAccuracy' in gun.tags:
        values.append(gun.dualAccuracy.afterShotDispersionAngle * multShotDispersionFactor)
    elif isTemperatureGun(vehicleDescr):
        values.append(getHeatedShotDispersion(shotDispersionAngle, vehicleDescr) * multShotDispersionFactor)
    values.append(shotDispersionAngle * multShotDispersionFactor)
    if 'twinGun' in gun.tags:
        siegeVehDescr = vehicleDescr.siegeVehicleDescr
        multShotDispersionSiegeFactor = siegeVehDescr.miscAttrs['multShotDispersionFactor'] * shotDispersionFactor
        values.append(siegeVehDescr.gun.shotDispersionAngle * multShotDispersionSiegeFactor)
    return tuple(values)


def getClientCoolingDelay(vehicleDescr, factors):
    return float(vehicleDescr.gun.dualAccuracy.coolingDelay) * factors['dualAccuracyCoolingDelay']


def getMaxSteeringLockAngle(axleSteeringLockAngles):
    return max(map(abs, axleSteeringLockAngles)) if axleSteeringLockAngles else None


def getRocketAccelerationEnginePower(vehicleDescr, value):
    return value * getRocketAccelerationKpiFactors(vehicleDescr).getCoeff(KPI.Name.VEHICLE_ENGINE_POWER) if vehicleDescr.hasRocketAcceleration else None


def getRocketAccelerationKpiFactors(vehDescr):
    rocketKPI = _KpiDict()
    if vehDescr.hasRocketAcceleration:
        for kpi in vehDescr.type.rocketAccelerationParams.kpi:
            rocketKPI.addKPI(kpi.name, kpi.value, kpi.type)

    return rocketKPI


def getTurboshaftEnginePower(vehicleDescr, _):
    return vehicleDescr.siegeVehicleDescr.physics['enginePower'] if vehicleDescr.hasTurboshaftEngine else None
