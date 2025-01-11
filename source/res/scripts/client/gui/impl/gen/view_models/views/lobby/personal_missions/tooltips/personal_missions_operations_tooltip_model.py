# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/personal_missions/tooltips/personal_missions_operations_tooltip_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.personal_missions.tooltips.pm3_operations_tooltip_branches_model import Pm3OperationsTooltipBranchesModel
from gui.impl.gen.view_models.views.lobby.personal_missions.tooltips.pm3_operations_tooltip_rewards_model import Pm3OperationsTooltipRewardsModel

class MissionStatus(Enum):
    AVAILABLE = 'available'
    ACTIVE = 'active'
    DISABLED = 'disabled'
    COMPLETED = 'completed'
    COMPLETEDPERFECTLY = 'completedPerfectly'
    DISABLEDLEVEL = 'disabledLevel'


class PersonalMissionsOperationsTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=0):
        super(PersonalMissionsOperationsTooltipModel, self).__init__(properties=properties, commands=commands)

    def getMissionStatus(self):
        return MissionStatus(self._getString(0))

    def setMissionStatus(self, value):
        self._setString(0, value.value)

    def getOperationID(self):
        return self._getNumber(1)

    def setOperationID(self, value):
        self._setNumber(1, value)

    def getName(self):
        return self._getString(2)

    def setName(self, value):
        self._setString(2, value)

    def getFrom(self):
        return self._getString(3)

    def setFrom(self, value):
        self._setString(3, value)

    def getPrevOperationName(self):
        return self._getString(4)

    def setPrevOperationName(self, value):
        self._setString(4, value)

    def getTo(self):
        return self._getString(5)

    def setTo(self, value):
        self._setString(5, value)

    def getBranches(self):
        return self._getArray(6)

    def setBranches(self, value):
        self._setArray(6, value)

    @staticmethod
    def getBranchesType():
        return Pm3OperationsTooltipBranchesModel

    def getRewards(self):
        return self._getArray(7)

    def setRewards(self, value):
        self._setArray(7, value)

    @staticmethod
    def getRewardsType():
        return Pm3OperationsTooltipRewardsModel

    def _initialize(self):
        super(PersonalMissionsOperationsTooltipModel, self)._initialize()
        self._addStringProperty('missionStatus')
        self._addNumberProperty('operationID', 0)
        self._addStringProperty('name', '')
        self._addStringProperty('from', '')
        self._addStringProperty('prevOperationName', '')
        self._addStringProperty('to', '')
        self._addArrayProperty('branches', Array())
        self._addArrayProperty('rewards', Array())
