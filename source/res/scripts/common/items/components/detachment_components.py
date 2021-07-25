# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/components/detachment_components.py
import struct
import copy
from enum import IntEnum
from typing import Tuple, Dict, Any, List, Optional, Callable, TYPE_CHECKING
from collections import namedtuple
from items.utils.common import spliceCompDescr, bitsCount, getBit
from soft_exception import SoftException
from constants import VEHICLE_CLASS_INDICES
from collections import defaultdict
from items import vehicles, perks
from items.components.perks_constants import PERKS_TYPE
from items.components.perks_components import packPerk, unpackPerk
from detachment_constants import PerksOperationResultCode, PerksOperationResult, DetachmentSlotType
from crew2 import settings_globals
if TYPE_CHECKING:
    from items.detachment import DetachmentDescr
VehicleIdentification = namedtuple('VehicleIdentification', ['nationID', 'classID', 'isPremium'])
PerkBonusInfluenceItem = namedtuple('PerkBonusInfluenceItem', ['type',
 'id',
 'perkID',
 'bonus',
 'overcap'])
PerkApplyItem = namedtuple('PerkApplyItem', ['type',
 'id',
 'perkID',
 'bonus',
 'overcap'])

class PerkBonusApplier(IntEnum):
    BOOSTER = 0
    INSTRUCTOR = 1


def validatePropertyLock(owner, bits, subBit=None):
    if getBit(owner.lockMask, bits, subBit):
        raise SoftException("'{}' property is not changeable".format(owner.__class__.__name__))


def packIDs(IDs, slots=False):
    if IDs:
        count = len(IDs)
        if slots:
            validIDs = []
            slotsBits = 0
            for i, val in enumerate(IDs):
                if val is not None:
                    slotsBits |= 1 << i
                    validIDs.append(val)

            if validIDs:
                return struct.pack(('<BB' + str(len(validIDs)) + 'H'), count, slotsBits, *validIDs)
            else:
                return struct.pack('<BB', count, slotsBits)
        else:
            return struct.pack(('<B' + str(count) + 'H'), count, *IDs)
    return struct.pack('<B', 0)


def unpackIDs(compDescr, offset, slots=False):
    cdPart, offset = spliceCompDescr(compDescr, offset, 1)
    count = struct.unpack('<B', cdPart)
    if count == 0:
        return ([], offset)
    elif slots:
        res = [None] * count
        cdPart, offset = spliceCompDescr(compDescr, offset, 1)
        slotsBits = struct.unpack('<B', cdPart)
        if slotsBits:
            valuesCount = bitsCount(slotsBits)
            cdPart, offset = spliceCompDescr(compDescr, offset, valuesCount * 2)
            IDs = struct.unpack('<' + str(valuesCount) + 'H', cdPart)
            j = 0
            for i in range(count):
                if slotsBits & 1 << i:
                    res[i] = IDs[j]
                    j += 1

        return (res, offset)
    else:
        cdPart, offset = spliceCompDescr(compDescr, offset, count * 2)
        return (list(struct.unpack('<' + str(count) + 'H', cdPart)), offset)
        return


def packPerks(perkIDToLevel):
    packedPerksList = [ packPerk(perkID, level) for perkID, level in perkIDToLevel.iteritems() ]
    return packIDs(packedPerksList)


def unpackPerks(compDescr, offset):
    IDs, offset = unpackIDs(compDescr, offset)
    return ({}, offset) if not IDs else (dict(map(unpackPerk, IDs)), offset)


def generate(generators, obj, ctx, *args):
    for attrName, val in generators:
        if attrName in ctx:
            setattr(obj, attrName, ctx[attrName])
        if callable(val):
            setattr(obj, attrName, val(*args))
        setattr(obj, attrName, copy.copy(val))


def validate(validators, obj, skipNone, *args):
    for attrName, validator in validators:
        attrVal = getattr(obj, attrName)
        if not skipNone and attrVal is None:
            raise SoftException('Validator error: attribute {} is None.'.format(attrName))
        if not validator(obj, attrVal, *args):
            raise SoftException("Validator error: attribute {} value '{}' is not valid.".format(attrName, attrVal))

    return


