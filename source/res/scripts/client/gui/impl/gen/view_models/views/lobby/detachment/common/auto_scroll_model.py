# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/common/auto_scroll_model.py
from frameworks.wulf import ViewModel

class AutoScrollModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(AutoScrollModel, self).__init__(properties=properties, commands=commands)

    def getIndex(self):
        return self._getNumber(0)

    def setIndex(self, value):
        self._setNumber(0, value)

    def getId(self):
        return self._getNumber(1)

    def setId(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(AutoScrollModel, self)._initialize()
        self._addNumberProperty('index', 0)
        self._addNumberProperty('id', 0)
