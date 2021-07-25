# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/post_progression/base_step_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class ActionType(Enum):
    MODIFICATION = 'modification'
    PAIRMODIFICATION = 'pairModification'
    MODIFICATIONWITHFEATURE = 'modificationWithFeature'


class BaseStepModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(BaseStepModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getNumber(0)

    def setId(self, value):
        self._setNumber(0, value)

    def getActionType(self):
        return ActionType(self._getString(1))

    def setActionType(self, value):
        self._setString(1, value.value)

    def _initialize(self):
        super(BaseStepModel, self)._initialize()
        self._addNumberProperty('id', 0)
        self._addStringProperty('actionType')
