# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/common/fast_operation_button_state.py
from frameworks.wulf import ViewModel

class FastOperationButtonState(ViewModel):
    __slots__ = ()
    AVAILABLE = 'available'
    ALL_IN_PLACE = 'allInPlace'
    IN_BATTLE = 'inBattle'
    IN_PLATOON = 'inPlatoon'
    LOCK_CREW = 'lockCrew'
    EMPTY = 'empty'
    UNKNOWN = 'unknown'
    DISMISSED = 'dismissed'
    CONVERTED = 'converted'
    RETRAINED = 'retrained'

    def __init__(self, properties=0, commands=0):
        super(FastOperationButtonState, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(FastOperationButtonState, self)._initialize()
