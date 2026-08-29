# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/personal_missions_30/tooltips/umg_tooltip_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.personal_missions_30.tooltips.mission_condition_model import MissionConditionModel
from gui.impl.gen.view_models.views.lobby.personal_missions_30.tooltips.umg_reward_model import UmgRewardModel
from gui.impl.gen.view_models.views.lobby.user_missions.widget.personal_mission_model import PersonalMissionModel

class UmgTooltipModel(PersonalMissionModel):
    __slots__ = ()

    def __init__(self, properties=16, commands=0):
        super(UmgTooltipModel, self).__init__(properties=properties, commands=commands)

    def getOperationId(self):
        return self._getNumber(10)

    def setOperationId(self, value):
        self._setNumber(10, value)

    def getAndConditions(self):
        return self._getArray(11)

    def setAndConditions(self, value):
        self._setArray(11, value)

    @staticmethod
    def getAndConditionsType():
        return MissionConditionModel

    def getOrConditions(self):
        return self._getArray(12)

    def setOrConditions(self, value):
        self._setArray(12, value)

    @staticmethod
    def getOrConditionsType():
        return MissionConditionModel

    def getRewards(self):
        return self._getArray(13)

    def setRewards(self, value):
        self._setArray(13, value)

    @staticmethod
    def getRewardsType():
        return UmgRewardModel

    def getTotalVehiclesForQuest(self):
        return self._getNumber(14)

    def setTotalVehiclesForQuest(self, value):
        self._setNumber(14, value)

    def getCompletedInVehicles(self):
        return self._getNumber(15)

    def setCompletedInVehicles(self, value):
        self._setNumber(15, value)

    def _initialize(self):
        super(UmgTooltipModel, self)._initialize()
        self._addNumberProperty('operationId', 0)
        self._addArrayProperty('andConditions', Array())
        self._addArrayProperty('orConditions', Array())
        self._addArrayProperty('rewards', Array())
        self._addNumberProperty('totalVehiclesForQuest', 1)
        self._addNumberProperty('completedInVehicles', 0)
