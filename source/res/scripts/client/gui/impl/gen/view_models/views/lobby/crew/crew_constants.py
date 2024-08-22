# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/crew_constants.py
from enum import Enum
from frameworks.wulf import ViewModel

class Color(Enum):
    BLACKREAL = 'blackReal'
    WHITEREAL = 'whiteReal'
    WHITE = 'white'
    WHITEORANGE = 'whiteOrange'
    WHITESPANISH = 'whiteSpanish'
    PAR = 'par'
    PARSECONDARY = 'parSecondary'
    PARTERTIARY = 'parTertiary'
    RED = 'red'
    REDDARK = 'redDark'
    YELLOW = 'yellow'
    ORANGE = 'orange'
    CREAM = 'cream'
    BROWN = 'brown'
    GREENBRIGHT = 'greenBright'
    GREEN = 'green'
    GREENDARK = 'greenDark'
    BLUEBOOSTER = 'blueBooster'
    BLUETEAMKILLER = 'blueTeamkiller'
    CRED = 'cred'
    GOLD = 'gold'
    BOND = 'bond'
    PROM = 'prom'


class CrewConstants(ViewModel):
    __slots__ = ()
    DONT_SHOW_LEVEL = -1
    SKILL_EFFICIENCY_UNTRAINED = -1
    SKILL_EFFICIENCY_MAX_LEVEL = 1
    SKILL_MAX_LEVEL = 100
    SKILL_MIN_LEVEL = 0
    NEW_SKILL = 'new_skill'
    MAX_FULL_SKILLS_FOR_DISCOUNT = 1
    MAX_BONUS_SKILLS_AMOUNT = 9
    MAX_MAJOR_SKILLS_AMOUNT = 6
    NO_TANKMAN = -1

    def __init__(self, properties=0, commands=0):
        super(CrewConstants, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(CrewConstants, self)._initialize()
