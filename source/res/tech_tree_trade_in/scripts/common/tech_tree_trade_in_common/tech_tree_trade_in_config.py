# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tech_tree_trade_in/scripts/common/tech_tree_trade_in_common/tech_tree_trade_in_config.py
import ResMgr
import nations
from copy import copy
from dossiers2.custom.cache import getCache
from items.vehicles import makeVehicleTypeCompDescrByName, getUnlocksSources
from tech_tree_trade_in_constants import TRADING_BRANCHES_CONFIG_PATH, MIN_TRADE_LEVEL, MAX_TRADE_LEVEL
g_tradeInVehiclesCfg = {}

def readTradingBranchesConfig():
    section = ResMgr.openSection(TRADING_BRANCHES_CONFIG_PATH)
    branchesToTradeBlacklistSubsection = section['branches']['branchesToTradeBlacklist']
    branchesToReceiveWhitelistSubsection = section['branches']['branchesToReceiveWhitelist']
    allBranches, multy10 = getAllTechTreeBranches()
    branchesToTrade = set()
    branchesToReceive = set()
    branchesToTradeBlacklist = []
    for branchToTradeBlacklist in branchesToTradeBlacklistSubsection.values():
        branchesToTradeBlacklist.append(parseBranch(branchToTradeBlacklist))

    for branchToTrade in allBranches:
        if branchToTrade not in branchesToTradeBlacklist:
            branchesToTrade.add(tuple(branchToTrade))

    for branchToReceive in branchesToReceiveWhitelistSubsection.values():
        branchesToReceive.add(tuple(parseBranch(branchToReceive)))

    return {'branches': {'branchesToTrade': branchesToTrade,
                  'branchesToReceive': branchesToReceive,
                  'allBranches': allBranches,
                  'multy10': multy10},
     'vehicleExperienceStorage': {nations.INDICES[vehicle.asString.split(':')[0]]:vehicle.asString for vehicle in section['vehicleExperienceStorage'].values()}}


def getAllTechTreeBranches():
    vehiclesInTreesByNation = getCache()['vehiclesInTreesByNation']
    maxLevelVehicles = getCache()['vehiclesByLevel'][MAX_TRADE_LEVEL]
    maxLevelUnlockableVehicles = [ maxLevelVehicles.intersection(vehiclesInTrees) for vehiclesInTrees in vehiclesInTreesByNation.values() ]
    unlockSourcesCache = getUnlocksSources()
    allBranches = []
    multy10 = set()
    all10 = set()
    for nation in maxLevelUnlockableVehicles:
        for vehicle in nation:
            branches = processTree(unlockSourcesCache, vehicle)
            for branch in branches:
                branch.reverse()
                allBranches.append(branch)
                if branch[-1] in all10:
                    multy10.add(branch[-1])
                all10.add(branch[-1])

    return (allBranches, multy10)


def processTree(unlockSourcesCache, vehicleIntCD):
    branches = [[vehicleIntCD]]
    for _ in range(MAX_TRADE_LEVEL - MIN_TRADE_LEVEL):
        currentBranches = copy(branches)
        for branchIdx, branch in enumerate(currentBranches):
            prevVehTypes = unlockSourcesCache.get(branch[-1])
            for vehTypeIdx, prevVehType in enumerate(prevVehTypes):
                if vehTypeIdx:
                    branches.append(copy(branch[:-1]))
                    branches[len(branches) - 1].append(prevVehType.compactDescr)
                branches[branchIdx].append(prevVehType.compactDescr)

        del currentBranches

    return branches


def parseBranch(branch):
    branchVehicles = branch.readString('').split()
    vehTypeCompDescrs = [ makeVehicleTypeCompDescrByName(vehicle) for vehicle in branchVehicles ]
    return vehTypeCompDescrs


def loadTradeInVehiclesCfg():
    global g_tradeInVehiclesCfg
    if not g_tradeInVehiclesCfg:
        g_tradeInVehiclesCfg = readTradingBranchesConfig()


def getTradeInVehiclesCfg():
    if not g_tradeInVehiclesCfg:
        loadTradeInVehiclesCfg()
    return g_tradeInVehiclesCfg
