# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/sub_views/shell_mechanic_column_config_model.py
from frameworks.wulf import ViewModel

class ShellMechanicColumnConfigModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(ShellMechanicColumnConfigModel, self).__init__(properties=properties, commands=commands)

    def getState(self):
        return self._getString(0)

    def setState(self, value):
        self._setString(0, value)

    def getSubtype(self):
        return self._getString(1)

    def setSubtype(self, value):
        self._setString(1, value)

    def getWithTextLabel(self):
        return self._getBool(2)

    def setWithTextLabel(self, value):
        self._setBool(2, value)

    def getWithRichTooltip(self):
        return self._getBool(3)

    def setWithRichTooltip(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(ShellMechanicColumnConfigModel, self)._initialize()
        self._addStringProperty('state', '')
        self._addStringProperty('subtype', '')
        self._addBoolProperty('withTextLabel', False)
        self._addBoolProperty('withRichTooltip', True)