def setCtxAttrIfNotNone(ctx, attrName, val):
    if val is not None:
        if isinstance(val, list):
            val = list(val)
        if isinstance(val, tuple):
            val = tuple(val)
        if isinstance(val, dict):
            val = val.copy()
        ctx[attrName] = val
    return


def convertAndGetPropertyValues(obj, names):
    res = []
    for propName in names:
        val = getattr(obj, propName)
        res.append(0 if val is None else val)

    return res


def convertAndApplyPropertyValues(obj, names, intValues):
    for propName, newValue in zip(names, intValues):
        setattr(obj, propName, None if newValue == 0 else newValue)

    return


def raiseAttrException(attr):
    raise SoftException("Generator error: attribute '{}' not set".format(attr))


def mergePerks(*builds):
    newBuild = defaultdict(int)
    for build in builds:
        for perkID, perkLevel in build.iteritems():
            newBuild[perkID] += perkLevel

    return newBuild


def applyBonusPerks(build, bonusCollection, perksMatrix, outApplyHistory):
    newBuild = dict(build)
    for item in bonusCollection:
        perkID = item.perkID
        maxPoints = perksMatrix[perkID].max_points
        perkPoints = newBuild.get(perkID, 0)
        isOvercap = perkPoints >= maxPoints
        pointsToAdd = item.overcap if isOvercap else min(item.bonus, maxPoints - perkPoints)
        newBuild[perkID] = newBuild.get(perkID, 0) + pointsToAdd
        if outApplyHistory is None:
            continue
        outApplyHistory.append(PerkApplyItem(item.type, item.id, perkID, pointsToAdd, pointsToAdd if isOvercap else 0))

    return newBuild


def isPerksRepartition(build, perksDict):
    for perkID, level in perksDict.iteritems():
        if level < 0 and perkID in build:
            return True

    return False


def addPerksToBuild(build, matrixID, levelLimit, perksDict):
    matrix = settings_globals.g_perkSettings.matrices.getMatrix(matrixID)
    currentPerks = dict(build)
    for perkID, levelToAdd in perksDict.iteritems():
        if levelToAdd == 0:
            return PerksOperationResult(PerksOperationResultCode.PERK_ZERO_LEVEL, [perkID], None)
        perk = perks.g_cache.perks().perks.get(perkID)
        if perk is None:
            return PerksOperationResult(PerksOperationResultCode.PERK_NOT_VALID, [perkID], None)
        currentLevel = currentPerks.get(perkID)
        if currentLevel is None:
            if levelToAdd <= 0:
                return PerksOperationResult(PerksOperationResultCode.PERK_NOT_IN_BUILD, [perkID], None)
            currentLevel = 0
        levelSum = currentLevel + levelToAdd
        perkCfg = matrix.perks.get(perkID)
        if perkCfg is None:
            return PerksOperationResult(PerksOperationResultCode.PERK_NOT_IN_MATRIX, [perkID], None)
        if levelSum > perkCfg.max_points:
            return PerksOperationResult(PerksOperationResultCode.PERK_MAX_LEVEL_REACHED, [perkID], None)
        if levelSum < 0:
            return PerksOperationResult(PerksOperationResultCode.PERK_NEGATIVE_LEVEL, [perkID], None)
        if levelSum == 0:
            del currentPerks[perkID]
        currentPerks[perkID] = levelSum if perk.perkType == PERKS_TYPE.SIMPLE else 1

    totalLevel = 0
    branchUPerksCounts = defaultdict(int)
    branchPoints = defaultdict(int)
    branchPerksStats = defaultdict(lambda : [0, 0])
    for perkID, level in currentPerks.iteritems():
        perkCfg = matrix.perks.get(perkID)
        branch = perkCfg.branch
        if perkCfg.ultimate:
            branchUPerksCounts[branch] += 1
        totalLevel += level
        branchPoints[branch] += level
        branchPerksStats[branch][0] += 1
        branchPerksStats[branch][1] += int(level >= matrix.perkMinThreshold)

    if totalLevel > levelLimit:
        return PerksOperationResult(PerksOperationResultCode.LEVEL_LIMIT_REACHED, [], None)
    else:
        for branchID, points in branchPoints.iteritems():
            branchCfg = matrix.branches.get(branchID)
            if points < branchCfg.ultimate_threshold and branchUPerksCounts[branchID] > 0:
                return PerksOperationResult(PerksOperationResultCode.UPERK_ACTIVE_WRONG, [branchID], None)
            if branchPerksStats[branchID][0] > branchPerksStats[branchID][1] + 1:
                return PerksOperationResult(PerksOperationResultCode.PERKS_RULES_FAILED, [branchID], None)

        for branchID, count in branchUPerksCounts.iteritems():
            if count > 1:
                return PerksOperationResult(PerksOperationResultCode.UPERK_ACTIVE_WRONG, [branchID], None)
            if count == 1:
                branchCfg = matrix.branches.get(branchID)
                if branchPoints[branchID] < branchCfg.ultimate_threshold:
                    return PerksOperationResult(PerksOperationResultCode.UPERK_ACTIVE_WRONG, [branchID], None)

        return PerksOperationResult(PerksOperationResultCode.NO_ERROR, [], currentPerks)


