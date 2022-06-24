# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/research/sold_module_info_tooltip_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class SoldModuleInfoTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(SoldModuleInfoTooltipModel, self).__init__(properties=properties, commands=commands)

    def getCompatibleTanks(self):
        return self._getArray(0)

    def setCompatibleTanks(self, value):
        self._setArray(0, value)

    @staticmethod
    def getCompatibleTanksType():
        return str

    def _initialize(self):
        super(SoldModuleInfoTooltipModel, self)._initialize()
        self._addArrayProperty('compatibleTanks', Array())
