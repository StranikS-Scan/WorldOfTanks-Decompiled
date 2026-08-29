# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/vehicle_hub/special_shell_param_model.py
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.views.lobby.vehicle_hub.shell_model import ShellModel

class SpecialShellParamModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(SpecialShellParamModel, self).__init__(properties=properties, commands=commands)

    def getShellArray(self):
        return self._getArray(0)

    def setShellArray(self, value):
        self._setArray(0, value)

    @staticmethod
    def getShellArrayType():
        return ShellModel

    def _initialize(self):
        super(SpecialShellParamModel, self)._initialize()
        self._addArrayProperty('shellArray', Array())
