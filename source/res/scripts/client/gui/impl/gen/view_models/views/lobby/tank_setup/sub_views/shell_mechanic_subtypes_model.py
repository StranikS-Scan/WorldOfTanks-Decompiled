# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/sub_views/shell_mechanic_subtypes_model.py
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.shell_mechanic_column_config_model import ShellMechanicColumnConfigModel

class ShellMechanicSubtypesModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(ShellMechanicSubtypesModel, self).__init__(properties=properties, commands=commands)

    def getMechanic(self):
        return self._getString(0)

    def setMechanic(self, value):
        self._setString(0, value)

    def getColumnConfigs(self):
        return self._getArray(1)

    def setColumnConfigs(self, value):
        self._setArray(1, value)

    @staticmethod
    def getColumnConfigsType():
        return ShellMechanicColumnConfigModel

    def _initialize(self):
        super(ShellMechanicSubtypesModel, self)._initialize()
        self._addStringProperty('mechanic', '')
        self._addArrayProperty('columnConfigs', Array())
