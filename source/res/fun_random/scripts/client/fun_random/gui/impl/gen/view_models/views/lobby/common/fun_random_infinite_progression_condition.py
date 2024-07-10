# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/gen/view_models/views/lobby/common/fun_random_infinite_progression_condition.py
from fun_random.gui.impl.gen.view_models.views.lobby.common.fun_random_progression_condition import FunRandomProgressionCondition

class FunRandomInfiniteProgressionCondition(FunRandomProgressionCondition):
    __slots__ = ()

    def __init__(self, properties=10, commands=0):
        super(FunRandomInfiniteProgressionCondition, self).__init__(properties=properties, commands=commands)

    def getCompleteCount(self):
        return self._getNumber(8)

    def setCompleteCount(self, value):
        self._setNumber(8, value)

    def getPrevCompleteCount(self):
        return self._getNumber(9)

    def setPrevCompleteCount(self, value):
        self._setNumber(9, value)

    def _initialize(self):
        super(FunRandomInfiniteProgressionCondition, self)._initialize()
        self._addNumberProperty('completeCount', -1)
        self._addNumberProperty('prevCompleteCount', -1)
