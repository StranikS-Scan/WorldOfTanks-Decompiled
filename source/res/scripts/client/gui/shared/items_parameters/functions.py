# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/items_parameters/functions.py
import typing
from collections import defaultdict
from operator import itemgetter
from gui.shared.gui_items import KPI
from items import utils, tankmen

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
        for kpiName, kpiValue in self.__dict.iteritems():
            kpiType = self.__typeDict[kpiName]
            yield KPI(kpiName, (1.0 if kpiType == KPI.Type.MUL else 0.0) + kpiValue, kpiType)


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

    return baseKPI * otherKPI


def getVehicleFactors(vehicle):
    factors = utils.makeDefaultVehicleAttributeFactors()
    vehicleDescr = vehicle.descriptor
    perksController = vehicle.getPerksController()
    if perksController and not perksController.isInitialized():
        perksController.recalc()
    eqs = [ eq.descriptor for eq in vehicle.consumables.installed.getItems() ]
    for booster in vehicle.battleBoosters.installed.getItems():
        eqs.append(booster.descriptor)

    crewCompactDescrs = extractCrewDescrs(vehicle)
    utils.updateAttrFactorsWithSplit(vehicleDescr, crewCompactDescrs, eqs, factors, perksController)
    return factors


def extractCrewDescrs(vehicle, replaceNone=True):
    crewCompactDescrs = []
    emptySlots = []
    otherVehicleSlots = []
    vehicleDescr = vehicle.descriptor
    for idx, tankman in sorted(vehicle.crew, key=itemgetter(0)):
        if tankman is not None:
            if hasattr(tankman, 'strCD'):
                tankmanDescr = tankman.strCD
                if tankman.efficiencyRoleLevel < tankman.roleLevel:
                    otherVehicleSlots.append(idx)
            else:
                tankmanDescr = tankman
        elif not replaceNone:
            tankmanDescr = None
            emptySlots.append(idx)
        else:
            role = vehicleDescr.type.crewRoles[idx][0]
            tankmanDescr = createFakeTankmanDescr(role, vehicleDescr.type)
        crewCompactDescrs.append(tankmanDescr)

    return crewCompactDescrs if replaceNone else (crewCompactDescrs, emptySlots, otherVehicleSlots)


def createFakeTankmanDescr(role, vehicleType, roleLevel=100):
    nationID, vehicleTypeID = vehicleType.id
    passport = tankmen.generatePassport(nationID)
    return tankmen.generateCompactDescr(passport, vehicleTypeID, role, roleLevel)


def getBasicShell(vehDescr):
    return vehDescr.gun.shots[0].shell
