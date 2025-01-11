# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/personal_missions/tooltips/personal_missions_last_operation_tooltip_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.personal_missions.tooltips.pm3_last_operation_tooltip_rewards_model import Pm3LastOperationTooltipRewardsModel

class LastMissionStatus(Enum):
    DEVELOPMENT = 'development'
    ACTIVE = 'active'
    COMPLETED = 'completed'


class PersonalMissionsLastOperationTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(PersonalMissionsLastOperationTooltipModel, self).__init__(properties=properties, commands=commands)

    def getMissionStatus(self):
        return LastMissionStatus(self._getString(0))

    def setMissionStatus(self, value):
        self._setString(0, value.value)

    def getName(self):
        return self._getString(1)

    def setName(self, value):
        self._setString(1, value)

    def getCompleted(self):
        return self._getNumber(2)

    def setCompleted(self, value):
        self._setNumber(2, value)

    def getAll(self):
        return self._getNumber(3)

    def setAll(self, value):
        self._setNumber(3, value)

    def getRewards(self):
        return self._getArray(4)

    def setRewards(self, value):
        self._setArray(4, value)

    @staticmethod
    def getRewardsType():
        return Pm3LastOperationTooltipRewardsModel

    def _initialize(self):
        super(PersonalMissionsLastOperationTooltipModel, self)._initialize()
        self._addStringProperty('missionStatus')
        self._addStringProperty('name', '')
        self._addNumberProperty('completed', 0)
        self._addNumberProperty('all', 0)
        self._addArrayProperty('rewards', Array())
