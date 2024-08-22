# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/comp7/tooltips/style3d_tooltip_model.py
from frameworks.wulf import ViewModel

class Style3dTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(Style3dTooltipModel, self).__init__(properties=properties, commands=commands)

    def getStyleId(self):
        return self._getNumber(0)

    def setStyleId(self, value):
        self._setNumber(0, value)

    def getVehicles(self):
        return self._getString(1)

    def setVehicles(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(Style3dTooltipModel, self)._initialize()
        self._addNumberProperty('styleId', 0)
        self._addStringProperty('vehicles', '')
