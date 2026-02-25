# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/vehicle_hub/views/sub_models/minor_short_tooltip_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen import R

class MinorShortTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(MinorShortTooltipModel, self).__init__(properties=properties, commands=commands)

    def getIcon(self):
        return self._getResource(0)

    def setIcon(self, value):
        self._setResource(0, value)

    def getHeader(self):
        return self._getString(1)

    def setHeader(self, value):
        self._setString(1, value)

    def getDescription(self):
        return self._getString(2)

    def setDescription(self, value):
        self._setString(2, value)

    def _initialize(self):
        super(MinorShortTooltipModel, self)._initialize()
        self._addResourceProperty('icon', R.invalid())
        self._addStringProperty('header', '')
        self._addStringProperty('description', '')
