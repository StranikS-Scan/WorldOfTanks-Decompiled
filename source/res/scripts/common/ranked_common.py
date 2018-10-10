# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/ranked_common.py
import time

def getRankedSeason(rankedConfig):
    if not rankedConfig or not rankedConfig['isEnabled'] or not rankedConfig['cycleTimes']:
        return (False, None)
    else:
        now = int(time.time())
        for cycleInfo in rankedConfig['cycleTimes']:
            startTime, endTime, seasonID, cycleID = cycleInfo
            if now >= endTime:
                continue
            if now >= startTime:
                return (True, cycleInfo)
            return (False, cycleInfo)

        return (False, None)


def getCycleConfig(rankedConfig):
    res, cycleInfo = getRankedSeason(rankedConfig)
    if not res:
        return None
    else:
        _, _, seasonID, cycleID = cycleInfo
        season = rankedConfig['seasons'].get(seasonID)
        if not season:
            return None
        cycle = season['cycles'].get(cycleID)
        return cycle


def getShieldsConfig(rankedConfig):
    result = {}
    res, seasonInfo = getRankedSeason(rankedConfig)
    if not res:
        return result
    _, _, seasonID, cycleID = seasonInfo
    season = rankedConfig['seasons'].get(seasonID)
    if season:
        cycle = season['cycles'].get(cycleID, {})
        result.update(cycle.get('shields', rankedConfig['shields']))
    return result
