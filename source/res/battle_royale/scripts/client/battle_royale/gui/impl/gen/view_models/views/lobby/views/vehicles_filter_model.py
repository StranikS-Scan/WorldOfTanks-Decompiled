# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/gen/view_models/views/lobby/views/vehicles_filter_model.py
from frameworks.wulf import Array, ViewModel

class VehiclesFilterModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(VehiclesFilterModel, self).__init__(properties=properties, commands=commands)

    def getCarouselRowCount(self):
        return self._getNumber(0)

    def setCarouselRowCount(self, value):
        self._setNumber(0, value)

    def getNationsOrder(self):
        return self._getArray(1)

    def setNationsOrder(self, value):
        self._setArray(1, value)

    @staticmethod
    def getNationsOrderType():
        return unicode

    def _initialize(self):
        super(VehiclesFilterModel, self)._initialize()
        self._addNumberProperty('carouselRowCount', -1)
        self._addArrayProperty('nationsOrder', Array())
