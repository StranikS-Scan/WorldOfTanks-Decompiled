# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/components/perks_components.py
import typing
from items.components.perks_constants import PERKS_TYPE
from soft_exception import SoftException

class Perk(object):
    __slots__ = ('id', 'name', 'description', 'icon', 'branchID', 'perkType', 'maxCount', 'situational')

    def __init__(self, ID, name, description, iconID, branchID, ultimative, maxCount, situational):
        self.id = ID
        self.name = name
        self.description = description
        self.icon = iconID
        self.branchID = branchID
        self.perkType = PERKS_TYPE.CONFIGURATION_MAPPING[ultimative]
        self.maxCount = maxCount
        self.situational = situational


class PerksBranch(object):
    __slots__ = ('id', 'name', 'needPoints', 'perkIDs')

    def __init__(self, ID, name, needPoints):
        self.id = ID
        self.name = name
        self.needPoints = needPoints
        self.perkIDs = []


class PerksCache(object):
    __slots__ = ('perks', 'branches')

    def __init__(self):
        self.perks = {}
        self.branches = {}

    def attachPerksToBranches(self):
        for key, item in self.perks.iteritems():
            branch = self.branches.get(item.branchID)
            if branch is not None:
                branch.perkIDs.append(key)
            if item.branchID:
                raise SoftException('PerksCache.attachPerksToBranches: wrong branch ID in perk {}'.format(key))

        return

    def getPerksOfBranch(self, branchID):
        if branchID not in self.branches:
            return None
        else:
            branchPerks = {}
            for perkID in self.branches[branchID].perkIDs:
                perkItem = self.perks[perkID]
                perkType = perkItem.perkType
                perks = branchPerks.setdefault(perkType, [])
                perks.append(perkID)

            return branchPerks

    def getPerksOfType(self, perkType):
        return filter(lambda itemID: self.perks[itemID].perkType == perkType, self.perks.iterkeys())

    def validatePerk(self, itemID):
        item = self.perks.get(itemID, None)
        return (False, 'perk {} not found'.format(itemID)) if item is None else (True, '')
