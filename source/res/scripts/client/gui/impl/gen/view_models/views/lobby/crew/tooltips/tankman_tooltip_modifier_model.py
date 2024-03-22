# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/tooltips/tankman_tooltip_modifier_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class TankmanTooltipModifierModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(TankmanTooltipModifierModel, self).__init__(properties=properties, commands=commands)

    def getValue(self):
        return self._getReal(0)

    def setValue(self, value):
        self._setReal(0, value)

    def getIcon(self):
        return self._getResource(1)

    def setIcon(self, value):
        self._setResource(1, value)

    def getTitle(self):
        return self._getString(2)

    def setTitle(self, value):
        self._setString(2, value)

    def getDescription(self):
        return self._getString(3)

    def setDescription(self, value):
        self._setString(3, value)

    def _initialize(self):
        super(TankmanTooltipModifierModel, self)._initialize()
        self._addRealProperty('value', 0.0)
        self._addResourceProperty('icon', R.invalid())
        self._addStringProperty('title', '')
        self._addStringProperty('description', '')
