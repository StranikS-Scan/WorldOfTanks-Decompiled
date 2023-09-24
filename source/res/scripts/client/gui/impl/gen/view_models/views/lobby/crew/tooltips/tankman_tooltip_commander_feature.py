# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/tooltips/tankman_tooltip_commander_feature.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class TankmanTooltipCommanderFeature(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(TankmanTooltipCommanderFeature, self).__init__(properties=properties, commands=commands)

    def getIcon(self):
        return self._getResource(0)

    def setIcon(self, value):
        self._setResource(0, value)

    def getDescription(self):
        return self._getString(1)

    def setDescription(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(TankmanTooltipCommanderFeature, self)._initialize()
        self._addResourceProperty('icon', R.invalid())
        self._addStringProperty('description', '')
