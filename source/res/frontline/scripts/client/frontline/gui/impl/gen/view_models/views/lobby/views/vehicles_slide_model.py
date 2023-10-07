# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/gen/view_models/views/lobby/views/vehicles_slide_model.py
from frameworks.wulf import ViewModel

class VehiclesSlideModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(VehiclesSlideModel, self).__init__(properties=properties, commands=commands)

    def getFromLevel(self):
        return self._getNumber(0)

    def setFromLevel(self, value):
        self._setNumber(0, value)

    def getToLevel(self):
        return self._getNumber(1)

    def setToLevel(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(VehiclesSlideModel, self)._initialize()
        self._addNumberProperty('fromLevel', 0)
        self._addNumberProperty('toLevel', 0)
