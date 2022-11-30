# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/ny_constants.py
from enum import Enum, IntEnum
from frameworks.wulf import ViewModel

class CollectionName(Enum):
    UNDEFINED = 'undefined'
    NEWYEAR = 'NewYear'
    CHRISTMAS = 'Christmas'
    FAIRYTALE = 'Fairytale'
    ORIENTAL = 'Oriental'
    SOVIET = 'soviet'
    TRADITIONALWESTERN = 'traditionalWestern'
    MODERNWESTERN = 'modernWestern'
    ASIAN = 'asian'
    MEGA = 'Mega'
    GIFTSYSTEM = 'GiftSystem'


class Resource(Enum):
    CRYSTAL = 'ny_crystal'
    EMERALD = 'ny_emerald'
    AMBER = 'ny_amber'
    IRON = 'ny_iron'


class EconomicBonus(Enum):
    XP = 'xpFactor'
    TANKMENXP = 'tankmenXPFactor'
    FREEXP = 'freeXPFactor'
    CREDITS = 'creditsFactor'


class RewardKit(Enum):
    NEWYEAR = 'NewYear'
    CHRISTMAS = 'Christmas'
    FAIRYTALE = 'Fairytale'
    ORIENTAL = 'Oriental'


class TutorialStates(IntEnum):
    INTRO = 0
    WIDGET = 1
    UI = 2
    FINISHED = 3


class NyConstants(ViewModel):
    __slots__ = ()

    def __init__(self, properties=0, commands=0):
        super(NyConstants, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(NyConstants, self)._initialize()
