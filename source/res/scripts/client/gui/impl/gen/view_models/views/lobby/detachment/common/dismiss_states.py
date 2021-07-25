# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/common/dismiss_states.py
from frameworks.wulf import ViewModel

class DismissStates(ViewModel):
    __slots__ = ()
    AVAILABLE = 'available'
    SELL_LIMIT_REACHED = 'sellLimitReached'
    HAS_LOCK_CREW = 'hasLockCrew'
    DISABLE = 'disable'

    def __init__(self, properties=0, commands=0):
        super(DismissStates, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(DismissStates, self)._initialize()
