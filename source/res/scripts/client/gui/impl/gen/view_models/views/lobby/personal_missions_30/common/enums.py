# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/personal_missions_30/common/enums.py
from enum import Enum

class MissionCategory(Enum):
    ASSAULT = 'assault'
    SNIPER = 'sniper'
    SUPPORT = 'support'


class OperationState(Enum):
    COMPLETED_WITH_HONORS = 'completedWithHonors'
    COMPLETED = 'completed'
    ACTIVE = 'active'
    AVAILABLE = 'available'
    UNAVAILABLE = 'unavailable'
    LOCKED = 'locked'


class ParamTooltipType(Enum):
    PROGRESSION = 'progression'
    PM3_POINTS = 'pm3_points'
    CUSTOM_SIMPLE = 'custom_simple'
