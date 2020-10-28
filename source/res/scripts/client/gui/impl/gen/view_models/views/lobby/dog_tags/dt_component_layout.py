# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/dog_tags/dt_component_layout.py
from frameworks.wulf import ViewModel

class DtComponentLayout(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(DtComponentLayout, self).__init__(properties=properties, commands=commands)

    def getMarginX(self):
        return self._getReal(0)

    def setMarginX(self, value):
        self._setReal(0, value)

    def getMarginY(self):
        return self._getReal(1)

    def setMarginY(self, value):
        self._setReal(1, value)

    def _initialize(self):
        super(DtComponentLayout, self)._initialize()
        self._addRealProperty('marginX', 0.0)
        self._addRealProperty('marginY', 0.0)
