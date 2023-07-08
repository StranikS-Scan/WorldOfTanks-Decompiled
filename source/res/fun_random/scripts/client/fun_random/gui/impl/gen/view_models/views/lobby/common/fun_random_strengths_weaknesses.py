# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/gen/view_models/views/lobby/common/fun_random_strengths_weaknesses.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from fun_random.gui.impl.gen.view_models.views.lobby.common.fun_random_vehicle_parameter import FunRandomVehicleParameter

class FunRandomStrengthsWeaknesses(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(FunRandomStrengthsWeaknesses, self).__init__(properties=properties, commands=commands)

    def getStrengths(self):
        return self._getArray(0)

    def setStrengths(self, value):
        self._setArray(0, value)

    @staticmethod
    def getStrengthsType():
        return FunRandomVehicleParameter

    def getWeaknesses(self):
        return self._getArray(1)

    def setWeaknesses(self, value):
        self._setArray(1, value)

    @staticmethod
    def getWeaknessesType():
        return FunRandomVehicleParameter

    def _initialize(self):
        super(FunRandomStrengthsWeaknesses, self)._initialize()
        self._addArrayProperty('strengths', Array())
        self._addArrayProperty('weaknesses', Array())
