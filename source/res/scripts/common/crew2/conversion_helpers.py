# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/crew2/conversion_helpers.py
from collections import namedtuple
from bisect import bisect_right
from enum import IntEnum
from typing import TYPE_CHECKING, List, Tuple
from crew2 import settings_globals
from items.components.detachment_constants import PerksOperationResultCode
from items.utils.common import SoftAssert
if TYPE_CHECKING:
    from items.tankmen import TankmanDescr
    from items.detachment import DetachmentDescr

class ConversionPointsLimit(IntEnum):
    NOT_CONVERTED = 0
    NO_LIMIT = 1
    LIMIT_REACHED = 2


PerkPointsThreshold = namedtuple('PerkPointsThreshold', ['threshold', 'groupPoints'])
ConversionStats = namedtuple('ConversionStats', ['limitOfFreePointsReached'])

def __getCrewSkillLevel(crew, skillName, calculateAvg):
    if not crew:
        return -1
    else:
        levelMax = -1
        levelAvg = 0
        for tankman in crew:
            if tankman is None:
                continue
            level = tankman.skillLevel(skillName)
            if level is None:
                continue
            levelMax = max(levelMax, level)
            levelAvg += level

        return levelAvg // len(crew) if calculateAvg and levelAvg > 0 else levelMax


def __makePointsAndThreshold(lastThresholdRec, points, groupID):
    lastGroupPoints = next(((i, gp) for i, (gp, gID) in enumerate(lastThresholdRec.groupPoints) if gID == groupID), None)
    groups = lastThresholdRec.groupPoints
    if groupID:
        if lastGroupPoints:
            points = lastGroupPoints[1] + points
            groups[lastGroupPoints[0]] = (points, groupID)
        else:
            groups.append((points, groupID))
    diff = points - lastThresholdRec.threshold
    pointsToAdd = diff if diff > 0 else 0
    return (pointsToAdd, PerkPointsThreshold(lastThresholdRec.threshold + pointsToAdd, groups))


def convertCrewSkills(detDescr, crew):
    matrixID = detDescr.perksMatrixID
    settings = settings_globals
    convData = settings.g_conversion.skillsConversion.getConversationData(matrixID)
    SoftAssert(convData is not None, 'Skill conversion settings is not found for matrixID: %d' % matrixID)
    matrixPerks = settings.g_perkSettings.matrices.getMatrix(matrixID).perks
    freePoints = detDescr.level - detDescr.getBuildLevel()
    build = detDescr.build.copy()
    detDescr.dropPerks()
    thresholds = {}
    limitReached = False
    for record in convData.skillsToPerkList:
        if not freePoints:
            break
        oldSkillLevel = __getCrewSkillLevel(crew, record.crewSkill, record.isAvg)
        if oldSkillLevel > -1:
            detPerkID = record.detPerkID
            inheritanceCoeff = int(oldSkillLevel * record.weight)
            points = bisect_right(convData.levelInheritanceThresholds, inheritanceCoeff) - 1
            pointsThreshold = thresholds.get(detPerkID, PerkPointsThreshold(0, []))
            points, thresholds[detPerkID] = __makePointsAndThreshold(pointsThreshold, points, record.group)
            if points == 0:
                continue
            points, limitReached = (freePoints, True) if points > freePoints else (points, False)
            if detPerkID in build and build[detPerkID] + points > matrixPerks[detPerkID].max_points:
                continue
            freePoints -= points
            build[detPerkID] = points + build.get(detPerkID, 0)

    addBuildRes = detDescr.addPerks(build)
    SoftAssert(addBuildRes.code == PerksOperationResultCode.NO_ERROR, 'Skill conversion faild, build error num: %d (PerksOperationResultCode)' % addBuildRes.code)
    return ConversionStats(limitReached)
