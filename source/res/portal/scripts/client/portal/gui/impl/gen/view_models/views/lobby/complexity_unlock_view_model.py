# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/impl/gen/view_models/views/lobby/complexity_unlock_view_model.py
from frameworks.wulf import ViewModel

class ComplexityUnlockViewModel(ViewModel):
    __slots__ = ('onApprove',)

    def __init__(self, properties=1, commands=1):
        super(ComplexityUnlockViewModel, self).__init__(properties=properties, commands=commands)

    def getComplexity(self):
        return self._getNumber(0)

    def setComplexity(self, value):
        self._setNumber(0, value)

    def _initialize(self):
        super(ComplexityUnlockViewModel, self)._initialize()
        self._addNumberProperty('complexity', 0)
        self.onApprove = self._addCommand('onApprove')
