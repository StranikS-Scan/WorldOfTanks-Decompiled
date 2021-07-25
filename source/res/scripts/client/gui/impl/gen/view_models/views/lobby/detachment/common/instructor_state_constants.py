# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/common/instructor_state_constants.py
from frameworks.wulf import ViewModel

class InstructorStateConstants(ViewModel):
    __slots__ = ()
    TOKEN = 'token'
    ASSIGNED = 'assigned'
    IN_BATTLE = 'inBattle'
    IN_SQUAD = 'inSquad'
    REMOVED = 'removed'
    NOT_CONVERTED = 'notConverted'

    def __init__(self, properties=0, commands=0):
        super(InstructorStateConstants, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(InstructorStateConstants, self)._initialize()
