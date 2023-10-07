# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/tooltips/training_level_modifiers_model.py
from frameworks.wulf import ViewModel

class TrainingLevelModifiersModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(TrainingLevelModifiersModel, self).__init__(properties=properties, commands=commands)

    def getValue(self):
        return self._getReal(0)

    def setValue(self, value):
        self._setReal(0, value)

    def getReason(self):
        return self._getString(1)

    def setReason(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(TrainingLevelModifiersModel, self)._initialize()
        self._addRealProperty('value', 0.0)
        self._addStringProperty('reason', '')
