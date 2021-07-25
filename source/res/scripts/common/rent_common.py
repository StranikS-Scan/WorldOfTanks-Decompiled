# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/rent_common.py
GOLD_TO_CREDITS_CONVERSION_RATE = 400
CREDITS_TO_GOLD_CONVERSION_RATE = 1.0 / GOLD_TO_CREDITS_CONVERSION_RATE

class SeasonRentDuration(object):
    ENTIRE_SEASON = 1
    SEASON_CYCLE = 2


RENT_TYPE_TO_DURATION = {'season': SeasonRentDuration.ENTIRE_SEASON,
 'cycle': SeasonRentDuration.SEASON_CYCLE}

def makeRentID(rentType, packageID):
    return (rentType << 28) + packageID


def parseRentID(rentID):
    packageId = rentID & 268435455
    rentType = rentID >> 28
    return (rentType, packageId)


def calculateSeasonRentPrice(priceForLastCycle, priceForSeason, currentCycleIdx, numCycles):
    creditsPerCycle = float(priceForLastCycle[0] + priceForLastCycle[1] * GOLD_TO_CREDITS_CONVERSION_RATE)
    creditsPerSeason = float(priceForSeason[0] + priceForSeason[1] * GOLD_TO_CREDITS_CONVERSION_RATE)
    if currentCycleIdx == 0:
        return priceForSeason
    if numCycles <= 1 or currentCycleIdx + 1 == numCycles:
        if priceForSeason[0] > 0:
            return (int(creditsPerCycle), 0)
        else:
            return (0, int(creditsPerCycle * CREDITS_TO_GOLD_CONVERSION_RATE))
    sumCyclesCost = creditsPerCycle * numCycles
    cycleFactor = float(currentCycleIdx) / (numCycles - 1.0)
    seasonFactor = 1.0 - cycleFactor
    timeLeftFactor = numCycles - currentCycleIdx
    creditsSeasonPrice = (sumCyclesCost * cycleFactor + creditsPerSeason * seasonFactor) / numCycles * timeLeftFactor
    if creditsPerSeason < creditsSeasonPrice:
        creditsSeasonPrice = creditsPerSeason
    if priceForSeason[0] > 0:
        return (int(creditsSeasonPrice), 0)
    else:
        return (0, int(creditsSeasonPrice * CREDITS_TO_GOLD_CONVERSION_RATE))


def isWithinMaxRentTime(maxRentDuration, rentLeftTime, daysToRent):
    return maxRentDuration - rentLeftTime >= daysToRent * 86400
