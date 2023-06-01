# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/achievements/achievements_constants.py
from enum import Enum
from frameworks.wulf import ViewModel

class KPITypes(Enum):
    BATTLES = 'battles'
    ASSISTANCE = 'assistance'
    DESTROYED = 'destroyed'
    BLOCKED = 'blocked'
    EXPERIENCE = 'experience'
    DAMAGE = 'damage'


class AchievementsConstants(ViewModel):
    __slots__ = ()

    def __init__(self, properties=0, commands=0):
        super(AchievementsConstants, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(AchievementsConstants, self)._initialize()
