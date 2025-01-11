# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/tooltips/ny_decoration_unavailable_tooltip_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class NyDecorationUnavailableTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(NyDecorationUnavailableTooltipModel, self).__init__(properties=properties, commands=commands)

    def getType(self):
        return self._getString(0)

    def setType(self, value):
        self._setString(0, value)

    def getToyName(self):
        return self._getResource(1)

    def setToyName(self, value):
        self._setResource(1, value)

    def getDropSource(self):
        return self._getString(2)

    def setDropSource(self, value):
        self._setString(2, value)

    def _initialize(self):
        super(NyDecorationUnavailableTooltipModel, self)._initialize()
        self._addStringProperty('type', '')
        self._addResourceProperty('toyName', R.invalid())
        self._addStringProperty('dropSource', '')
