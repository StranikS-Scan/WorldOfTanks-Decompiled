# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/components/perks_constants.py
import typing
PERKS_XML_FILE = 'perks.xml'
PERK_BONUS_VALUE_PRECISION = 5

class PERK_STATE(object):
    INACTIVE = 0
    ACTIVE = 1


class PERKS_TYPE(object):
    SIMPLE = 1
    ULTIMATE = 2
    ANY = SIMPLE | ULTIMATE
    CONFIGURATION_MAPPING = {True: ULTIMATE,
     False: SIMPLE}


class PerkTags(object):
    AUTOPERK = 4

    @classmethod
    def pack(cls, tags):
        return reduce(int.__or__, [ getattr(cls, tag.upper()) for tag in tags ], 0)


class PerksValueType(object):
    PERCENTS = 1
    SECONDS = 2
    ANY = PERCENTS | SECONDS
    CONFIGURATION_MAPPING = {'seconds': SECONDS,
     'percents': PERCENTS,
     '': SECONDS}


class PerkMasks(object):
    PERK_ID_MASK = 1023
    PERK_LEVEL_MASK = 63
