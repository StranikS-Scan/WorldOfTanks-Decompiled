# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/items_parameters/functions.py
from collections import defaultdict
import typing
from gui.shared.gui_items import KPI
from items.utils.common import makeDefaultVehicleAttributeFactors, updateAttrFactorsWithSplit
from helpers import dependency
from skeletons.gui.detachment import IDetachmentCache
from items import perks, vehicles
from items.vehicles import getBonusID
from items.components.perks_constants import PerksValueType, PERK_BONUS_VALUE_PRECISION
from items.components import component_constants
from constants import BonusTypes, SITUATIONAL_BONUSES, AbilitySystemScopeNames
from gui.shared.gui_items.perk import PerkGUI
from skeletons.gui.shared import IItemsCache
from debug_utils import LOG_ERROR
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.Vehicle import Vehicle
    from items.components.perks_components import Perk

def isSituationalBonus(bonusName, bonusType='', paramName=''):
    if bonusType == BonusTypes.DETACHMENT:
        bnsId = getBonusID(bonusType, str(bonusName))
        perk = PerkGUI(int(bnsId))
        if paramName and perk.hasParam(paramName):
            return perk.isSituationalForParam(paramName)
        return perk.situational
    if paramName and bonusType == BonusTypes.OPTIONAL_DEVICE:
        optionalDevicesID = vehicles.g_cache.optionalDeviceIDs()[bonusName]
        optDevice = vehicles.g_cache.optionalDevices()[optionalDevicesID]
        for kpi in optDevice.kpi:
            if kpi.name == paramName:
                return kpi.situational

    bnsId = getBonusID(bonusType, bonusName)
    return bnsId in SITUATIONAL_BONUSES


class _KpiDict(object):

    def __init__(self):
        self.__passiveBonuses = defaultdict(float)
        self.__allBonuses = defaultdict(float)
        self.__typeDict = {}

    def addKPI(self, name, value, kpiType, situational=False):
        delta = 1.0 if kpiType == KPI.Type.MUL else 0.0
        if not situational:
            self.__passiveBonuses[name] += value - delta
        self.__allBonuses[name] += value - delta
        self.__typeDict[name] = kpiType

    def getFactor(self, kpiName, toCompare=False, onlyPassive=False):
        if not toCompare and kpiName in self.__passiveBonuses:
            kpiValue = self.__passiveBonuses[kpiName]
        elif not onlyPassive and kpiName in self.__allBonuses:
            kpiValue = self.__allBonuses[kpiName]
        else:
            return 0.0
        kpiType = self.__typeDict[kpiName]
        return kpiValue * 100 if kpiType == KPI.Type.MUL else kpiValue


def getKpiFactors(vehicle):
    result = _KpiDict()
    for idx, optDevice in enumerate(vehicle.optDevices.installed):
        if optDevice is None:
            continue
        isSpec = bool(vehicle.optDevices.slots[idx].categories & optDevice.descriptor.categories)
        for kpi in optDevice.getKpi(vehicle):
            value = kpi.specValue if isSpec and kpi.specValue is not None else kpi.value
            result.addKPI(kpi.name, value, kpi.type, kpi.situational)

    for item in vehicle.consumables.installed:
        if item is None:
            continue
        for kpi in item.getKpi(vehicle):
            result.addKPI(kpi.name, kpi.value, kpi.type, kpi.situational)

    for item in vehicle.battleBoosters.installed:
        if item is None or item.isCrewBooster() or not item.isAffectsOnVehicle(vehicle):
            continue
        for kpi in item.getKpi(vehicle):
            result.addKPI(kpi.name, kpi.value, kpi.type, kpi.situational)

    perksController = vehicle.getPerksController()
    if perksController:
        perksCache = perks.g_cache.perks()
        for perkID, perkLevel in perksController.mergedPerks.iteritems():
            perk = perksCache.perks[perkID]
            ignoredLevel = perksController.getPerkIgnoredLevel(AbilitySystemScopeNames.DETACHMENT, perkID)
            for kpi in getPerkKpi(perk, perkLevel - ignoredLevel, vehicle):
                result.addKPI(kpi.name, kpi.value, kpi.type, kpi.situational)

    return result


def getPerkKpi(perk, perkLevel, vehicle=None):
    result = []
    for bonusName, perkArgument in perk.defaultBlockSettings.iteritems():
        value = round(perk.getArgBonusByLevel(bonusName, perkLevel), PERK_BONUS_VALUE_PRECISION)
        if perkArgument.UISettings.revert:
            value *= -1
        if perkArgument.UISettings.type == PerksValueType.PERCENTS:
            value += 1
            kpiType = KPI.Type.MUL
        else:
            kpiType = KPI.Type.ADD
        if vehicle is not None and perkArgument.UISettings.equipmentCooldown is not None:
            value *= getEquipmentCdForPerkPercentToTimeConversion(vehicle, perkArgument.UISettings.equipmentCooldown)
        situational = isSituationalBonus(perk.id, BonusTypes.DETACHMENT, bonusName)
        result.append(KPI(bonusName, value, kpiType, situational=situational))

    return result


def buildKpiDict(perksDict):
    perksCache = perks.g_cache.perks()
    kpiDict = _KpiDict()
    for perkID, perkLevel in perksDict.iteritems():
        perk = perksCache.perks[perkID]
        for kpi in getPerkKpi(perk, perkLevel):
            kpiDict.addKPI(kpi.name, kpi.value, kpi.type)

    return kpiDict


def getVehicleFactors(vehicle, ignoreSituational=False):
    factors = makeDefaultVehicleAttributeFactors()
    vehicleDescr = vehicle.descriptor
    detachmentCache = dependency.instance(IDetachmentCache)
    detachment = detachmentCache.getDetachment(vehicle.getLinkedDetachmentID())
    detachmentDescr = detachment.getDescriptor() if detachment else None
    perksController = vehicle.getPerksController()
    if perksController and not perksController.isInitialized():
        perksController.recalc()
    eqs = [ eq.descriptor for eq in vehicle.consumables.installed.getItems() ]
    for booster in vehicle.battleBoosters.installed.getItems():
        eqs.append(booster.descriptor)

    updateAttrFactorsWithSplit(vehicleDescr, detachmentDescr, eqs, factors, perksController, ignoreSituational)
    return factors


def getEquipmentCdForPerkPercentToTimeConversion(vehicle, itemNames):
    itemsCache = dependency.instance(IItemsCache)
    eqs = itemsCache.items.getEquipmentSuitableForVehicle(vehicle, itemNames)
    cds = [ eq.descriptor.cooldownSeconds for eq in eqs.itervalues() if eq.descriptor.cooldownSeconds != component_constants.ZERO_INT ]
    if not cds:
        LOG_ERROR('No reusable equipment with names {} with vehicle constraint {} available'.format(itemNames, vehicle.intCD if vehicle is not None else None))
        return component_constants.ZERO_INT
    else:
        allSameCds = all((cds[0] == cd for cd in cds))
        if not allSameCds:
            LOG_ERROR('Reusable equipment {} has different cooldowns for vehicle constraint {}'.format(itemNames, vehicle.intCD if vehicle is not None else None))
        return cds[0]


def getBasicShell(vehDescr):
    return vehDescr.gun.shots[0].shell