BranchPointsAndTalents = namedtuple('BranchPointsAndTalents', ['points', 'talents', 'totalPoints'])

def getBranchPointsAndTalents(matrixSettings, build, countTalentsLevel=False):
    totalPoints = 0
    points = defaultdict(int)
    talents = {}
    for perk, level in build.iteritems():
        perkSett = matrixSettings.perks[perk]
        if perkSett.ultimate:
            talents[perkSett.branch] = True
            if not countTalentsLevel:
                continue
        points[perkSett.branch] += level
        totalPoints += level

    return BranchPointsAndTalents(points, talents, totalPoints)


def getFilteredBuild(matrixSettings, build, select=PERKS_TYPE.ANY):
    res = {}
    for pID, level in build.iteritems():
        ultimative = matrixSettings.perks[pID].ultimate
        if ultimative and getBit(select, PERKS_TYPE.ULTIMATE) or not ultimative and getBit(select, PERKS_TYPE.SIMPLE):
            res[pID] = level

    return res


def getVehicleIdentification(vehCompDescr):
    vehicleType = vehicles.getVehicleType(vehCompDescr)
    vehClassIndex = VEHICLE_CLASS_INDICES[vehicles.getVehicleClassFromVehicleType(vehicleType)]
    vehNationID, _ = vehicleType.id
    return VehicleIdentification(vehNationID, vehClassIndex, vehicleType.isPremium())


def getCommonClassForVehicles(vehTypeCompDescrList, validate=True):
    res = None
    for vehTypeCompDescr in vehTypeCompDescrList:
        if vehTypeCompDescr is not None:
            vehIdent = getVehicleIdentification(vehTypeCompDescr)
            if res is not None and res != vehIdent.classID:
                if validate:
                    raise SoftException('vehicle slots contains vehicle with different classes')
                else:
                    return -1
            res = vehIdent.classID

    return res


def isSuitableVehicleForSlotByType(vehCompDescr, detDescr):
    vehTypeCompDescr = vehicles.getVehicleTypeCompactDescr(vehCompDescr)
    return any((slotVal == vehTypeCompDescr for slotVal in detDescr.iterSlots(DetachmentSlotType.VEHICLES)))


def getHours(seconds):
    return seconds / 3600


def getVehTypeCDIsPremForVitalHistory(inventory, detInvID):
    detMgr = inventory._detachmentMgr
    vehTypeCompDescr = inventory.getVehicleTypeCompDescr(detMgr.getDetachmentToVehicleLink(detInvID))
    if vehTypeCompDescr:
        vehicleIdent = getVehicleIdentification(vehTypeCompDescr)
        if vehicleIdent.isPremium:
            return vehTypeCompDescr
        return None
    else:
        return vehTypeCompDescr
