# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: open_bundle/scripts/client/open_bundle/gui/impl/gen/view_models/views/lobby/coordinate_model.py
from frameworks.wulf import ViewModel

class CoordinateModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(CoordinateModel, self).__init__(properties=properties, commands=commands)

    def getX(self):
        return self._getNumber(0)

    def setX(self, value):
        self._setNumber(0, value)

    def getY(self):
        return self._getNumber(1)

    def setY(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(CoordinateModel, self)._initialize()
        self._addNumberProperty('x', 0)
        self._addNumberProperty('y', 0)
