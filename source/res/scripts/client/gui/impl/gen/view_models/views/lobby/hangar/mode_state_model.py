# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/hangar/mode_state_model.py
from frameworks.wulf import ViewModel

class ModeStateModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(ModeStateModel, self).__init__(properties=properties, commands=commands)

    def getHasSuitableVehicles(self):
        return self._getBool(0)

    def setHasSuitableVehicles(self, value):
        self._setBool(0, value)

    def _initialize(self):
        super(ModeStateModel, self)._initialize()
        self._addBoolProperty('hasSuitableVehicles', False)
