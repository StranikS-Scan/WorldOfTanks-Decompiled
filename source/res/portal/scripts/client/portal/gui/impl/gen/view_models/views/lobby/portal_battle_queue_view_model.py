# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/impl/gen/view_models/views/lobby/portal_battle_queue_view_model.py
from enum import IntEnum
from frameworks.wulf import ViewModel

class Complexity(IntEnum):
    EASY = 1
    MEDIUM = 2
    HARD = 3
    EXPERT = 4
    MASTER = 5


class PortalBattleQueueViewModel(ViewModel):
    __slots__ = ('onLeave',)

    def __init__(self, properties=1, commands=1):
        super(PortalBattleQueueViewModel, self).__init__(properties=properties, commands=commands)

    def getComplexity(self):
        return Complexity(self._getNumber(0))

    def setComplexity(self, value):
        self._setNumber(0, value.value)

    def _initialize(self):
        super(PortalBattleQueueViewModel, self)._initialize()
        self._addNumberProperty('complexity')
        self.onLeave = self._addCommand('onLeave')
