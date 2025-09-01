# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/personal_missions_30/select_operation_model.py
from gui.impl.gen.view_models.views.lobby.personal_missions_30.common.enums import OperationState
from frameworks.wulf import ViewModel

class SelectOperationModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(SelectOperationModel, self).__init__(properties=properties, commands=commands)

    def getCompleted(self):
        return self._getBool(0)

    def setCompleted(self, value):
        self._setBool(0, value)

    def getState(self):
        return OperationState(self._getString(1))

    def setState(self, value):
        self._setString(1, value.value)

    def getOperationId(self):
        return self._getNumber(2)

    def setOperationId(self, value):
        self._setNumber(2, value)

    def getOperationName(self):
        return self._getString(3)

    def setOperationName(self, value):
        self._setString(3, value)

    def getOperationIcon(self):
        return self._getString(4)

    def setOperationIcon(self, value):
        self._setString(4, value)

    def getActive(self):
        return self._getBool(5)

    def setActive(self, value):
        self._setBool(5, value)

    def _initialize(self):
        super(SelectOperationModel, self)._initialize()
        self._addBoolProperty('completed', False)
        self._addStringProperty('state')
        self._addNumberProperty('operationId', 0)
        self._addStringProperty('operationName', '')
        self._addStringProperty('operationIcon', '')
        self._addBoolProperty('active', False)
