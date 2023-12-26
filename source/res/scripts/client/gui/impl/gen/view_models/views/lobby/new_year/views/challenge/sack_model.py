# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/challenge/sack_model.py
from frameworks.wulf import ViewModel

class SackModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(SackModel, self).__init__(properties=properties, commands=commands)

    def getLevel(self):
        return self._getNumber(0)

    def setLevel(self, value):
        self._setNumber(0, value)

    def getCount(self):
        return self._getNumber(1)

    def setCount(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(SackModel, self)._initialize()
        self._addNumberProperty('level', 0)
        self._addNumberProperty('count', 0)
