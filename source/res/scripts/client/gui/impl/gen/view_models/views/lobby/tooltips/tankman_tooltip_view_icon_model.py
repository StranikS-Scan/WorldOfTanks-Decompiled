# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tooltips/tankman_tooltip_view_icon_model.py
from frameworks.wulf import ViewModel

class TankmanTooltipViewIconModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(TankmanTooltipViewIconModel, self).__init__(properties=properties, commands=commands)

    def getIcon(self):
        return self._getString(0)

    def setIcon(self, value):
        self._setString(0, value)

    def _initialize(self):
        super(TankmanTooltipViewIconModel, self)._initialize()
        self._addStringProperty('icon', '')
