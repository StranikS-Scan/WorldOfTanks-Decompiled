# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/tooltips/ny_decoration_state_tooltip_model.py
from frameworks.wulf import ViewModel

class NyDecorationStateTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(NyDecorationStateTooltipModel, self).__init__(properties=properties, commands=commands)

    def getAtmosphereBonus(self):
        return self._getNumber(0)

    def setAtmosphereBonus(self, value):
        self._setNumber(0, value)

    def getDescription(self):
        return self._getString(1)

    def setDescription(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(NyDecorationStateTooltipModel, self)._initialize()
        self._addNumberProperty('atmosphereBonus', 0)
        self._addStringProperty('description', '')
