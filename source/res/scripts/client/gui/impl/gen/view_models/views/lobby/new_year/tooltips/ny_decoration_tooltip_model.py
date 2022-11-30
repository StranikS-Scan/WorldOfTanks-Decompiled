# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/tooltips/ny_decoration_tooltip_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class NyDecorationTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(NyDecorationTooltipModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getResource(0)

    def setName(self, value):
        self._setResource(0, value)

    def getDescription(self):
        return self._getResource(1)

    def setDescription(self, value):
        self._setResource(1, value)

    def getCount(self):
        return self._getNumber(2)

    def setCount(self, value):
        self._setNumber(2, value)

    def getType(self):
        return self._getString(3)

    def setType(self, value):
        self._setString(3, value)

    def getIcon(self):
        return self._getResource(4)

    def setIcon(self, value):
        self._setResource(4, value)

    def _initialize(self):
        super(NyDecorationTooltipModel, self)._initialize()
        self._addResourceProperty('name', R.invalid())
        self._addResourceProperty('description', R.invalid())
        self._addNumberProperty('count', 0)
        self._addStringProperty('type', '')
        self._addResourceProperty('icon', R.invalid())
