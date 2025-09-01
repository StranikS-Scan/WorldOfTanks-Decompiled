# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: one_time_gift/scripts/common/one_time_gift_common/one_time_gift_branches_config.py
import ResMgr
import typing
from items.vehicles import makeVehicleTypeCompDescrByName, getVehicleType
from soft_exception import SoftException
from one_time_gift_common.one_time_gift_constants import OTG_BRANCHES_CONFIG_PATH, BRANCHES
if typing.TYPE_CHECKING:
    from typing import Dict, List, Tuple, Set
    VehCD = int
g_oneTimeGiftBranchesCfg = {}

def readOneTimeGiftBranchesConfig():
    section = ResMgr.openSection(OTG_BRANCHES_CONFIG_PATH)
    return _readConfig(section)


def _readConfig(section):
    if section is None:
        raise SoftException('Branches config is not found!')
    branchesSection = section['branches']
    if branchesSection is None:
        raise SoftException('Branches section is not found!')
    if set(branchesSection.keys()) != BRANCHES or len(branchesSection.keys()) != len(BRANCHES):
        raise SoftException('Branches section has wrong keys! {}'.format(branchesSection.keys()))
    result = {}
    for branchName in BRANCHES:
        parsedBranches = set()
        branchSubsection = branchesSection[branchName]
        if branchSubsection is None:
            raise SoftException('Branch {} is not found!'.format(branchName))
        if branchSubsection.keys() and set(branchSubsection.keys()) != {'branch'}:
            raise SoftException("Branch '{}' is not valid! Branch subsetion can have only 'branch' items.".format(branchName))
        for item in branchSubsection.values():
            branch = parseBranch(item)
            parsedBranches.add(branch)

        result[branchName] = parsedBranches

    return result


def parseBranch(branchSection):
    branchVehicles = branchSection.readString('').split()
    branch = tuple((makeVehicleTypeCompDescrByName(vehicle) for vehicle in branchVehicles))
    for index in range(len(branch) - 1):
        vehicleIntCD = branch[index]
        nextVehIntCD = branch[index + 1]
        vehType = getVehicleType(vehicleIntCD)
        if nextVehIntCD not in [ unlockDescr[1] for unlockDescr in vehType.unlocksDescrs ]:
            raise SoftException('Branch {} is not valid. Vehicle {} can not be unlocked by vehicle {}!'.format(branchSection.readString(''), nextVehIntCD, vehicleIntCD))

    return branch


def loadOneTimeGiftBranchesCfg():
    global g_oneTimeGiftBranchesCfg
    if not g_oneTimeGiftBranchesCfg:
        g_oneTimeGiftBranchesCfg = readOneTimeGiftBranchesConfig()


def getOneTimeGiftBranchesCfg():
    if not g_oneTimeGiftBranchesCfg:
        loadOneTimeGiftBranchesCfg()
    return g_oneTimeGiftBranchesCfg
