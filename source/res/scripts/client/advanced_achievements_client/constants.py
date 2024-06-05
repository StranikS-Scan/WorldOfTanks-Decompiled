# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/advanced_achievements_client/constants.py
from enum import Enum

class AchievementType(Enum):
    REGULAR = 'regular'
    STEPPED = 'stepped'
    CUMULATIVE = 'cumulative'
    SUBCATEGORY = 'subcategory'


NEAREST_REQUIRED_COUNT = 3
TROPHIES_ACHIEVEMENT_ID = -1
BONUS_PRIORITY_MAP = {'dogTagComponents': 1,
 'customizations': 2}
