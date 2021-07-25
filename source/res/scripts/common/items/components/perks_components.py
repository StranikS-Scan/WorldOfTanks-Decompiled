# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/components/perks_components.py
from collections import namedtuple
import typing
from items.components.perks_constants import PERKS_TYPE, PerkMasks, PerkTags
from soft_exception import SoftException
PerkArgumentUISettings = namedtuple('PerkArgumentUISettings', ('type', 'revert', 'situationalArg', 'equipmentCooldown', 'localeFormatting', 'perkTooltipBonus', 'icon'))
PerkArgument = namedtuple('PerkArgument', ('value', 'postValues', 'diminishingStartsAfter', 'maxStacks', 'UISettings'))

def convertPerksListToDict(perksList):
    return {perksList[i]:perksList[i + 1] for i in range(0, len(perksList), 2)}


def convertPerksDictToList(perksDict):
    return list(reduce(lambda t1, t2: t1 + t2, perksDict.iteritems()))


def packPerk(perkID, level):
    return (level & PerkMasks.PERK_LEVEL_MASK) << 10 | perkID & PerkMasks.PERK_ID_MASK


def unpackPerk(val):
    return (val & PerkMasks.PERK_ID_MASK, val >> 10 & PerkMasks.PERK_LEVEL_MASK)


class Perk(object):
    __slots__ = ('id', 'flags', 'perkType', 'situational', 'defaultBlockSettings')

    def __init__(self, ID, flags, ultimative, situational, args):
        self.id = ID
        self.flags = flags
        self.perkType = PERKS_TYPE.CONFIGURATION_MAPPING[ultimative]
        self.situational = situational
        self.defaultBlockSettings = args

    @property
    def isAutoperk(self):
        return bool(self.flags & PerkTags.AUTOPERK)

    def getArgBonusByLevel(self, argName, perkLevel):
        argRecord = self.defaultBlockSettings.get(argName)
        if not argRecord:
            raise SoftException('Perk item do not contain argument {}'.format(argName))
        simpleLevel = min(perkLevel, argRecord.diminishingStartsAfter)
        value = argRecord.value * simpleLevel
        postValues = argRecord.postValues
        postLevel = min(perkLevel - simpleLevel, len(postValues))
        if postLevel > 0:
            value += sum((postValues[i] for i in xrange(postLevel)))
        overloadLevel = perkLevel - simpleLevel - postLevel
        if overloadLevel > 0:
            overloadValue = postValues[-1] if postValues else argRecord.value
            value += overloadValue * overloadLevel
        return value


class PerksCache(object):
    __slots__ = ('perks',)

    def __init__(self):
        self.perks = {}

    def getPerksOfType(self, perkType):
        return filter(lambda itemID: self.perks[itemID].perkType == perkType, self.perks.iterkeys())

    def validatePerk(self, itemID, isUltimative=None):
        item = self.perks.get(itemID, None)
        if item is None:
            return (False, 'perk {} not found'.format(itemID))
        else:
            return (False, 'perk {} wrong ultimate'.format(itemID)) if isUltimative is not None and PERKS_TYPE.CONFIGURATION_MAPPING[isUltimative] != item.perkType else (True, '')
