# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/vehicle_hub/views/sub_models/field_modification_model.py
from frameworks.wulf import ViewModel

class FieldModificationModel(ViewModel):
    __slots__ = ('onVehiclePostProgression',)
    HIDDEN = 0
    LOCKED = 1
    UNLOCKED = 2

    def __init__(self, properties=2, commands=1):
        super(FieldModificationModel, self).__init__(properties=properties, commands=commands)

    def getState(self):
        return self._getNumber(0)

    def setState(self, value):
        self._setNumber(0, value)

    def getCounter(self):
        return self._getNumber(1)

    def setCounter(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(FieldModificationModel, self)._initialize()
        self._addNumberProperty('state', 0)
        self._addNumberProperty('counter', 0)
        self.onVehiclePostProgression = self._addCommand('onVehiclePostProgression')
