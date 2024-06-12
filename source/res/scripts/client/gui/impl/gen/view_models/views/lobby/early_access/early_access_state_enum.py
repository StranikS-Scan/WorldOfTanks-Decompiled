# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/early_access/early_access_state_enum.py
from enum import Enum
from frameworks.wulf import ViewModel

class State(Enum):
    ACTIVE = 'active'
    POSTPROGRESSION = 'postProgression'
    BUY = 'buy'
    COMPLETED = 'completed'


class EarlyAccessStateEnum(ViewModel):
    __slots__ = ()

    def __init__(self, properties=0, commands=0):
        super(EarlyAccessStateEnum, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(EarlyAccessStateEnum, self)._initialize()
