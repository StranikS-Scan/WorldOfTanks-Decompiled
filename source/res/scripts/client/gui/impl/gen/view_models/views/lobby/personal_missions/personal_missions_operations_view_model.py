# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/personal_missions/personal_missions_operations_view_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.personal_missions.pm3_operation_model import Pm3OperationModel

class RewardsStatus(Enum):
    AVAILABLE = 'available'
    DISABLE = 'disable'
    HIDDEN = 'hidden'


class PersonalMissionsOperationsViewModel(ViewModel):
    __slots__ = ('onClose', 'onOpenOperation', 'onTakeRewards', 'onInfo')

    def __init__(self, properties=3, commands=4):
        super(PersonalMissionsOperationsViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def lastOperation(self):
        return self._getViewModel(0)

    @staticmethod
    def getLastOperationType():
        return Pm3OperationModel

    def getRewardsStatus(self):
        return RewardsStatus(self._getString(1))

    def setRewardsStatus(self, value):
        self._setString(1, value.value)

    def getOperations(self):
        return self._getArray(2)

    def setOperations(self, value):
        self._setArray(2, value)

    @staticmethod
    def getOperationsType():
        return Pm3OperationModel

    def _initialize(self):
        super(PersonalMissionsOperationsViewModel, self)._initialize()
        self._addViewModelProperty('lastOperation', Pm3OperationModel())
        self._addStringProperty('rewardsStatus')
        self._addArrayProperty('operations', Array())
        self.onClose = self._addCommand('onClose')
        self.onOpenOperation = self._addCommand('onOpenOperation')
        self.onTakeRewards = self._addCommand('onTakeRewards')
        self.onInfo = self._addCommand('onInfo')
