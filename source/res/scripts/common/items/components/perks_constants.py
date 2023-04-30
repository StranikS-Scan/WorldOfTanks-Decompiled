# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/components/perks_constants.py
import typing
PERKS_XML_FILE = 'perks.xml'
PERK_BONUS_VALUE_PRECISION = 5

class PerkState(object):
    INACTIVE = 0
    ACTIVE = 1


class CrewPerkLevelCollectors(object):
    MAX = 0
    AVERAGE = 1
    AVERAGE_ALL = 2


class PerkTags(object):
    AUTOPERK = 4

    @classmethod
    def pack(cls, tags):
        return reduce(int.__or__, (getattr(cls, tag.upper()) for tag in tags), 0)


class PerkMasks(object):
    PERK_ID_MASK = 1023
    PERK_LEVEL_MASK = 63


class StubPerkIDs(object):
    COMMANDER_UNIVERSALIST = 102
    RADIOMAN_LAST_EFFORT = 504
