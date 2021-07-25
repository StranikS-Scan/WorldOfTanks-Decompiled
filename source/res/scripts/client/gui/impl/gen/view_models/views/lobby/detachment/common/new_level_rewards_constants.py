# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/common/new_level_rewards_constants.py
from frameworks.wulf import ViewModel

class NewLevelRewardsConstants(ViewModel):
    __slots__ = ()
    SKILL_POINT = 'SKILL_POINT'
    INSTRUCTOR_SLOT = 'INSTRUCTOR_SLOT'
    VEHICLE_SLOT = 'VEHICLE_SLOT'
    PROGRESSION_DISCOUNT = 'PROGRESSION_DISCOUNT'
    VEHICLE_PROFICIENCY = 'VEHICLE_PROFICIENCY'
    BADGE = 'BADGE'
    RANK = 'RANK'

    def __init__(self, properties=0, commands=0):
        super(NewLevelRewardsConstants, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(NewLevelRewardsConstants, self)._initialize()
