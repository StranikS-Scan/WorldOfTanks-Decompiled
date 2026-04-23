# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/common/historical_battles_common/helpers_config.py


def getDivisionExpByLevel(config, divisionID, level):
    levelXps = config['divisions'][divisionID]['levelsXp']
    level = min(max(level - 1, 0), len(levelXps) - 1)
    return levelXps[level]


def getDivisionLevelByExp(config, divisionId, currentXp):
    levelsXp = config['divisions'][divisionId]['levelsXp']
    for i, xp in enumerate(levelsXp):
        if currentXp < xp:
            return i

    return len(levelsXp)


def getDivisionCurrentLevelMaxExp(config, divisionId, currentXp):
    levelsXp = config['divisions'][divisionId]['levelsXp']
    for xp in levelsXp:
        if currentXp < xp:
            return xp

    return levelsXp[-1]


def getFrontIDBySubdivisionID(config, divisionId):
    return config['divisions'][divisionId]['frontID']


def frontBySubdivisionIDIsEnabled(config, divisionId):
    frontID = config['divisions'][divisionId]['frontID']
    return config['fronts'][frontID]['enabled']
