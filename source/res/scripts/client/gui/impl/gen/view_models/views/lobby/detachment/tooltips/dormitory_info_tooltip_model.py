# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/tooltips/dormitory_info_tooltip_model.py
from frameworks.wulf import ViewModel

class DormitoryInfoTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(DormitoryInfoTooltipModel, self).__init__(properties=properties, commands=commands)

    def getHangarDorms(self):
        return self._getNumber(0)

    def setHangarDorms(self, value):
        self._setNumber(0, value)

    def getExtraDorms(self):
        return self._getNumber(1)

    def setExtraDorms(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(DormitoryInfoTooltipModel, self)._initialize()
        self._addNumberProperty('hangarDorms', 0)
        self._addNumberProperty('extraDorms', 0)
