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


def getPrevRanks(accRank, vehRank, rankChange, rankedConfig, cycleConfig):
    if not rankChange:
        return (accRank, vehRank)
    elif rankedConfig is None or cycleConfig is None:
        return (None, None)
    else:
        maxRank = cycleConfig.get('accRanks', rankedConfig['accRanks'])
        accSteps = cycleConfig.get('accSteps', rankedConfig['accSteps'])
        maxVehRank = cycleConfig.get('vehRanks', rankedConfig['vehRanks'])
        vehSteps = cycleConfig.get('vehSteps', rankedConfig['vehSteps'])
        rank, step = accRank
        vrank, vstep = vehRank
        if rankChange > 0:
            if vehRank > (0, 0):
                if vstep:
                    return (accRank, (vrank, vstep - 1))
                else:
                    vrank -= 1
                    maxVehSteps = vehSteps[vrank] if vrank < maxVehRank else vehSteps[-1]
                    return (accRank, (vrank, maxVehSteps - 1))
            elif step:
                return ((rank, step - 1), vehRank)
            else:
                rank -= 1
                maxSteps = accSteps[rank]
                return ((rank, maxSteps - 1), vehRank)

        elif rank >= maxRank:
            maxVehSteps = vehSteps[vrank] if vrank < maxVehRank else vehSteps[-1]
            if vstep + 1 < maxVehSteps:
                return (accRank, (vrank, vstep + 1))
            else:
                return (accRank, (vrank + 1, 0))
        else:
            maxSteps = accSteps[rank]
            if step + 1 < maxSteps:
                return ((rank, step + 1), vehRank)
            return ((rank + 1, 0), vehRank)
        return
