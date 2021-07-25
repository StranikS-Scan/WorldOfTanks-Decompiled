# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/common/recruit_constants.py
from frameworks.wulf import ViewModel

class RecruitConstants(ViewModel):
    __slots__ = ()
    IN_BATTLE = 'inBattle'
    IN_PLATOON = 'inPlatoon'
    ON_VEHICLE = 'onVehicle'
    DISMISSED = 'dismissed'
    IN_BARRACK = 'inBarrack'
    DEFAULT = 'default'
    LEADER = 'leader'
    INSTRUCTOR = 'instructor'
    INEXPERIENCED = 'inexperienced'

    def __init__(self, properties=0, commands=0):
        super(RecruitConstants, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(RecruitConstants, self)._initialize()
