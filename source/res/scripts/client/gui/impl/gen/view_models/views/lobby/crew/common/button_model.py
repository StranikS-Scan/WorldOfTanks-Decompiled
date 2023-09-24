# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/common/button_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class ButtonType(Enum):
    CREWOPERATIONS = 'crewOperations'
    CREWBOOKS = 'crewBooks'
    ACCELERATEDTRAINING = 'acceleratedTraining'
    WOTPLUS = 'wotPlus'


class ButtonModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(ButtonModel, self).__init__(properties=properties, commands=commands)

    def getType(self):
        return ButtonType(self._getString(0))

    def setType(self, value):
        self._setString(0, value.value)

    def _initialize(self):
        super(ButtonModel, self)._initialize()
        self._addStringProperty('type')
